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
skill skills/prod/p
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
skill skills/prod/q                     # new sibling of a tracked path pinned elsewhere
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
# p lives in another tracked dir and is already at the newest commit, so the
# source's items sit at two different pins.
adopt "$C3" skills/prod/p user/shared/skills/p >/dev/null

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
lacks "deep leaves a sibling of an up-to-date tracked path alone" "$out" "skills/prod/q"
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
lacks "re-pin leaves another tracked dir's sibling alone" "$out" "skills/prod/q"

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

caller 'Call the Skill tool with `a` to start.'
out="$(run bin/check-integrity)"; rc=$?
eq "a resolvable backticked Skill tool call passes" "$rc" "0"

caller 'Call the Skill tool with `ghost` to start.'
out="$(run bin/check-integrity)"; rc=$?
eq "an unresolved backticked Skill tool call exits 1" "$rc" "1"
has "the backticked call is named" "$out" 'references skill "ghost" (Skill tool call)'
rm -rf "$REPO/user/shared/skills/caller"

echo "bin/check-integrity (template skills)"

tskill() { # tskill <name> <body> — a skill in the fixture template; its
  # frontmatter name deliberately differs from the directory, as upstreams do.
  mkdir -p "$REPO/project-templates/t/.claude/skills/$1"
  printf -- '---\nname: upstream-%s\ndescription: fixture\n---\n%s\n' "$1" "$2" \
    > "$REPO/project-templates/t/.claude/skills/$1/SKILL.md"
}

tskill helper 'body'
tskill main 'Call the Skill tool with "helper", then with "a".'
out="$(run bin/check-integrity)"; rc=$?
eq "a template skill may call a sibling and a user-scope skill" "$rc" "0"
has "template skills are counted" "$out" "Checked 2 skills in project-templates/t/.claude/skills"

tskill main 'Call the Skill tool with "ghost".'
out="$(run bin/check-integrity)"; rc=$?
eq "an unresolved call in a template skill exits 1" "$rc" "1"
has "the template skill is named" "$out" "project-templates/t/.claude/skills/main/SKILL.md"

tskill main 'Open `/about`, then see [the notes](missing.md).'
out="$(run bin/check-integrity --strict)"; rc=$?
eq "template skills skip the frontmatter, /token and link checks" "$rc" "0"

tskill main 'body'
caller 'Call the Skill tool with "helper".'
out="$(run bin/check-integrity)"; rc=$?
eq "a user-scope skill cannot resolve a template's skill" "$rc" "1"
rm -rf "$REPO/user/shared/skills/caller" "$REPO/project-templates"

echo "bin/check-integrity (declarations)"

declare_item() { # declare_item <mcp|plugins> <name> <readme-text>
  mkdir -p "$REPO/user/shared/$1/$2"
  printf '%s\n' "$3" > "$REPO/user/shared/$1/$2/README.md"
}
user_plugins() { printf '{"enabledPlugins": {%s}}\n' "$1" > "$REPO/user/shared/settings.json"; }

user_plugins '"good@market": true'
declare_item mcp srv 'Run: claude mcp add --scope user srv https://example.invalid'
declare_item plugins good 'Run: /plugin install good@market'
out="$(run bin/check-integrity --strict)"; rc=$?
eq "complete declarations pass under --strict" "$rc" "0"
has "declarations are counted" "$out" "Checked 1 plugin and 1 MCP server declarations"

declare_item mcp srv 'No command here.'
out="$(run bin/check-integrity)"; rc=$?
eq "an MCP declaration without its command exits 1" "$rc" "1"
has "the missing MCP command is named" "$out" 'declaration lacks its `claude mcp add` command'
declare_item mcp srv 'Run: claude mcp add --scope user srv https://example.invalid'

declare_item plugins good 'No command here.'
out="$(run bin/check-integrity)"; rc=$?
eq "a plugin declaration without its command exits 1" "$rc" "1"
declare_item plugins good 'Run: claude plugin install good@market'
out="$(run bin/check-integrity)"; rc=$?
eq "the claude plugin install form counts as the command" "$rc" "0"

mkdir -p "$REPO/user/shared/plugins/bare"
out="$(run bin/check-integrity)"; rc=$?
eq "a declaration directory without a README exits 1" "$rc" "1"
rm -rf "$REPO/user/shared/plugins/bare"

