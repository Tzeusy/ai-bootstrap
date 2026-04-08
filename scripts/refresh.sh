#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$ROOT/skills/personal/excalidraw-diagram"
VENDOR_DIR="$SKILL_DIR/references/vendor"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Refreshing vendored Excalidraw bundle..."

mkdir -p "$VENDOR_DIR"

cat >"$TMP_DIR/package.json" <<'JSON'
{
  "name": "excalidraw-diagram-refresh",
  "private": true,
  "type": "module"
}
JSON

cat >"$TMP_DIR/entry.mjs" <<'JS'
import { exportToSvg } from "@excalidraw/excalidraw";
window.__EXCALIDRAW_EXPORT_TO_SVG__ = exportToSvg;
JS

pushd "$TMP_DIR" >/dev/null
npm install --silent @excalidraw/excalidraw@latest esbuild@latest
PACKAGE_VERSION="$(node -p "require('./node_modules/@excalidraw/excalidraw/package.json').version")"
npx esbuild entry.mjs \
  --bundle \
  --format=esm \
  --platform=browser \
  --minify \
  --outfile="$VENDOR_DIR/excalidraw.bundle.mjs"
popd >/dev/null

cat >"$VENDOR_DIR/excalidraw.bundle.version.json" <<JSON
{
  "package": "@excalidraw/excalidraw",
  "version": "$PACKAGE_VERSION"
}
JSON

echo "Bundled @excalidraw/excalidraw@$PACKAGE_VERSION -> $VENDOR_DIR/excalidraw.bundle.mjs"
