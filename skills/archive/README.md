# Legacy skill packages

This directory contains retired packages kept only for history-backed rollback.
It is not an authored source or installation surface. The skill linker prunes
`archive/` completely, so none of these packages enters the Claude, Codex,
Gemini, or Antigravity catalogs.

To revive useful upstream-derived behavior, move and tune it under
`skills/personal/`, record its source revision, authorship, license, and local
relationship, then validate it as an active package. Do not link archived
content directly into a runtime catalog.