declare_item plugins idle 'Run: /plugin install idle@market'
out="$(run bin/check-integrity)"; rc=$?
eq "a declared plugin enabled nowhere only warns" "$rc" "0"
has "the idle plugin is named" "$out" "user/shared/plugins/idle:1  declared plugin is not enabled in any settings.json"
user_plugins '"good@market": true, "idle@market": false'
out="$(run bin/check-integrity --strict)"; rc=$?
eq "an entry set to false does not count as enabled" "$rc" "1"
user_plugins '"good@market": true'
mkdir -p "$REPO/project-templates/t/.claude"
printf '{"enabledPlugins": {"idle@market": true}}\n' > "$REPO/project-templates/t/.claude/settings.json"
out="$(run bin/check-integrity --strict)"; rc=$?
eq "enabling it in a template settles the warning" "$rc" "0"

user_plugins '"good@market": true, "stray@market": true'
out="$(run bin/check-integrity)"; rc=$?
eq "a plugin enabled without a declaration only warns" "$rc" "0"
has "the undeclared plugin is named" "$out" "plugin 'stray' is enabled but not declared"
rm -rf "$REPO/user/shared/plugins" "$REPO/user/shared/mcp" "$REPO/user/shared/settings.json" "$REPO/project-templates"

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

# ----- install.sh and bin/check-machine --------------------------------------
echo "install.sh and bin/check-machine"

cp "$ROOT/install.sh" "$REPO/"
mkdir -p "$REPO/user/shared/commands" "$REPO/user/shared/agents" "$REPO/user/shared/rules" \
  "$REPO/user/shared/output-styles" "$REPO/user/shared/hooks"
printf 'fixture\n' > "$REPO/user/shared/CLAUDE.md"
for os in mac linux; do
  mkdir -p "$REPO/user/$os/hooks"
  printf '#!/bin/sh\n' > "$REPO/user/$os/statusline-command.sh"
  printf '#!/bin/sh\n' > "$REPO/user/$os/subagent-statusline.sh"
done
plugin() { # plugin <name> — a declared plugin, sidecar included
  declare_item plugins "$1" "Run: /plugin install $1@market"
  printf '{"provenance":[{"source":"self","adopted-as":"inspired-by"}]}\n' > "$REPO/user/shared/plugins/$1/.provenance.json"
}
installed() { mkdir -p "$TMP/home/.claude/plugins"; printf '{"version": 2, "plugins": {%s}}\n' "$1" > "$TMP/home/.claude/plugins/installed_plugins.json"; }
registered() { printf '{"mcpServers": {%s}}\n' "$1" > "$TMP/home/.claude.json"; }

user_plugins '"good@market": true'
plugin good
declare_item mcp srv 'Run: claude mcp add --scope user srv https://example.invalid'

out="$(run bin/check-machine)"; rc=$?
eq "a machine with nothing installed exits 1" "$rc" "1"
has "a missing owned path is named" "$out" "~/.claude/settings.json is missing"

run ./install.sh >/dev/null
out="$(run bin/check-machine)"; rc=$?
lacks "install.sh links every owned path" "$out" "is missing"
eq "missing plugins and MCP servers still exit 1" "$rc" "1"
has "an enabled plugin that is not installed is an error" "$out" "plugin good@market is enabled at user scope but not installed"
has "a declared MCP server that is not registered is an error" "$out" "MCP server srv is declared but not registered at user scope"

installed '"good@market": [{"scope": "user"}]'
registered '"srv": {"type": "http", "headers": {"Authorization": "Bearer SECRET-VALUE"}}'
out="$(run bin/check-machine)"; rc=$?
eq "a machine matching the repo exits 0" "$rc" "0"
lacks "a matching machine reports no errors" "$out" "ERRORS"
lacks "secret values never reach the output" "$out" "SECRET-VALUE"
has "uncommitted changes are a warning" "$out" "uncommitted change"
has "a missing upstream branch is a warning" "$out" "no upstream branch is set"
out="$(run bin/check-machine --strict)"; rc=$?
eq "--strict fails on those warnings" "$rc" "1"

installed '"good@market": [{"scope": "user"}], "extra@market": [{"scope": "user"}]'
registered '"srv": {}, "rogue": {}'
out="$(run bin/check-machine)"; rc=$?
eq "undeclared plugins and MCP servers only warn" "$rc" "0"
has "the undeclared plugin is named" "$out" "plugin extra@market is installed but not declared"
has "the undeclared MCP server is named" "$out" "MCP server rogue is registered but not declared"
installed '"good@market": [{"scope": "user"}]'
registered '"srv": {}'

