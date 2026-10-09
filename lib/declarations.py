"""What the repo declares: plugins and MCP servers, and where plugins are enabled.

lib/common.sh, bin/check-integrity, and bin/check-machine all read these, so
the three agree on what "declared" and "enabled" mean.
"""
import json
import os


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
