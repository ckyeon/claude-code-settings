#!/usr/bin/env bash
# Tests for the tools under bin/.
#
# Builds a throwaway copy of the tooling plus a fake upstream in a temp dir and
# runs the tools there with HOME pointed at an empty directory. Nothing touches
# the real repo, ~/.claude, or the network.
#
# Usage: tests/run.sh
# Exit: 0 when every check passes, 1 otherwise.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/settings-tests.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/home" "$TMP/tmp"

PASS=0
FAIL=0

ok() { PASS=$((PASS + 1)); printf '  ok    %s\n' "$1"; }
bad() {
  FAIL=$((FAIL + 1))
  printf '  FAIL  %s\n' "$1"
  if [ -n "${2:-}" ]; then printf '%s\n' "$2" | head -25 | sed 's/^/          /'; fi
}
# has <description> <output> <needle>
has() { case "$2" in *"$3"*) ok "$1" ;; *) bad "$1" "missing: $3"$'\n'"--- output ---"$'\n'"$2" ;; esac; }
lacks() { case "$2" in *"$3"*) bad "$1" "unexpected: $3"$'\n'"--- output ---"$'\n'"$2" ;; *) ok "$1" ;; esac; }
# eq <description> <actual> <expected>
eq() { if [ "$2" = "$3" ]; then ok "$1"; else bad "$1" "expected: $3"$'\n'"actual:   $2"; fi; }

# Every git and tool call runs without the user's global config or plugin cache.
git_clean() { HOME="$TMP/home" GIT_CONFIG_NOSYSTEM=1 git -c user.name=test -c user.email=test@example.invalid "$@"; }
# run <command...> — inside the sandbox repo, output and stderr together.
run() { (cd "$REPO" && HOME="$TMP/home" GIT_CONFIG_NOSYSTEM=1 TMPDIR="$TMP/tmp" "$@") 2>&1; }

# ----- Fake upstream ---------------------------------------------------------
UP="$TMP/upstream"
mkdir -p "$UP"
git_clean -C "$UP" init -q -b main

put() { mkdir -p "$UP/$(dirname "$1")"; printf '%s\n' "$2" > "$UP/$1"; }
skill() { put "$1/SKILL.md" "---
name: $(basename "$1")
description: fixture skill
---
${2:-body}"; }
commit() { git_clean -C "$UP" add -A && git_clean -C "$UP" commit -q --allow-empty -m "$1" && git_clean -C "$UP" rev-parse HEAD; }

# c1: the state items are first adopted from.
skill skills/eng/a "a v1"
put skills/eng/a/old.md "dropped in c2"
skill skills/eng/b
skill skills/eng/r
skill skills/eng/z
skill skills/beta/old
put plugins/p1/.claude-plugin/plugin.json "{}"
skill plugins/p1/skills/s1
C1="$(commit c1)"

# c2: content change, a removal, and additions in every position that matters.
skill skills/eng/a "a v2"
rm "$UP/skills/eng/a/old.md"
rm -rf "$UP/skills/eng/r"
skill skills/eng/c                      # new sibling of a tracked path
skill skills/eng/a/sub                  # inside a tracked path
skill skills/eng/b/deep                 # nested in an existing, unadopted skill
skill skills/beta/new                   # new skill outside the tracked dirs
skill plugins/p1/skills/s2              # new skill inside an existing plugin
put plugins/p2/.claude-plugin/plugin.json "{}"
skill plugins/p2/skills/x               # new plugin, with a skill nested in it
skill "docs/ünï"                        # non-ASCII path
C2="$(commit c2)"

# c3: nothing structural changes after c2.
C3="$(commit c3)"

SRC="file://$UP"

# ----- Sandbox repo ----------------------------------------------------------
REPO="$TMP/repo"
mkdir -p "$REPO/user/shared/skills"
cp -R "$ROOT/bin" "$ROOT/lib" "$REPO/"
git_clean -C "$REPO" init -q -b main

adopt() { # adopt <commit> <upstream-path> <dest> [mode]
  run bin/adopt --from "$SRC" --commit "$1" --path "$2" --to "$3" \
    --mode "${4:-copied}" --license MIT --no-index --no-check
}
sidecar_entries() { python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["provenance"]))' "$1"; }

# ----- bin/adopt -------------------------------------------------------------
echo "bin/adopt"

out="$(adopt "$C1" skills/eng/a user/shared/skills/a)"
eq "first adoption copies the skill" "$(sed -n 5p "$REPO/user/shared/skills/a/SKILL.md")" "a v1"
eq "first adoption writes one sidecar entry" "$(sidecar_entries "$REPO/user/shared/skills/a/.provenance.json")" "1"
lacks "first adoption prints no structure warning" "$out" "Upstream structure changed"
adopt "$C1" skills/eng/r user/shared/skills/r >/dev/null
adopt "$C1" skills/eng/z user/shared/skills/z >/dev/null

# check-updates needs the pre-re-pin state, so it runs before the re-pin below.
echo "bin/check-updates"

out="$(run bin/check-updates)"; rc=$?
eq "fast check exits 1 when pins are behind" "$rc" "1"
has "fast check counts the outdated source" "$out" "1 outdated"

