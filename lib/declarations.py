"""What the repo declares: plugins and MCP servers, and how each gets created.

The one place that says what "declared" and "enabled" mean, and that words
the commands a person runs to create or remove the declared items.
install.sh and uninstall.sh print those words, and bin/check-integrity,
bin/check-machine, and bin/check-updates read the same answers.

Run as a script, it prints the hints for the bash callers:
    python3 lib/declarations.py install-hints|uninstall-hints <repo-root>
"""
import json
import os
import sys


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def declared(repo_root, kind):
    """Names declared under user/shared/<kind>/, one directory each.

    kind is "plugins" or "mcp". A sidecar is not required: a declaration with
    no public upstream is still a declaration.
    """
    d = os.path.join(repo_root, "user", "shared", kind)
    if not os.path.isdir(d):
        return []
    return sorted(n for n in os.listdir(d) if os.path.isdir(os.path.join(d, n)))


def settings_files(repo_root):
    """[(scope, parsed settings)]: user scope first, then each project template."""
    found = [("user", _load(os.path.join(repo_root, "user", "shared", "settings.json")))]
    templates = os.path.join(repo_root, "project-templates")
    if os.path.isdir(templates):
        for t in sorted(os.listdir(templates)):
            found.append(("project", _load(os.path.join(templates, t, ".claude", "settings.json"))))
    return found


def plugin_entries(repo_root):
    """name -> (marketplace, scope), from every enabledPlugins key.

    Keys are "<name>@<marketplace>". scope is "user" or "project" where the
    plugin is switched on, and "" when every entry for it is false: the
    marketplace is still known, but nothing enables the plugin. User scope
    wins over a template, and an entry that is on wins over one that is off.
    """
    entries = {}
    for scope, settings in settings_files(repo_root):
        for key, on in (settings.get("enabledPlugins") or {}).items():
            name, _, marketplace = key.partition("@")
            current = entries.get(name)
            if on and (current is None or not current[1]):
                entries[name] = (marketplace, scope)
            elif current is None:
                entries[name] = (marketplace, "")
    return entries


def marketplace_sources(repo_root):
    """marketplace -> its repo or url, from extraKnownMarketplaces. User scope wins.

    A built-in marketplace has no entry, since it needs no `marketplace add`.
    """
    sources = {}
    for _scope, settings in settings_files(repo_root):
        for name, spec in (settings.get("extraKnownMarketplaces") or {}).items():
            source = (spec or {}).get("source") or {}
            sources.setdefault(name, source.get("repo") or source.get("url") or "")
    return sources


def plugin_rows(repo_root):
    """[(name, marketplace, source, scope)] for every declared plugin.

    marketplace is empty when no settings file mentions the plugin, and source
    is empty for a built-in marketplace. Built-in marketplaces sort first,
    then third-party ones, then plugins with no known marketplace, so one
    `marketplace add` line can head each group.
    """
    entries = plugin_entries(repo_root)
    sources = marketplace_sources(repo_root)
    rows = []
    for name in declared(repo_root, "plugins"):
        marketplace, scope = entries.get(name, ("", ""))
        rows.append((name, marketplace, sources.get(marketplace, "") if marketplace else "", scope))
    rows.sort(key=lambda r: (2 if not r[1] else 1 if r[2] else 0, r[1], r[0]))
    return rows


def install_hints(repo_root):
    """The lines telling a person what to run to create each declared item."""
    lines = []
    rows = plugin_rows(repo_root)
    if rows:
        lines += ["", "Declared plugins (NOT installed by this script — see user/shared/plugins/):",
                  "", "Inside a Claude Code session, run:"]
        previous = None
        for name, marketplace, source, scope in rows:
            if marketplace != previous:
                lines.append("")
                if not marketplace:
                    lines.append("  # No settings.json enables these — add them to enabledPlugins, or install by hand:")
                elif source:
                    lines.append(f"  # {marketplace} (third-party marketplace — add it before installing)")
                    lines.append(f"  /plugin marketplace add {source}")
                else:
                    lines.append(f"  # {marketplace} (built-in marketplace — no 'marketplace add' needed)")
                previous = marketplace
            if not marketplace:
                lines.append(f"  #   - {name}")
            elif scope == "project":
                lines.append(f"  /plugin install {name}@{marketplace}   "
                             f"# project-scope only (see user/shared/plugins/{name}/README.md)")
            else:
                lines.append(f"  /plugin install {name}@{marketplace}")
    servers = declared(repo_root, "mcp")
    if servers:
        lines += ["", "Declared MCP servers (NOT registered by this script — see user/shared/mcp/):"]
        lines += [f"  - {name}" for name in servers]
        lines += ["", "For each, open user/shared/mcp/<name>/README.md and run the registration",
                  "command shown there (typically: claude mcp add --scope user ...)."]
    return lines


def uninstall_hints(repo_root):
    """The lines telling a person what to run to remove each declared item."""
    lines = []
    rows = plugin_rows(repo_root)
    if rows:
        lines += ["", "Declared plugins detected (this script does NOT remove Claude Code-installed plugins):",
                  "", "To remove them, run in a Claude Code session:"]
        for name, marketplace, _source, _scope in rows:
            if marketplace:
                lines.append(f"  /plugin uninstall {name}@{marketplace}")
            else:
                lines.append(f"  # {name} — marketplace unknown; check user/shared/plugins/{name}/README.md")
    servers = declared(repo_root, "mcp")
    if servers:
        lines += ["", "Declared MCP servers detected (this script does NOT remove registered MCP servers):"]
        lines += [f"  - {name}" for name in servers]
        lines += ["", "To remove them, run:",
                  "  claude mcp remove <name> -s user          # per server above"]
    return lines


if __name__ == "__main__":
    hints = {"install-hints": install_hints, "uninstall-hints": uninstall_hints}
    if len(sys.argv) != 3 or sys.argv[1] not in hints:
        sys.exit("usage: declarations.py install-hints|uninstall-hints <repo-root>")
    for line in hints[sys.argv[1]](sys.argv[2]):
        print(line)
