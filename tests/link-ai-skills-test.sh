#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
linker="$repo_root/scripts/link-ai-skills.sh"
test_root="$(mktemp -d "${TMPDIR:-/tmp}/link-ai-skills-test.XXXXXX")"

cleanup() {
    local status=$?

    rm -rf -- "$test_root"
    exit "$status"
}
trap cleanup EXIT

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    exit 1
}

assert_file_contains() {
    local file="$1"
    local expected="$2"

    grep -Fqx -- "$expected" "$file" || fail "expected $file to contain: $expected"
}

write_skill() {
    local skill_dir="$1"
    local name="$2"
    local description="$3"

    mkdir -p "$skill_dir"
    printf '%s\n' \
        '---' \
        "name: $name" \
        "description: $description" \
        '---' \
        '' \
        '# Canonical instructions' > "$skill_dir/SKILL.md"
}

assert_shallow_codex_catalog() {
    local codex_skills_dir="$1"
    local skill_file
    local relative_path
    local skill_dir

    while IFS= read -r -d '' skill_file; do
        relative_path="${skill_file#"$codex_skills_dir"/}"
        [[ "$relative_path" == */SKILL.md ]] || fail "unexpected Codex skill path: $relative_path"
        skill_dir="${relative_path%/SKILL.md}"
        [[ "$skill_dir" != */* ]] || fail "nested Codex skill entered catalog: $relative_path"
    done < <(find -L "$codex_skills_dir" \
        -path "$codex_skills_dir/.system" -prune -o \
        -type f -name SKILL.md -print0)
}

bootstrap_dir="$test_root/ai-bootstrap"

write_skill "$bootstrap_dir/skills/plain" "plain" "A flat skill."
write_skill "$bootstrap_dir/skills/superskill" "superskill" "A routed parent skill."
write_skill "$bootstrap_dir/skills/superskill/subskills/deep" "deep" "Must not enter Codex's root catalog."
write_skill "$bootstrap_dir/skills/duplicate" "duplicate" "The shallow canonical skill."
write_skill "$bootstrap_dir/skills/vendor/skills/duplicate" "duplicate" "A deeper conflicting skill."
write_skill "$bootstrap_dir/skills/writing-skills" "writing-skills" "Excluded from all catalogs."
write_skill "$bootstrap_dir/.codex/skills/local" "local" "An unmanaged local skill."
write_skill "$bootstrap_dir/.codex/skills/.system/internal" "internal" "A system-owned skill outside the shared projection."

# Simulate the old direct-directory Codex installation. The first run must
# migrate this managed symlink to a generated real wrapper.
ln -s "$bootstrap_dir/skills/superskill" "$bootstrap_dir/.codex/skills/superskill"

cd "$test_root"
"$linker" "ai-bootstrap"
cd "$repo_root"

for skill_name in plain superskill duplicate; do
    wrapper="$bootstrap_dir/.codex/skills/$skill_name"
    [ -d "$wrapper" ] || fail "missing Codex wrapper for $skill_name"
    [ ! -L "$wrapper" ] || fail "Codex wrapper for $skill_name must not be a directory symlink"
    [ -f "$wrapper/.codex-skill-projection" ] || fail "missing managed marker for $skill_name"
done

[ ! -e "$bootstrap_dir/.codex/skills/writing-skills" ] || fail "excluded skill entered Codex catalog"
[ -f "$bootstrap_dir/.codex/skills/local/SKILL.md" ] || fail "unmanaged Codex skill was removed"
assert_shallow_codex_catalog "$bootstrap_dir/.codex/skills"

superskill_wrapper="$bootstrap_dir/.codex/skills/superskill/SKILL.md"
assert_file_contains "$superskill_wrapper" "name: superskill"
assert_file_contains "$superskill_wrapper" "description: A routed parent skill."
grep -Fq -- "$bootstrap_dir/skills/superskill/SKILL.md" "$superskill_wrapper" || fail "wrapper does not redirect to canonical source"

duplicate_wrapper="$bootstrap_dir/.codex/skills/duplicate/SKILL.md"
grep -Fq -- "$bootstrap_dir/skills/duplicate/SKILL.md" "$duplicate_wrapper" || fail "shallower duplicate source did not win"
grep -Fq -- "$bootstrap_dir/skills/vendor/skills/duplicate/SKILL.md" "$duplicate_wrapper" && fail "deeper duplicate source unexpectedly won"

for target in \
    "$bootstrap_dir/.claude/skills/superskill" \
    "$bootstrap_dir/.gemini/skills/superskill" \
    "$bootstrap_dir/.gemini/antigravity/skills/superskill"; do
    [ -L "$target" ] || fail "$target must remain a direct source symlink"
    [ "$(readlink "$target")" = "$bootstrap_dir/skills/superskill" ] || fail "$target points at the wrong source"
done

"$linker" "$bootstrap_dir"

rm -rf -- "$bootstrap_dir/skills/plain"
"$linker" "$bootstrap_dir"

[ ! -e "$bootstrap_dir/.codex/skills/plain" ] || fail "stale managed Codex wrapper was not removed"
[ -f "$bootstrap_dir/.codex/skills/local/SKILL.md" ] || fail "stale cleanup removed unmanaged Codex skill"

codex_conflict_dir="$test_root/codex-conflict"
write_skill "$codex_conflict_dir/skills/plain" "plain" "A canonical skill."
write_skill "$codex_conflict_dir/.codex/skills/plain" "plain" "An unmanaged local skill."
if "$linker" "$codex_conflict_dir" > "$test_root/codex-conflict.log" 2>&1; then
    fail "unmanaged Codex collision should fail"
fi
[ -f "$codex_conflict_dir/.codex/skills/plain/SKILL.md" ] || fail "unmanaged Codex collision was removed"

claude_conflict_dir="$test_root/claude-conflict"
write_skill "$claude_conflict_dir/skills/plain" "plain" "A canonical skill."
write_skill "$claude_conflict_dir/.claude/skills/plain" "plain" "An unmanaged local skill."
if "$linker" "$claude_conflict_dir" > "$test_root/claude-conflict.log" 2>&1; then
    fail "unmanaged Claude collision should fail"
fi
[ -f "$claude_conflict_dir/.claude/skills/plain/SKILL.md" ] || fail "unmanaged Claude collision was removed"

printf 'link-ai-skills test: PASS\n'