out="$(run bin/check-updates --deep)"
has "deep marks a content change as CHANGED" "$out" "CHANGED    1 commit  user/shared/skills/a"
has "deep marks an untouched path as pin-only" "$out" "pin-only     user/shared/skills/z"
has "deep reports a new sibling" "$out" "NEW      upstream added   skills/eng/c"
has "deep flags a removed entry that is adopted here" "$out" "skills/eng/r  ** adopted here **"
has "deep reports a new skill outside the tracked dirs" "$out" "skills/beta/new  (outside tracked dirs)"
has "deep reports a new plugin once, as its outer directory" "$out" "plugins/p2  (outside tracked dirs)"
lacks "deep folds a nested skill into its plugin" "$out" "plugins/p2/skills/x"
lacks "deep skips a new skill inside an existing plugin" "$out" "plugins/p1/skills/s2"
lacks "deep skips a new skill inside a tracked path" "$out" "skills/eng/a/sub"
lacks "deep skips a skill nested in an unadopted skill" "$out" "skills/eng/b/deep"
lacks "deep stays silent about entries that predate the pin" "$out" "skills/beta/old"
eq "deep reports three entries outside the tracked dirs" "$(printf '%s\n' "$out" | grep -c "(outside tracked dirs)")" "3"
deep_json="$(ls -d "$TMP"/tmp/check-updates-deep-*/deep.json 2>/dev/null | head -1)"
scopes="$(python3 -c 'import json,sys; print(",".join(sorted(r["scope"] for r in json.load(open(sys.argv[1]))["structure"])))' "$deep_json" 2>&1)"
eq "deep.json labels each structure record with its scope" "$scopes" "elsewhere,sibling"

echo "bin/adopt (re-pin)"

out="$(adopt "$C2" skills/eng/a user/shared/skills/a)"
eq "re-pin updates the content" "$(sed -n 5p "$REPO/user/shared/skills/a/SKILL.md")" "a v2"
eq "re-pin appends a sidecar entry" "$(sidecar_entries "$REPO/user/shared/skills/a/.provenance.json")" "2"
if [ -e "$REPO/user/shared/skills/a/old.md" ]; then bad "re-pin prunes a file upstream deleted"; else ok "re-pin prunes a file upstream deleted"; fi
has "re-pin warns about a new sibling" "$out" "NEW      skills/eng/c"
has "re-pin warns about a removed sibling" "$out" "REMOVED  skills/eng/r"
has "re-pin warns about a new skill outside the tracked dirs" "$out" "skills/beta/new  (outside tracked dirs)"
lacks "re-pin skips a new skill inside the adopted path" "$out" "skills/eng/a/sub"

out="$(adopt "$C3" skills/eng/a user/shared/skills/a)"
lacks "re-pin with no structure change prints no warning" "$out" "Upstream structure changed"

mkdir -p "$REPO/user/shared/plugins/gone"
printf 'declared\n' > "$REPO/user/shared/plugins/gone/README.md"
adopt "$C1" skills/eng/r user/shared/plugins/gone inspired-by >/dev/null
out="$(adopt "$C3" skills/eng/r user/shared/plugins/gone inspired-by)"
has "inspired-by re-pin warns when the path vanished upstream" "$out" "does not exist upstream"
rm -rf "$REPO/user/shared/plugins"

echo "bin/check-updates (after re-pin)"

adopt "$C3" skills/eng/z user/shared/skills/z >/dev/null
rm -rf "$REPO/user/shared/skills/r"
out="$(run bin/check-updates)"; rc=$?
eq "fast check exits 0 when every pin matches" "$rc" "0"

# ----- bin/check-integrity ---------------------------------------------------
echo "bin/check-integrity"

caller() { # caller <body> — a self-authored skill whose body holds one reference
  mkdir -p "$REPO/user/shared/skills/caller"
  printf -- '---\nname: caller\ndescription: fixture caller\n---\n%s\n' "$1" > "$REPO/user/shared/skills/caller/SKILL.md"
}

out="$(run bin/check-integrity)"; rc=$?
eq "a consistent repo exits 0" "$rc" "0"
has "a consistent repo reports Clean" "$out" "Clean."

caller 'Call the Skill tool with "a" to start.'
out="$(run bin/check-integrity)"; rc=$?
eq "a resolvable quoted Skill tool call passes" "$rc" "0"

caller 'Call the Skill tool with "ghost" to start.'
out="$(run bin/check-integrity)"; rc=$?
eq "an unresolved quoted Skill tool call exits 1" "$rc" "1"
has "an unresolved quoted Skill tool call is named" "$out" 'references skill "ghost" (Skill tool call)'

caller 'Use the `/ghost` skill first.'
out="$(run bin/check-integrity)"; rc=$?
eq "an unresolved /name skill reference exits 1" "$rc" "1"

caller 'Run `/ghost` first.'
out="$(run bin/check-integrity)"; rc=$?
eq "a bare unresolved /token only warns" "$rc" "0"
has "the warning names the token" "$out" 'unresolved reference `/ghost`'
out="$(run bin/check-integrity --strict)"; rc=$?
eq "--strict turns the warning into a failure" "$rc" "1"

caller 'See [the notes](missing.md).'
out="$(run bin/check-integrity)"; rc=$?
eq "a broken relative link exits 1" "$rc" "1"
rm -rf "$REPO/user/shared/skills/caller"

python3 - "$REPO/user/shared/skills/z/.provenance.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["trak"] = "release"
json.dump(d, open(p, "w"))
PY
out="$(run bin/check-integrity)"; rc=$?
eq "an unknown sidecar top-level key exits 1" "$rc" "1"
has "the unknown key is named" "$out" "unknown top-level key(s): trak"

# ----- Summary ---------------------------------------------------------------
echo ""
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
