/* Fixed, offline rendering. Every visual is derived here from snapshot data;
   polling never invokes a model or a task tracker. */
"use strict";

(() => {
  const byId = id => document.getElementById(id);
  const text = (id, value) => {
    const node = byId(id), content = String(value ?? "");
    if (node.textContent !== content) node.textContent = content;
  };
  const counted = value => Number.isFinite(value);
  const compact = value => counted(value)
    ? new Intl.NumberFormat("en", {notation: "compact", maximumFractionDigits: 1}).format(value) : "—";
  const exact = value => counted(value) ? new Intl.NumberFormat("en").format(value) : "unknown";
  const plural = (count, word) => `${count} ${word}${count === 1 ? "" : "s"}`;
  const TASK_GROUPS = [["in-progress", "In progress"], ["todo", "Up next"], ["complete", "Done"]];
  const STATUS = { // label, tone, glyph: state is never carried by color alone
    running: ["Running", "active", "●"], waiting: ["Waiting", "waiting", "◐"], complete: ["Done", "done", "✓"],
    failed: ["Failed", "failed", "✕"], unknown: ["Unknown", "quiet", "?"],
    "in-progress": ["In progress", "active", "●"], todo: ["Up next", "quiet", "○"],
    done: ["Done", "done", "✓"], active: ["Active", "active", "●"],
  };
  const KINDS = {feedback: "Comment", steer: "Direction", question: "Question"};
  const form = byId("feedback-form"), feedbackText = byId("feedback-text");
  const kind = byId("feedback-kind"), target = byId("feedback-target");
  const draftKey = `progress-dashboard-draft:${location.pathname}`;
  let current = null, etag = null, timer = null, inFlight = false, failures = 0;
  let sending = false, pendingSubmission = null, targetSignature = "";

  function el(tag, className, content) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined && content !== null) node.textContent = content;
    return node;
  }

  function age(value) {
    const elapsed = Date.now() - new Date(value || NaN).getTime();
    if (!Number.isFinite(elapsed)) return "time unknown";
    if (elapsed < 60000) return "just now";
    if (elapsed < 3600000) return `${Math.floor(elapsed / 60000)}m ago`;
    if (elapsed < 86400000) return `${Math.floor(elapsed / 3600000)}h ago`;
    return `${Math.floor(elapsed / 86400000)}d ago`;
  }

  function when(value) {
    const date = new Date(value || NaN);
    const node = el("time", null, age(value));
    if (Number.isFinite(date.getTime())) {
      node.dateTime = date.toISOString();
      node.title = date.toLocaleString();
    }
    node.dataset.relative = value || "";
    return node;
  }

  function badge(status, text) {
    const [label, tone, glyph] = STATUS[status] || [status || "Unknown", "quiet", "·"];
    const node = el("span", `badge ${tone}`);
    const mark = el("span", "glyph", glyph);
    mark.setAttribute("aria-hidden", "true");
    node.append(mark, text || label);
    return node;
  }

  /* Keyed rows: unchanged rows keep their node, so focus, text selection and
     open disclosures survive a background refresh. */
  function sync(container, items, build, update) {
    const existing = new Map([...container.children].map(node => [node.dataset.key, node]));
    items.forEach(([key, value], index) => {
      const signature = JSON.stringify(value);
      let node = existing.get(key);
      existing.delete(key);
      if (node && update && node.dataset.signature !== signature) {
        update(node, value);
        node.dataset.signature = signature;
      } else if (!node || node.dataset.signature !== signature) {
        const fresh = build(value);
        if (update) update(fresh, value);
        fresh.dataset.key = key;
        fresh.dataset.signature = signature;
        if (node?.open) fresh.open = true;
        if (node) node.replaceWith(fresh); else container.append(fresh);
        node = fresh;
      }
      if (container.children[index] !== node) container.insertBefore(node, container.children[index]);
    });
    for (const node of existing.values()) node.remove();
  }

  function commentButton(id, label) {
    const button = el("button", "link-button", "Comment");
    button.type = "button";
    button.dataset.focusKey = `comment:${id}`;
    button.setAttribute("aria-label", `Comment on ${label}`);
    button.addEventListener("click", () => {
      if ([...target.options].some(option => option.value === id)) target.value = id;
      saveDraft();
      byId("feedback").scrollIntoView({block: "nearest"});
      feedbackText.focus();
    });
    return button;
  }

  function externalLink(value, label) {
    try {
      const url = new URL(value);
      if (!["http:", "https:"].includes(url.protocol) || url.username || url.password) return null;
      const link = el("a", null, url.host + url.pathname);
      link.href = url.href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.dataset.focusKey = `link:${label}`;
      link.setAttribute("aria-label", `${label}: ${url.href} (opens in a new tab)`);
      return link;
    } catch { return null; }
  }

  function renderTasks(tasks, agents) {
    const container = byId("task-groups");
    if (!tasks.length) {
      container.replaceChildren(el("p", "empty", "No tasks recorded yet."));
      return;
    }
    container.querySelector(":scope > .empty")?.remove();
    const build = task => {
      const row = el("article", "task");
      row.dataset.taskId = task.id;
      const head = el("div", "task-head");
      const mark = el("span", `glyph ${STATUS[task.status][1]}`, STATUS[task.status][2]);
      mark.setAttribute("aria-hidden", "true");
      const title = el("h4");
      title.append(mark, task.title);
      head.append(title, el("code", null, task.id));
      for (const agent of task.agents) {
        const chip = el("a", "chip", agent.name);
        chip.href = "#agents";
        chip.title = `${agent.name}: ${STATUS[agent.status]?.[0] || agent.status}`;
        chip.dataset.focusKey = `chip:${task.id}:${agent.id}`;
        chip.dataset.tone = STATUS[agent.status]?.[1] || "quiet";
        chip.addEventListener("click", () => {
          const row = [...byId("agent-list").children].find(node => node.dataset.key === agent.id);
          if (row) row.open = true;
        });
        head.append(chip);
      }
      head.append(commentButton(task.id, task.title));
      row.append(head);
      if (task.detail) row.append(el("p", null, task.detail));
      if (task.evidence) {
        const evidence = el("p", "evidence");
        evidence.append(el("span", "label", "Evidence"), task.evidence);
        row.append(evidence);
      }
      return row;
    };
    const groups = TASK_GROUPS.map(([status, label]) => [status, {
      label, rows: tasks.filter(task => task.status === status).map(task => ({...task,
        agents: agents.filter(agent => agent.task === task.id).map(({id, name, status}) => ({id, name: name || id, status}))})),
    }]).filter(([, group]) => group.rows.length);
    sync(container, groups.map(([status, group]) => [status, {status, label: group.label, count: group.rows.length}]), group => {
      // Finished work stays one click away instead of pushing live work down.
      const wrap = el(group.status === "complete" ? "details" : "div", "task-group");
      const heading = el(group.status === "complete" ? "summary" : "h3", "group-heading", group.label);
      heading.append(el("span", "count", group.count));
      wrap.append(heading, el("div", "task-rows"));
      return wrap;
    });
    for (const [status, group] of groups) {
      const rows = [...container.children].find(node => node.dataset.key === status).querySelector(".task-rows");
      sync(rows, group.rows.map(task => [task.id, task]), build);
    }
  }

  function usageOf(row) {
    if (!row || row.status !== "measured" || !counted(row.total_tokens)) return null;
    const cached = row.cached_input_tokens || 0;
    return {total: row.total_tokens, cached, fresh: Math.max(0, row.total_tokens - cached),
            input: row.input_tokens, output: row.output_tokens};
  }

  function fact(list, label, value) {
    if (!value) return;
    const item = el("div");
    const body = el("dd");
    body.append(value);
    item.append(el("dt", null, label), body);
    list.append(item);
  }

  /* Usage ticks every few seconds for a running agent. Its row is patched in
     place so an open report keeps its focus, selection and scroll position. */
  function buildAgent(agent) {
    const row = el("details", "agent");
    row.dataset.agentId = agent.id;
    const summary = el("summary");
    summary.dataset.focusKey = `agent:${agent.id}`;
    const name = el("span", "agent-name");
    name.append(el("strong"), el("span", "caption"));
    const tokens = el("span", "agent-tokens");
    const bar = el("span", "bar");
    bar.setAttribute("role", "img");
    bar.append(el("span", "fresh"), el("span", "cached"));
    tokens.append(el("span", "number"), bar);
    summary.append(name, el("span", "agent-status"), tokens, el("span", "agent-updated caption"));
    const body = el("div", "agent-body");
    const facts = el("dl", "facts usage");
    for (const label of ["Tokens", "Runtime"]) {
      const item = el("div");
      item.append(el("dt", null, label), el("dd"));
      facts.append(item);
    }
    body.append(el("div", "agent-report"), facts);
    if (agent.commentable) body.append(commentButton(agent.id, agent.name));
    row.append(summary, body);
    return row;
  }

  function updateAgent(row, agent) {
    const set = (selector, value) => {
      const node = row.querySelector(selector);
      if (node.textContent !== value) node.textContent = value;
    };
    set(".agent-name strong", agent.name);
    set(".agent-name .caption", [agent.role, agent.taskTitle].filter(Boolean).join(" · "));
    const status = row.querySelector(".agent-status");
    if (status.dataset.status !== (agent.status || "")) {
      status.replaceChildren(...(agent.status ? [badge(agent.status)] : []));
      status.dataset.status = agent.status || "";
    }
    const updated = row.querySelector(".agent-updated");
    if (updated.dataset.at !== (agent.updated_at || "")) {
      updated.replaceChildren(...(agent.updated_at ? [when(agent.updated_at)] : []));
      updated.dataset.at = agent.updated_at || "";
    }
    const usage = agent.usage, tokens = row.querySelector(".agent-tokens"), bar = tokens.querySelector(".bar");
    set(".agent-tokens .number", usage ? compact(usage.total) : "Not measured");
    tokens.classList.toggle("unmeasured", !usage);
    bar.hidden = !usage;
    if (usage) {
      for (const [tone, amount] of [["fresh", usage.fresh], ["cached", usage.cached]]) {
        const segment = bar.querySelector(`.${tone}`);
        segment.hidden = !amount;
        segment.style.width = `${amount / agent.scale * 100}%`;
      }
      bar.setAttribute("aria-label", `${exact(usage.total)} tokens, ${exact(usage.cached)} of them cached input`);
      tokens.title = `${exact(usage.fresh)} new input and output · ${exact(usage.cached)} cached input`;
    } else {
      tokens.removeAttribute("title");
    }
    const [tokenFact, runtimeFact] = row.querySelectorAll(".usage > div");
    const runtime = [agent.model, agent.provider, agent.thread && `session ${agent.thread.slice(0, 8)}`].filter(Boolean).join(" · ");
    set(".usage > div:nth-child(1) dd", usage
      ? `${exact(usage.input - usage.cached)} new input · ${exact(usage.cached)} cached · ${exact(usage.output)} output` : agent.unmeasured);
    set(".usage > div:nth-child(2) dd", runtime);
    tokenFact.hidden = false;
    runtimeFact.hidden = !runtime;
    // The authored report changes only at checkpoints; rebuild it only then.
    const report = row.querySelector(".agent-report");
    const signature = JSON.stringify([agent.summary, agent.activity, agent.branch, agent.worktree, agent.pr_url]);
    if (report.dataset.signature === signature) return;
    report.dataset.signature = signature;
    report.replaceChildren();
    if (agent.summary) report.append(el("p", null, agent.summary));
    if (agent.activity?.length) {
      const list = el("ul", "actions");
      for (const item of agent.activity) list.append(el("li", null, item));
      report.append(el("h4", "label", "Recent actions"), list);
    }
    const facts = el("dl", "facts");
    fact(facts, "Branch", agent.branch && el("code", null, agent.branch));
    fact(facts, "Worktree", agent.worktree && el("code", null, agent.worktree));
    fact(facts, "Pull request", agent.pr_url && (externalLink(agent.pr_url, `Pull request for ${agent.name}`) || agent.pr_url));
    if (facts.children.length) report.append(facts);
  }

  function renderAgents(state, telemetry) {
    const measured = new Map((telemetry.agents || []).map(row => [row.id, row]));
    const tasks = new Map(state.tasks.map(task => [task.id, task.title]));
    const runtime = row => ({usage: usageOf(row), provider: row?.provider || "", thread: row?.thread_id || "",
                             model: row?.model || "",
                             unmeasured: !row || row.reason === "not-attached" ? "Not measured: no usage source attached"
                               : `Not measured${row.reason ? `: ${row.reason.replaceAll("-", " ")}` : ""}`});
    const rows = [{id: state.actor, name: "Parent session", role: "coordinator", ...runtime(measured.get(state.actor))}];
    for (const agent of state.agents) {
      const usage = runtime(measured.get(agent.id));
      rows.push({...agent, name: agent.name || agent.id, taskTitle: tasks.get(agent.task) || agent.task, commentable: true,
                 ...usage, model: agent.model || usage.model, thread: agent.thread_id || usage.thread});
    }
    const known = new Set(rows.map(row => row.id));
    for (const row of telemetry.agents || []) {
      if (!known.has(row.id)) rows.push({id: row.id, name: row.id, role: "attached session", ...runtime(row)});
    }
    const scale = Math.max(1, ...rows.map(row => row.usage?.total || 0));
    sync(byId("agent-list"), rows.map(row => [row.id, {...row, scale}]), buildAgent, updateAgent);
    byId("token-legend").hidden = !rows.some(row => row.usage);
    const warning = byId("usage-warning");
    warning.hidden = !telemetry.error;
    text("usage-warning", telemetry.error || "");
  }

  function numeric(value) { return typeof value === "number"; }

  function buildPanel(panel) {
    const figure = el("figure", "panel");
    figure.append(el("figcaption", null, panel.title));
    const rows = panel.rows || [];
    if (panel.kind === "stats") {
      const grid = el("dl", "tiles");
      for (const [label, value, note] of rows) {
        const tile = el("div");
        tile.append(el("dt", null, label), el("dd", null, numeric(value) ? compact(value) : value));
        if (note !== undefined) tile.append(el("dd", "caption", note));
        grid.append(tile);
      }
      figure.append(grid);
    } else if (panel.kind === "bars") {
      const scale = Math.max(...rows.map(row => row[1]), 0) || 1;
      const list = el("dl", "bars");
      for (const [label, value, note] of rows) {
        const row = el("div");
        const track = el("span", "bar");
        const fill = el("span", "fresh");
        fill.style.width = `${value / scale * 100}%`;
        track.append(fill);
        const amount = el("dd");
        amount.append(track, el("span", "number", exact(value)), note === undefined ? "" : el("span", "caption", note));
        row.append(el("dt", null, label), amount);
        row.title = `${label}: ${exact(value)}`;
        list.append(row);
      }
      figure.append(list);
    } else if (panel.kind === "steps") {
      const list = el("ol", "steps");
      for (const [label, state, note] of rows) {
        const tone = {done: "done", active: "active", todo: "quiet", failed: "failed"}[state];
        const item = el("li", tone);
        const mark = el("span", `glyph ${tone}`, (STATUS[state] || STATUS.todo)[2]);
        mark.setAttribute("aria-hidden", "true");
        item.append(mark, el("span", "step-label", label), el("span", "sr-only", ` (${state})`));
        if (note !== undefined) item.append(el("span", "caption", note));
        list.append(item);
      }
      figure.append(list);
    } else {
      const scroll = el("div", "scroll");
      const table = el("table");
      rows.forEach((cells, index) => {
        const line = el("tr");
        for (const cell of cells) {
          const node = el(index ? "td" : "th", numeric(cell) ? "number" : null, numeric(cell) ? exact(cell) : cell);
          if (!index) node.scope = "col";
          line.append(node);
        }
        (index ? table.tBodies[0] || table.createTBody() : table.createTHead()).append(line);
      });
      scroll.append(table);
      figure.append(scroll);
    }
    if (panel.note) figure.append(el("p", "caption", panel.note));
    return figure;
  }

  function buildArtifact(artifact) {
    const figure = el("figure", "panel artifact");
    const url = `artifacts/${artifact.path.split("/").map(encodeURIComponent).join("/")}`;
    const label = artifact.label || artifact.path;
    const caption = el("figcaption", null, label);
    const link = el("a", null, "Download");
    link.href = url;
    link.download = artifact.path.split("/").pop();
    link.dataset.focusKey = `artifact:${artifact.path}`;
    link.setAttribute("aria-label", `Download ${label}`);
    caption.append(link);
    figure.append(caption);
    if (/\.(png|jpe?g|gif|webp|svg)$/i.test(artifact.path)) {
      const image = el("img");
      image.src = url;
      image.alt = label;
      image.loading = "lazy";
      figure.append(image);
    }
    return figure;
  }

  function renderActivity(log) {
    const entries = [...log].reverse().map((entry, index) => [`${entry.at}:${log.length - index}`, entry]);
    sync(byId("activity-list"), entries, entry => {
      const item = el("li");
      item.append(when(entry.at), el("span", null, entry.text));
      return item;
    });
  }

  // A small readable Markdown subset; text never enters an HTML parser.
  function renderProse(destination, content) {
    destination.replaceChildren();
    let list = null;
    for (const line of content.split("\n")) {
      const heading = /^(#{1,4})\s+(.*)$/.exec(line);
      const bullet = /^\s*[-*]\s+(.*)$/.exec(line);
      if (bullet) {
        if (!list) destination.append(list = el("ul"));
        list.append(el("li", null, bullet[1]));
        continue;
      }
      list = null;
      if (heading) destination.append(el(heading[1].length < 2 ? "h3" : "h4", null, heading[2]));
      else if (line.trim()) destination.append(el("p", null, line));
    }
  }

  function renderFeedback(feedback, enabled) {
    const pending = feedback.filter(item => item.status === "pending").length;
    text("nav-feedback", pending);
    byId("nav-feedback").hidden = !pending;
    text("feedback-total", !enabled ? "Off" : feedback.length ? pending ? `${pending} pending` : "All read" : "—");
    text("feedback-caption", !enabled ? "Disabled for this workspace"
      : feedback.length ? `${feedback.length - pending} of ${feedback.length} read by the session` : "Nothing sent");
    sync(byId("feedback-history"), [...feedback].reverse().map(item => [String(item.id), item]), item => {
      const entry = el("article", "message");
      const meta = el("p", "meta");
      meta.append(el("strong", null, KINDS[item.kind] || "Comment"));
      if (item.target && item.target !== "loop") meta.append(el("code", null, item.target));
      meta.append(when(item.created_at), item.status === "pending" ? badge("waiting", "Queued") : badge("done", "Read"));
      entry.append(meta, el("p", null, item.text));
      if (item.response) {
        const reply = el("p", "reply");
        reply.append(el("span", "label", "Reply"), el("span", null, item.response));
        entry.append(reply);
      }
      return entry;
    });
  }

  function updateTargets(state) {
    const options = [{id: "loop", label: "Whole session"},
      ...state.tasks.map(task => ({id: task.id, label: `Task · ${task.title}`})),
      ...state.agents.map(agent => ({id: agent.id, label: `Agent · ${agent.name || agent.id}`}))];
    const signature = JSON.stringify(options);
    // A background update must not replace an open dropdown.
    if (signature === targetSignature || document.activeElement === target) return;
    const selected = target.value;
    target.replaceChildren(...options.map(option => {
      const node = el("option", null, option.label);
      node.value = option.id;
      return node;
    }));
    if (!options.some(option => option.id === selected)) {
      const removed = el("option", null, `${selected} · no longer listed`);
      removed.value = selected;
      target.append(removed);
    }
    target.value = selected;
    targetSignature = signature;
  }

  function section(id, count) {
    byId(id).hidden = !count;
    document.querySelector(`nav [data-section="${id}"]`).hidden = !count;
    const badge = byId(`nav-${id}`);
    if (badge) text(badge.id, count || "");
  }

  function render(data) {
    current = data;
    const state = data.state, telemetry = data.telemetry || {};
    const tasks = state.tasks, agents = state.agents;
    const focusKey = document.activeElement?.dataset.focusKey;
    document.title = `${state.title} · Progress`;
    text("title", state.title);
    text("top-title", state.title);
    text("summary", state.summary || "Waiting for the first checkpoint.");
    text("outcome", state.outcome ? `Goal: ${state.outcome}` : "");
    byId("outcome").hidden = !state.outcome;
    text("phase", state.phase);
    byId("phase").className = `badge ${state.phase === "complete" ? "done" : "active"}`;

    const tally = Object.fromEntries(TASK_GROUPS.map(([status]) => [status, tasks.filter(task => task.status === status).length]));
    text("task-total", tasks.length ? `${tally.complete}/${tasks.length}` : "—");
    text("task-caption", tasks.length
      ? [tally["in-progress"] && `${tally["in-progress"]} in progress`, tally.todo && `${tally.todo} up next`].filter(Boolean).join(" · ") || "All done"
      : "No tasks recorded");
    const meter = byId("task-meter");
    meter.replaceChildren(...[["done", tally.complete], ["active", tally["in-progress"]], ["quiet", tally.todo]]
      .filter(([, count]) => count).map(([tone, count]) => {
        const segment = el("span", tone);
        segment.style.flexGrow = count;
        return segment;
      }));
    meter.setAttribute("aria-label", tasks.length
      ? `${tally.complete} done, ${tally["in-progress"]} in progress, ${tally.todo} up next` : "No tasks recorded");
    text("nav-work", tasks.length || "");

    const by = status => agents.filter(agent => agent.status === status).length;
    text("agent-total", !agents.length ? "—" : by("running") ? `${by("running")} running` : agents.length);
    text("agent-caption", agents.length ? ["waiting", "complete", "failed", "unknown"].filter(by)
      .map(status => `${by(status)} ${STATUS[status][0].toLowerCase()}`).join(" · ") || "All running" : "None reported");
    text("nav-agents", agents.length || "");

    const totals = counted(telemetry.totals?.total_tokens) ? telemetry.totals : null, coverage = telemetry.coverage || {};
    text("token-total", totals ? compact(totals.total_tokens) : "—");
    text("token-caption", !totals ? telemetry.error ? "Usage unavailable" : "No usage measured" : [
      totals.input_tokens ? `${Math.round((totals.cached_input_tokens || 0) / totals.input_tokens * 100)}% of input cached` : "",
      `${compact(totals.output_tokens)} output`].filter(Boolean).join(" · "));
    text("token-coverage", totals && coverage.measured < coverage.expected
      ? `${coverage.measured} of ${plural(coverage.expected, "session")} measured` : "");

    renderTasks(tasks, agents);
    renderAgents(state, telemetry);
    sync(byId("finding-list"), state.findings.map((finding, index) => [`${index}:${finding}`, finding]), finding => el("li", null, finding));
    section("findings", state.findings.length);
    sync(byId("panel-list"), state.panels.map(panel => [panel.id, panel]), buildPanel);
    sync(byId("artifact-list"), state.artifacts.map(artifact => [artifact.path, artifact]), buildArtifact);
    section("visuals", state.panels.length + state.artifacts.length);
    renderActivity(state.log);
    section("activity", state.log.length);
    byId("handover").hidden = !data.handover;
    if (data.handover && byId("handover-content").dataset.signature !== data.handover) {
      renderProse(byId("handover-content"), data.handover);
      byId("handover-content").dataset.signature = data.handover;
    }
    renderFeedback(data.feedback || [], data.feedback_enabled !== false);
    updateTargets(state);
    for (const field of form.elements) field.disabled = data.feedback_enabled === false;
    updateSubmitState();
    text("footer-state", `${data.workspace} · checkpoint ${state.revision}`);
    // A rebuilt row must not strand a keyboard user at the document root.
    if (focusKey && document.activeElement?.dataset.focusKey !== focusKey) {
      [...document.querySelectorAll("[data-focus-key]")].find(node => node.dataset.focusKey === focusKey)?.focus({preventScroll: true});
    }
    updateFreshness();
    updateNavigation();
  }

  function updateFreshness() {
    if (!current) return;
    const updated = current.state.updated_at;
    const elapsed = Date.now() - new Date(updated).getTime();
    // Reported progress is an observation, not proof the session is running now.
    const stale = current.state.phase !== "complete" && current.state.revision > 0 && !(elapsed <= 300000);
    text("checkpoint-time", current.state.revision ? `Updated ${age(updated)}${stale ? " · may be stale" : ""}` : "No checkpoint yet");
    byId("checkpoint-time").classList.toggle("stale", stale);
    for (const node of document.querySelectorAll("time[data-relative]")) node.textContent = age(node.dataset.relative);
    if (!failures) text("connection-text", document.hidden ? "Paused" : "Live");
  }

  function updateSubmitState() {
    byId("submit-feedback").disabled = !current || current.feedback_enabled === false || sending || !feedbackText.value.trim();
  }

  function saveDraft() {
    updateSubmitState();
    try {
      sessionStorage.setItem(draftKey, JSON.stringify({text: feedbackText.value, kind: kind.value, target: target.value, pending: pendingSubmission}));
      text("draft-state", feedbackText.value ? "Draft kept in this tab" : "");
    } catch { text("draft-state", ""); }
  }

  function restoreDraft() {
    try {
      const draft = JSON.parse(sessionStorage.getItem(draftKey) || "null");
      if (!draft) return;
      feedbackText.value = draft.text || "";
      if (draft.kind in KINDS) kind.value = draft.kind;
      if (draft.target && draft.target !== "loop") {
        const option = el("option", null, draft.target);
        option.value = draft.target;
        target.append(option);
        target.value = draft.target;
      }
      pendingSubmission = draft.pending || null;
      text("draft-state", feedbackText.value ? "Draft restored" : "");
    } catch { /* Storage is optional; an unavailable store never blocks input. */ }
  }

  function setResult(message, error = false) {
    byId("feedback-result").classList.toggle("error", error);
    text("feedback-result", message);
  }

  async function submitFeedback(event) {
    event.preventDefault();
    if (sending || !current || current.feedback_enabled === false) return;
    const message = feedbackText.value.trim();
    if (!message) { feedbackText.focus(); return; }
    const content = {kind: kind.value, target: target.value, text: message};
    // The same content retried after a lost response reuses its idempotency key.
    if (!pendingSubmission || JSON.stringify(pendingSubmission.content) !== JSON.stringify(content)) {
      pendingSubmission = {client_id: clientId(), content, revision: current.state.revision};
    }
    const submission = pendingSubmission;
    saveDraft();
    sending = true;
    updateSubmitState();
    text("submit-feedback", "Sending…");
    form.setAttribute("aria-busy", "true");
    setResult("");
    try {
      const response = await fetch("api/feedback", {method: "POST",
        headers: {"Content-Type": "application/json", "X-Loop-Feedback": "1"},
        body: JSON.stringify({...content, client_id: submission.client_id, revision: submission.revision}),
        signal: AbortSignal.timeout(12000)});
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || `Feedback could not be saved (${response.status}).`);
      if (!body.feedback?.id) throw new Error("The server did not confirm a saved feedback record.");
      // A slow save must not erase a new draft typed while it was in flight.
      if (feedbackText.value.trim() === content.text && kind.value === content.kind && target.value === content.target) {
        feedbackText.value = "";
        pendingSubmission = null;
      }
      saveDraft();
      setResult("Saved. The session reads it at its next checkpoint.");
      await poll(true);
    } catch (error) {
      setResult(error.name === "TimeoutError" ? "Confirmation timed out. Your draft is kept; sending again will not duplicate it."
        : `${error.message || "Could not confirm feedback."} Your draft is kept.`, true);
    } finally {
      sending = false;
      text("submit-feedback", "Send");
      form.setAttribute("aria-busy", "false");
      updateSubmitState();
    }
  }

  function clientId() {
    // getRandomValues also works on private-network HTTP origins, where
    // randomUUID is unavailable because the origin is not a secure context.
    if (typeof crypto.randomUUID === "function") return crypto.randomUUID();
    const bytes = crypto.getRandomValues(new Uint8Array(16));
    bytes[6] = (bytes[6] & 15) | 64;
    bytes[8] = (bytes[8] & 63) | 128;
    const hex = [...bytes].map(byte => byte.toString(16).padStart(2, "0")).join("");
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  }

  function schedule() {
    clearTimeout(timer);
    if (!document.hidden) timer = setTimeout(() => poll(), Math.min(30000, 3000 * 2 ** Math.min(failures, 4)));
  }

  async function poll(force = false) {
    if (inFlight || (document.hidden && !force)) return;
    inFlight = true;
    byId("refresh").disabled = true;
    try {
      const response = await fetch("api/state", {headers: etag && !force ? {"If-None-Match": etag} : {},
        cache: "no-store", signal: AbortSignal.timeout(10000)});
      if (!response.ok && response.status !== 304) throw new Error(`Progress could not be loaded (${response.status}).`);
      if (response.status !== 304) {
        const data = await response.json();
        if (!Array.isArray(data.state?.tasks) || !Array.isArray(data.state.panels)) throw new Error("The server returned an invalid snapshot.");
        etag = response.headers.get("ETag");
        render(data);
      }
      failures = 0;
      document.querySelector(".connection").dataset.state = "connected";
      byId("load-error").hidden = true;
      updateFreshness();
    } catch (error) {
      failures += 1;
      document.querySelector(".connection").dataset.state = "offline";
      text("connection-text", "Disconnected");
      text("load-error", `${error.message || "Connection unavailable."} ${current ? "Showing the last snapshot. " : ""}Retrying automatically; your draft is kept.`);
      byId("load-error").hidden = false;
    } finally {
      inFlight = false;
      byId("refresh").disabled = false;
      schedule();
    }
  }

  function updateNavigation() {
    const line = document.querySelector(".topbar").getBoundingClientRect().bottom + 56;
    let active = "work";
    // Feedback is a section only once the rail stacks under the content.
    const stacked = matchMedia("(max-width: 1020px)").matches;
    const sections = [...document.querySelectorAll(`.content > section:not([hidden])${stacked ? ", #feedback" : ""}`)];
    const atEnd = innerHeight + scrollY >= document.documentElement.scrollHeight - 2 && scrollY > 0;
    for (const node of sections) {
      if (atEnd || node.getBoundingClientRect().top <= line) active = node.id;
    }
    const nav = document.querySelector("nav");
    for (const link of nav.querySelectorAll("a")) {
      const here = link.hash === `#${active}`;
      // On narrow screens the current section's link stays within the scrolling strip.
      if (here && link.getAttribute("aria-current") !== "true") {
        nav.scrollTo({left: link.offsetLeft - nav.offsetLeft - (nav.clientWidth - link.offsetWidth) / 2});
      }
      link.setAttribute("aria-current", String(here));
    }
  }

  restoreDraft();
  form.addEventListener("submit", submitFeedback);
  form.addEventListener("input", () => { pendingSubmission = null; saveDraft(); });
  target.addEventListener("blur", () => { if (current) updateTargets(current.state); });
  byId("refresh").addEventListener("click", () => poll(true));
  document.addEventListener("visibilitychange", () => {
    clearTimeout(timer);
    if (document.hidden) text("connection-text", "Paused"); else poll(true);
  });
  document.addEventListener("keydown", event => {
    const typing = event.target.closest("input,textarea,select,[contenteditable]");
    if (event.key === "f" && !event.altKey && !event.ctrlKey && !event.metaKey && !typing) {
      event.preventDefault();
      feedbackText.focus();
    } else if (event.key === "Enter" && (event.ctrlKey || event.metaKey) && event.target === feedbackText) {
      event.preventDefault();
      form.requestSubmit();
    }
  });
  let frame = null;
  const trackNavigation = () => { frame ??= requestAnimationFrame(() => { frame = null; updateNavigation(); }); };
  document.addEventListener("scroll", trackNavigation, {passive: true});
  window.addEventListener("resize", trackNavigation);
  setInterval(updateFreshness, 30000);
  poll();
})();
