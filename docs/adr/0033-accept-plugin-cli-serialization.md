# 0033 — Accept the plugin CLI's settings.json serialization order as canonical

`/plugin install` rewrites `user/shared/settings.json` through the `~/.claude/settings.json` symlink, reordering keys without changing any values. Reverting the order would just churn again on the next plugin operation, so the CLI's serialization is committed as-is.