plugin proj
mkdir -p "$REPO/project-templates/t/.claude"
printf '{"enabledPlugins": {"proj@market": true}}\n' > "$REPO/project-templates/t/.claude/settings.json"
out="$(run bin/check-machine)"; rc=$?
eq "a plugin enabled only in a template need not be installed" "$rc" "0"

user_plugins '"good@market": true, "off@market": false'
plugin off
out="$(run bin/check-machine)"; rc=$?
eq "a plugin switched off need not be installed" "$rc" "0"

user_plugins '"good@market": true, "ghost@market": true'
out="$(run bin/check-machine)"; rc=$?
eq "an enabled plugin with no declaration must still be installed" "$rc" "1"
has "the undeclared, uninstalled plugin is named" "$out" "plugin ghost@market is enabled at user scope but not installed"

user_plugins '"good@market": true, "plain@market": true'
declare_item plugins plain 'Run: /plugin install plain@market'
out="$(run bin/check-machine)"; rc=$?
eq "a declaration without a sidecar is still checked" "$rc" "1"
installed '"good@market": [{"scope": "user"}], "plain@market": [{"scope": "user"}]'
out="$(run bin/check-machine)"; rc=$?
eq "once installed, the sidecar-less declaration passes" "$rc" "0"
lacks "and it is not reported as undeclared" "$out" "plugin plain@market is installed but not declared"
installed '"good@market": [{"scope": "user"}]'
rm -rf "$REPO/user/shared/plugins/plain"
user_plugins '"good@market": true'

rm "$TMP/home/.claude/rules"
ln -s "$TMP/elsewhere" "$TMP/home/.claude/rules"
out="$(run bin/check-machine)"; rc=$?
eq "an owned path linked somewhere else exits 1" "$rc" "1"
has "the stray link is named" "$out" "~/.claude/rules points to"
run ./install.sh >/dev/null

mv "$REPO/user/shared/output-styles" "$REPO/user/shared/output-styles.moved"
out="$(run bin/check-machine)"; rc=$?
eq "a link whose target left the repo exits 1" "$rc" "1"
has "the dangling link is named" "$out" "which is missing from this repo"
mv "$REPO/user/shared/output-styles.moved" "$REPO/user/shared/output-styles"

rm "$TMP/home/.claude/CLAUDE.md"
printf 'local copy\n' > "$TMP/home/.claude/CLAUDE.md"
out="$(run bin/check-machine)"; rc=$?
eq "an owned path replaced by a plain file exits 1" "$rc" "1"
has "the replaced path is named" "$out" "~/.claude/CLAUDE.md exists but is not a symlink into this repo"
run ./install.sh >/dev/null

# With everything committed and pushed, the machine is fully reproduced.
git_clean init -q --bare "$TMP/remote.git"
git_clean -C "$REPO" add -A
git_clean -C "$REPO" commit -q -m base
git_clean -C "$REPO" remote add origin "$TMP/remote.git"
git_clean -C "$REPO" push -q -u origin main
out="$(run bin/check-machine --strict)"; rc=$?
eq "a reproduced machine passes --strict" "$rc" "0"
has "a reproduced machine reports Clean" "$out" "Clean."

git_clean -C "$REPO" commit -q --allow-empty -m ahead
out="$(run bin/check-machine)"; rc=$?
eq "an unpushed commit only warns" "$rc" "0"
has "the unpushed commit is counted" "$out" "1 commit not on origin/main"

echo "uninstall.sh"

cp "$ROOT/uninstall.sh" "$REPO/"
printf 'mine\n' > "$TMP/home/.claude/notes.txt"
# $TMP can hold a doubled slash (macOS TMPDIR ends in one), which the link
# targets do not, so match on the normalized path.
repo_path="$(cd "$REPO" && pwd)"
repo_links() { find "$TMP/home/.claude" -maxdepth 2 -type l -lname "$repo_path/*" | wc -l | tr -d ' '; }
eq "before uninstall, every owned path links into the repo" "$(repo_links)" "11"
run ./uninstall.sh >/dev/null
eq "uninstall.sh removes every link into the repo" "$(repo_links)" "0"
if [ -f "$TMP/home/.claude/CLAUDE.md" ] && [ ! -L "$TMP/home/.claude/CLAUDE.md" ]; then
  ok "uninstall.sh restores the file install.sh backed up"
else
  bad "uninstall.sh restores the file install.sh backed up"
fi
if [ -f "$TMP/home/.claude/notes.txt" ]; then ok "uninstall.sh leaves other files alone"; else bad "uninstall.sh leaves other files alone"; fi

# ----- Summary ---------------------------------------------------------------
echo ""
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
