/* Fixed, offline rendering. Polling never invokes a model or a task tracker. */
"use strict";

(() => {
  const byId = id => document.getElementById(id);
  const text = (id, value) => {
    const node = byId(id);
    const content = String(value ?? "");
    if (node.textContent !== content) node.textContent = content;
  };
  const number = value => Number.isFinite(value) ? new Intl.NumberFormat().format(value) : "Unknown";
  const compact = value => Number.isFinite(value) ? new Intl.NumberFormat(undefined, {notation: "compact", maximumFractionDigits: 1}).format(value) : "Unknown";
  const form = byId("feedback-form");
  const feedbackText = byId("feedback-text");
  const kind = byId("feedback-kind");
  const target = byId("feedback-target");
  const result = byId("feedback-result");
  const draftKey = `progress-dashboard-draft:${location.pathname}`;
  let current = null;
  let etag = null;
  let timer = null;
  let inFlight = false;
  let failures = 0;
  let lastSuccess = null;
  let sending = false;
  let pendingSubmission = null;
  let targetSignature = "";
  const signatures = new Map();

  function el(tag, className, content) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined && content !== null) node.textContent = content;
    return node;
  }

  function changed(key, value, render) {
    const signature = JSON.stringify(value);
    if (signatures.get(key) !== signature) {
      const focused = document.activeElement;
      const focusKey = focused?.dataset.focusKey;
      render();
      // A changed row must not strand a keyboard user at the document root.
      if (focusKey && document.activeElement !== focused) {
        [...document.querySelectorAll("[data-focus-key]")].find(node => node.dataset.focusKey === focusKey)?.focus({preventScroll: true});
      }
      signatures.set(key, signature);
    }
  }

  function dateLabel(value) {
    if (typeof value !== "string" || !value) return "Unknown time";
    const date = new Date(value);
    return Number.isFinite(date.getTime()) ? date.toLocaleString(undefined, {month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"}) : "Unknown time";
  }

  function age(value) {
    if (typeof value !== "string" || !value) return "time unknown";
    const elapsed = Date.now() - new Date(value).getTime();
    if (!Number.isFinite(elapsed)) return "time unknown";
    if (elapsed < 60000) return "just now";
    if (elapsed < 3600000) return `${Math.floor(elapsed / 60000)}m ago`;
    if (elapsed < 86400000) return `${Math.floor(elapsed / 3600000)}h ago`;
    return `${Math.floor(elapsed / 86400000)}d ago`;
  }

  function statusClass(value) {
    if (["running", "working", "active", "implementing", "reviewing", "in-progress", "in_progress"].includes(value)) return "active";
    if (["waiting", "blocked", "parked", "pending", "idle"].includes(value)) return "waiting";
    if (["error", "failed"].includes(value)) return "error";
    return "neutral";
  }

  function relativeTime(value, prefix) {
    const node = el("span", null, `${prefix}${age(value)}`);
    node.dataset.relativeTime = value || "";
    node.dataset.timePrefix = prefix;
    return node;
  }

  function clientId() {
    // getRandomValues also works on private-network HTTP origins where
    // randomUUID is unavailable because the origin is not a secure context.
    if (typeof crypto.randomUUID === "function") return crypto.randomUUID();
    const bytes = crypto.getRandomValues(new Uint8Array(16));
    bytes[6] = (bytes[6] & 15) | 64;
    bytes[8] = (bytes[8] & 63) | 128;
    const hex = [...bytes].map(byte => byte.toString(16).padStart(2, "0")).join("");
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  }

  function commentButton(id, label) {
    const button = el("button", "task-feedback", "Comment");
    button.type = "button";
    button.dataset.focusKey = `comment:${id}`;
    button.setAttribute("aria-label", `Comment on ${label}`);
    button.addEventListener("click", () => {
      if ([...target.options].some(option => option.value === id)) target.value = id;
      saveDraft();
      feedbackText.focus();
      byId("feedback-heading").scrollIntoView({block: "center", behavior: "auto"});
    });
    return button;
  }

  function renderTasks(tasks) {
    const labels = {"in-progress": "In progress", todo: "Up next", complete: "Completed"};
    for (const status of Object.keys(labels)) {
      const destination = byId(status);
      destination.replaceChildren();
      const matching = tasks.filter(task => task.status === status);
      if (status !== "complete") {
        const heading = el("h3", "task-group-heading", labels[status]);
        heading.append(el("span", "count", matching.length));
        destination.append(heading);
      }
      if (!matching.length) {
        destination.append(el("p", "empty", status === "in-progress" ? "No active task at this checkpoint." : status === "todo" ? "No upcoming work recorded." : "Completed work will appear here."));
      }
      for (const task of matching) {
        const article = el("article", "task");
        const row = el("div", "task-title");
        const mark = el("span", `task-status-mark ${status}`, status === "complete" ? "✓" : status === "in-progress" ? "◐" : "○");
        mark.setAttribute("aria-hidden", "true");
        row.append(mark, el("h3", null, task.title), commentButton(task.id, task.title));
        article.append(row);
        if (task.id) article.append(el("span", "task-id", task.id));
        if (task.detail) article.append(el("p", "task-detail", task.detail));
        if (task.evidence) article.append(el("p", "task-evidence", `Evidence · ${task.evidence}`));
        destination.append(article);
      }
    }
  }

  function renderAgents(agents, telemetry) {
    const destination = byId("agent-list");
    const existing = new Map([...destination.querySelectorAll(".agent")].map(node => [node.dataset.agentId, node]));
    for (const node of destination.querySelectorAll(".empty")) node.remove();
    if (!agents.length) destination.append(el("p", "empty", "No subagents recorded. This loop may be working on its own."));
    const usage = new Map((telemetry.agents || []).map(agent => [agent.id, agent]));
    for (const agent of agents) {
      const measured = usage.get(agent.id);
      const signature = JSON.stringify([agent, measured]);
      const prior = existing.get(agent.id);
      existing.delete(agent.id);
      if (prior?.dataset.signature === signature) continue;
      const article = el("article", "agent");
      article.dataset.agentId = agent.id;
      article.dataset.signature = signature;
      const heading = el("div", "agent-heading");
      const name = agent.name || agent.id;
      heading.append(el("h3", null, name), el("span", `badge ${statusClass(agent.status)}`, agent.status || "Unknown"));
      if (agent.role) heading.append(el("span", "agent-role", agent.role));
      heading.append(commentButton(agent.id, name));
      article.append(heading);
      if (agent.task) article.append(el("p", "agent-task", agent.task));
      if (agent.summary) article.append(el("p", "agent-summary", agent.summary));
      const meta = el("div", "agent-meta");
      if (agent.model) meta.append(el("span", null, agent.model));
      meta.append(el("span", null, measured?.status === "measured" ? `${number(measured.total_tokens)} tokens · ${measured.provider || "runtime"}` : "Token usage unknown"));
      meta.append(relativeTime(agent.updated_at, "Status · "));
      if (measured?.status === "measured") meta.append(relativeTime(measured.observed_at, "Usage · "));
      article.append(meta);
      if (prior) prior.replaceWith(article);
      else destination.append(article);
    }
    for (const node of existing.values()) node.remove();
    // Reorder retained rows without recreating their controls.
    const ordered = new Map([...destination.querySelectorAll(".agent")].map(node => [node.dataset.agentId, node]));
    agents.forEach((agent, index) => {
      const node = ordered.get(agent.id);
      if (destination.children[index] !== node) destination.insertBefore(node, destination.children[index] || null);
    });
    const rows = byId("usage-rows");
    rows.replaceChildren();
    for (const usageRow of telemetry.agents || []) {
      const row = el("tr");
      const name = agents.find(agent => agent.id === usageRow.id)?.name || usageRow.id;
      const first = el("td", null, name);
      first.append(el("small", null, `${usageRow.provider || "Unknown source"} · ${usageRow.status || "unknown"}`));
      if (usageRow.status === "measured") first.append(relativeTime(usageRow.observed_at, "Usage · "));
      if (usageRow.reason) first.append(el("small", null, usageRow.reason.replaceAll("-", " ")));
      row.append(first);
      for (const field of ["input_tokens", "cached_input_tokens", "output_tokens", "total_tokens"]) row.append(el("td", null, usageRow.status === "measured" ? number(usageRow[field]) : "Unknown"));
      rows.append(row);
    }
    if (!rows.children.length) {
      const cell = el("td", null, "No runtime usage counters attached.");
      cell.colSpan = 5;
      rows.append(el("tr"));
      rows.lastChild.append(cell);
    }
    text("usage-note", "Counters come from attached runtime records. Cached input is shown separately and may already be included in input. Missing sessions are excluded; counts are not a bill or a measure of engineering progress.");
  }

  function renderArtifacts(artifacts) {
    const destination = byId("artifact-list");
    destination.replaceChildren();
    if (!artifacts.length) destination.append(el("p", "empty", "Diagrams, rendered graphs, and other evidence will appear here when published."));
    for (const artifact of artifacts) {
      const image = /\.(png|jpe?g|gif|webp|svg)$/i.test(artifact.path);
      const figure = el("figure", `artifact${image ? "" : " download-only"}`);
      const url = `artifacts/${encodeURIComponent(artifact.path)}`;
      if (image) {
        const preview = el("img");
        preview.src = url;
        preview.alt = artifact.label || artifact.path;
        preview.loading = "lazy";
        figure.append(preview);
      }
      const caption = el("figcaption");
      const link = el("a", null, "Download");
      link.href = url;
      link.setAttribute("aria-label", `Download ${artifact.label || artifact.path}`);
      link.download = artifact.path.split("/").pop();
      caption.append(el("span", null, artifact.label || artifact.path), link);
      figure.append(caption);
      destination.append(figure);
    }
  }

  // A small readable Markdown subset; text never enters an HTML parser.
  function renderDocument(destination, content) {
    destination.replaceChildren();
    if (!content) {
      destination.append(el("p", "empty", "No document published yet."));
      return;
    }
    let paragraph = [];
    let list = null;
    let code = null;
    const flush = () => {
      if (paragraph.length) destination.append(el("p", null, paragraph.join("\n")));
      paragraph = [];
      list = null;
    };
    for (const line of content.split("\n")) {
      if (line.startsWith("```")) {
        if (code) code = null;
        else { flush(); code = el("pre"); destination.append(code); }
        continue;
      }
      if (code) { code.textContent += `${line}\n`; continue; }
      const heading = /^(#{1,6})\s+(.+)$/.exec(line);
      if (heading) { flush(); destination.append(el(`h${Math.min(heading[1].length + 1, 6)}`, null, heading[2])); continue; }
      const bullet = /^\s*[-*]\s+(.+)$/.exec(line);
      if (bullet) {
        if (!list) { flush(); list = el("ul"); destination.append(list); }
        list.append(el("li", null, bullet[1]));
      } else if (!line.trim()) flush();
      else { list = null; paragraph.push(line); }
    }
    flush();
  }

  function renderDocuments(documents) {
    const destination = byId("document-list");
    for (const name of ["in-progress.md", "todo.md", "complete.md"]) {
      let details = [...destination.children].find(node => node.dataset.name === name);
      if (!details) {
        details = el("details", "document");
        details.dataset.name = name;
        details.append(el("summary", null, name), el("div", "document-body"));
        destination.append(details);
      }
      changed(`document:${name}`, documents[name], () => renderDocument(details.lastChild, documents[name]));
    }
    changed("document:handover", documents["handover.md"], () => renderDocument(byId("handover-content"), documents["handover.md"]));
  }

  function renderFeedback(feedback) {
    const destination = byId("feedback-history");
    const previousScroll = destination.scrollTop;
    const pinnedBottom = previousScroll + destination.clientHeight >= destination.scrollHeight - 25;
    destination.replaceChildren();
    const pending = feedback.filter(item => item.status === "pending").length;
    text("feedback-pending", pending ? `${pending} awaiting checkpoint` : "");
    text("nav-feedback", pending);
    byId("nav-feedback").hidden = !pending;
    if (!feedback.length) destination.append(el("p", "empty small", "Your feedback and the loop’s replies will appear here."));
    for (const item of feedback) {
      const article = el("article", "feedback-item");
      const meta = el("div", "feedback-meta");
      meta.append(el("span", null, item.kind === "steer" ? "Direction" : item.kind === "question" ? "Question" : "Feedback"));
      if (item.target && item.target !== "loop") meta.append(el("span", null, `· ${item.target}`));
      meta.append(el("span", `badge ${item.status === "pending" ? "waiting" : "neutral"}`, item.status === "pending" ? "Queued" : "Acknowledged"));
      const time = el("time", null, dateLabel(item.created_at));
      time.dateTime = item.created_at;
      meta.append(time);
      article.append(meta, el("p", "feedback-content", item.text));
      if (item.response) {
        const response = el("div", "feedback-response");
        response.append(el("span", "response-label", "Loop response"), el("span", null, item.response));
        article.append(response);
      }
      destination.append(article);
    }
    destination.scrollTop = pinnedBottom ? destination.scrollHeight : previousScroll;
  }

  function updateTargets(state) {
    const options = [{id: "loop", label: "Whole loop"}, ...(state.tasks || []).map(task => ({id: task.id, label: `Task · ${task.title}`})), ...(state.agents || []).map(agent => ({id: agent.id, label: `Agent · ${agent.name || agent.id}`}))];
    const signature = JSON.stringify(options);
    if (signature === targetSignature) return;
    // A running update must not replace the user's open dropdown or target.
    if (document.activeElement === target) return;
    const selected = target.value;
    target.replaceChildren();
    for (const option of options) {
      const node = el("option", null, option.label);
      node.value = option.id;
      target.append(node);
    }
    if (![...target.options].some(option => option.value === selected)) {
      const removed = el("option", null, `${selected} · previously selected`);
      removed.value = selected;
      target.append(removed);
    }
    target.value = selected;
    targetSignature = signature;
  }

  function render(data) {
    current = data;
    const state = data.state;
    const tasks = state.tasks || [];
    const agents = state.agents || [];
    const telemetry = data.telemetry || {agents: [], totals: {}, coverage: {attached: 0, measured: 0}};
    const completed = tasks.filter(task => task.status === "complete").length;
    const running = agents.filter(agent => statusClass(agent.status) === "active").length;
    const waiting = agents.filter(agent => statusClass(agent.status) === "waiting").length;
    const completeAgents = agents.filter(agent => agent.status === "complete").length;
    const failedAgents = agents.filter(agent => agent.status === "failed").length;
    const unknownAgents = agents.length - running - waiting - completeAgents - failedAgents;
    document.title = `${state.title || state.slug} · Progress workspace`;
    text("loop-name", state.slug);
    text("title", state.title || state.slug);
    text("summary", state.summary || "No progress summary published yet.");
    text("phase", state.phase || "No phase reported");
    text("actor", state.actor);
    text("repository", state.repo_root);
    text("outcome", state.outcome ? `Outcome · ${state.outcome}` : "");
    byId("outcome").hidden = !state.outcome;
    text("completed-count", `${completed} / ${tasks.length}`);
    text("work-caption", tasks.length ? `${tasks.filter(task => task.status === "in-progress").length} in progress · ${tasks.filter(task => task.status === "todo").length} up next` : "No work recorded");
    byId("work-progress").max = Math.max(1, tasks.length);
    byId("work-progress").value = completed;
    const measured = telemetry.coverage?.measured || 0;
    const attached = telemetry.coverage?.attached || 0;
    const expected = telemetry.coverage?.expected ?? attached;
    text("token-total", measured ? compact(telemetry.totals?.total_tokens) : "Unknown");
    byId("token-total").title = measured ? `${number(telemetry.totals?.total_tokens)} reported tokens` : "No measured runtime counters";
    byId("token-coverage").hidden = !measured || measured >= expected;
    text("usage-warning", telemetry.error || "");
    byId("usage-warning").hidden = !telemetry.error;
    text("token-caption", telemetry.error ? "Usage unavailable · see session details" : expected ? `${measured} of ${expected} sessions measured · ${expected - measured} unknown` : "No usage counters attached");
    byId("token-caption").title = `${attached} sessions attached. Missing or incomplete counters are excluded from totals.`;
    text("token-breakdown", measured ? `${compact(telemetry.totals?.input_tokens)} in · ${compact(telemetry.totals?.output_tokens)} out · ${compact(telemetry.totals?.cached_input_tokens)} cached` : "Unavailable usage stays unknown");
    text("agent-total", `${agents.length} recorded`);
    const activity = [[running, "working"], [waiting, "waiting"], [completeAgents, "complete"], [failedAgents, "failed"], [unknownAgents, "unknown"]];
    text("agent-caption", agents.length ? activity.filter(([count]) => count).map(([count, label]) => `${count} ${label}`).join(" · ") : "No subagents recorded");
    text("nav-work", tasks.length);
    text("nav-agents", agents.length);
    text("nav-findings", (state.findings || []).length);
    text("nav-artifacts", (state.artifacts || []).length);
    text("completed-badge", completed);
    text("work-revision", `Checkpoint ${state.revision}`);
    changed("tasks", tasks, () => renderTasks(tasks));
    changed("findings", state.findings || [], () => {
      const destination = byId("findings");
      destination.replaceChildren(...(state.findings?.length ? state.findings.map(finding => el("p", "finding", finding)) : [el("p", "empty", "Findings and useful context will appear as the work progresses.")]));
    });
    changed("agents", [agents, telemetry.agents], () => renderAgents(agents, telemetry));
    changed("artifacts", state.artifacts || [], () => renderArtifacts(state.artifacts || []));
    changed("documents", data.documents || {}, () => renderDocuments(data.documents || {}));
    changed("feedback", data.feedback || [], () => renderFeedback(data.feedback || []));
    updateTargets(state);
    const enabled = data.feedback_enabled !== false;
    for (const field of form.elements) field.disabled = !enabled;
    updateSubmitState();
    text("feedback-explanation", enabled ? "Leave feedback here. The loop reads it at its next safe checkpoint." : "Feedback is disabled for this workspace. You can still inspect progress and previous replies.");
    updateFreshness();
    updateNavigation();
  }

  function updateFreshness() {
    if (!current) return;
    const updated = current.state.updated_at;
    const elapsed = Date.now() - new Date(updated).getTime();
    const stale = !Number.isFinite(elapsed) || elapsed > 300000;
    text("checkpoint-time", `Checkpoint ${age(updated)}${stale ? " · status may be stale" : ""}`);
    byId("checkpoint-time").classList.toggle("stale", stale);
    byId("checkpoint-time").title = `Progress last reported ${dateLabel(updated)}. Page refreshes do not imply the loop is currently executing.`;
    text("footer-state", `Checkpoint ${current.state.revision} · ${dateLabel(updated)}`);
    for (const node of document.querySelectorAll("[data-relative-time]")) node.textContent = `${node.dataset.timePrefix}${age(node.dataset.relativeTime)}`;
    if (!failures && lastSuccess) text("connection-text", document.hidden ? "Updates paused" : "Page connected");
  }

  function updateSubmitState() {
    byId("submit-feedback").disabled = !current || current.feedback_enabled === false || sending || !feedbackText.value.trim();
  }

  function saveDraft() {
    updateSubmitState();
    try {
      sessionStorage.setItem(draftKey, JSON.stringify({text: feedbackText.value, kind: kind.value, target: target.value, pending: pendingSubmission}));
      text("draft-state", feedbackText.value ? "Draft kept in this tab" : "");
    } catch { text("draft-state", feedbackText.value ? "Draft in memory" : ""); }
  }

  function restoreDraft() {
    try {
      const draft = JSON.parse(sessionStorage.getItem(draftKey) || "null");
      if (!draft) return;
      feedbackText.value = draft.text || "";
      if (["feedback", "steer", "question"].includes(draft.kind)) kind.value = draft.kind;
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
    result.classList.toggle("error", error);
    result.textContent = message;
  }

  async function submitFeedback(event) {
    event.preventDefault();
    if (sending || !current || current.feedback_enabled === false) return;
    const message = feedbackText.value.trim();
    if (!message) { feedbackText.focus(); return; }
    const content = {kind: kind.value, target: target.value, text: message};
    if (!pendingSubmission || JSON.stringify(pendingSubmission.content) !== JSON.stringify(content)) pendingSubmission = {client_id: clientId(), content, revision: current.state.revision};
    const submission = pendingSubmission;
    saveDraft();
    sending = true;
    byId("submit-feedback").disabled = true;
    text("submit-feedback", "Sending…");
    form.setAttribute("aria-busy", "true");
    setResult("Saving feedback…");
    try {
      const response = await fetch("api/feedback", {method: "POST", headers: {"Content-Type": "application/json", "X-Loop-Feedback": "1"}, body: JSON.stringify({...content, client_id: submission.client_id, revision: submission.revision}), signal: AbortSignal.timeout(12000)});
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || `Feedback could not be saved (${response.status}).`);
      if (!body.feedback?.id) throw new Error("The server did not confirm a saved feedback record.");
      // A slow save must not erase a new draft typed while it was in flight.
      if (feedbackText.value.trim() === content.text && kind.value === content.kind && target.value === content.target) {
        feedbackText.value = "";
        pendingSubmission = null;
      }
      saveDraft();
      setResult("Saved. The loop will read this at its next checkpoint.");
      etag = null;
      await poll(true);
    } catch (error) {
      setResult(error.name === "TimeoutError" ? "Confirmation timed out. Your draft is kept; retrying will not create a duplicate." : `${error.message || "Could not confirm feedback."} Your draft is kept.`, true);
    } finally {
      sending = false;
      for (const field of form.elements) field.disabled = current?.feedback_enabled === false;
      text("submit-feedback", "Send feedback");
      form.setAttribute("aria-busy", "false");
      updateSubmitState();
    }
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
      const headers = etag && !force ? {"If-None-Match": etag} : {};
      const response = await fetch("api/state", {headers, cache: "no-store", signal: AbortSignal.timeout(10000)});
      if (!response.ok && response.status !== 304) throw new Error(`Progress could not be loaded (${response.status}).`);
      if (response.status !== 304) {
        const data = await response.json();
        if (!data.state || !Array.isArray(data.state.tasks)) throw new Error("The server returned an invalid progress snapshot.");
        etag = response.headers.get("ETag");
        render(data);
      }
      failures = 0;
      lastSuccess = Date.now();
      document.querySelector(".connection").dataset.state = "connected";
      byId("load-error").hidden = true;
      updateFreshness();
    } catch (error) {
      failures += 1;
      document.querySelector(".connection").dataset.state = "offline";
      text("connection-text", "Disconnected");
      const notice = byId("load-error");
      notice.textContent = `${error.message || "Connection unavailable."} ${current ? "Showing the last received snapshot. " : ""}Retrying automatically; your feedback draft is kept.`;
      notice.hidden = false;
    } finally {
      inFlight = false;
      byId("refresh").disabled = false;
      schedule();
    }
  }

  restoreDraft();
  form.addEventListener("submit", submitFeedback);
  form.addEventListener("input", () => { pendingSubmission = null; saveDraft(); });
  target.addEventListener("blur", () => { if (current) updateTargets(current.state); });
  byId("refresh").addEventListener("click", () => poll(true));
  document.addEventListener("visibilitychange", () => {
    clearTimeout(timer);
    if (!document.hidden) poll(true);
    else text("connection-text", "Updates paused");
  });
  document.addEventListener("keydown", event => {
    if (event.key === "f" && !event.altKey && !event.ctrlKey && !event.metaKey && !event.target.closest("input,textarea,select,[contenteditable]")) { event.preventDefault(); feedbackText.focus(); }
  });
  function updateNavigation() {
    const mobile = matchMedia("(max-width: 650px)").matches;
    const stacked = matchMedia("(max-width: 970px)").matches;
    const anchor = (mobile ? document.querySelector(".navigation") : document.querySelector(".topbar")).getBoundingClientRect().bottom + 48;
    const sections = document.querySelectorAll(stacked ? ".work-column > section[id], #feedback" : ".work-column > section[id]");
    let active = "work";
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= anchor) active = section.id;
    }
    for (const link of document.querySelectorAll("nav a")) link.setAttribute("aria-current", String(link.hash === `#${active}`));
  }
  let navigationFrame = null;
  const scheduleNavigation = () => {
    if (navigationFrame !== null) return;
    navigationFrame = requestAnimationFrame(() => { navigationFrame = null; updateNavigation(); });
  };
  document.addEventListener("scroll", scheduleNavigation, {passive: true});
  window.addEventListener("resize", scheduleNavigation);

  poll();
})();
