# Diagram Assets

Store future topology-diagram assets here when the maps outgrow inline markdown diagrams.

Conventions:

- Keep editable sources beside rendered outputs.
- Use stable names such as `system-overview.mmd`, `system-overview.excalidraw`, and `system-overview.svg`.
- Record the regeneration command or script in the markdown file that references the asset.
- If a diagram reflects ignored/local-only boundaries, state the source of truth used to derive it, such as `.gitignore` plus the relevant tool config docs.
- Diagrams must agree with the structural contract in RFC 0001 (`../../legends-and-lore/rfcs/`) and the repository-shape spec under `openspec/`; when they diverge, fix the diagram or escalate the contract change — a rendered map must not become a second source of truth.
