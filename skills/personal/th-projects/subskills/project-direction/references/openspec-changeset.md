# OpenSpec Changeset Synthesis (Tool-Agnostic)

How to turn Phase 2 findings into an OpenSpec changeset using the `openspec`
CLI directly. This procedure works from any agent environment. In Codex, the
`/opsx:ff` prompt automates the same loop — treat it as an accelerator, not a
dependency; the acceptance criteria are identical either way.

Prerequisite: `openspec` on PATH (`which openspec`). If the CLI is missing,
stop and report it — do not hand-write changeset files into
`openspec/changes/`; the scaffold and schema come from the tool.

## The Loop

1. **Name the change** — kebab-case, derived from the finding set (e.g.
   `align-auth-spec-with-implementation`). One changeset per coherent theme;
   split unrelated findings into separate changes.

2. **Scaffold it**:
   ```bash
   openspec new change "<name>"
   ```
   Creates `openspec/changes/<name>/`.

3. **Get the artifact build order**:
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse `applyRequires` (artifact IDs needed before implementation) and
   `artifacts` (each with status and dependencies).

4. **Create artifacts in dependency order.** For each artifact whose
   dependencies are satisfied:
   ```bash
   openspec instructions <artifact-id> --change "<name>" --json
   ```
   The JSON gives you `template` (the structure), `instruction`
   (schema-specific guidance), `outputPath` (where to write), `dependencies`
   (completed artifacts to read first), plus `context` and `rules` — apply
   those two as constraints; do not copy them into the output file.

   Write the artifact, grounding every requirement in Phase 2 evidence
   (agent findings, file references, drift inventory). Re-run
   `openspec status --change "<name>" --json` after each artifact; continue
   until everything in `applyRequires` is `done`.

5. **Verify**: `openspec status --change "<name>"` should report apply-ready.
   The changeset then enters reconciliation (see SKILL.md — changeset edits
   are change-tier).

## Content Rules

- Every requirement traces to evidence: a doctrine mandate, an agent finding,
  or an observed implementation behavior — cite it in the artifact.
- Delta semantics: active changes override main specs. Extend existing specs;
  never fork a parallel truth.
- Spec format follows `../../project-review/references/spec-format.md`
  (heading hierarchy, WHEN/THEN bullets, naming, `[TARGET-STATE]` tags for
  aspirational requirements).
- A changeset proposes; it does not sequence. Sequencing happens in Phase 3.
