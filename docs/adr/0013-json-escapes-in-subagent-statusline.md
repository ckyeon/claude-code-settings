# Use JSON escapes, not shell escapes, for colors in the sub-agent status line

`user/{mac,linux}/subagent-statusline.sh` defined its ANSI colors as `\033[…m` and
emitted them verbatim into the JSON it prints. `\0` is not a legal JSON escape, so
every line the script produced was invalid JSON and the sub-agent status line never
rendered on any machine. Switch the definitions to `\u001b[…m`, which JSON decodes to
a real ESC byte.

## Context

Found while diagnosing a separate report that the main status line was blank on the
Linux/WSL machine. That turned out to be a missing `jq` (installed by the user, no
repo change). Validating the fix surfaced this second, independent defect:

```
$ … | bash ~/.claude/subagent-statusline.sh | python3 -c "json.loads(…)"
INVALID JSON: Invalid \escape: line 1 column 23
```

The colors were single-quoted, so the shell left `\033` as four literal characters,
and the final `printf '%s'` did not expand them either. Both copies of the script are
byte-identical, so the breakage was never platform-specific — it affected macOS too.

## Considered Options

- **`\u001b` literals** (chosen) — two lines per file, no new dependency, and strictly
  valid JSON.
- **`$'\033[32m'`** — emits a raw ESC byte. Lenient parsers accept it, but raw control
  characters in a JSON string violate the grammar, so this trades one latent bug for
  another.
- **Generate the JSON with `python3 -c json.dumps`** — also fixes the unescaped `name`
  interpolation (below), but rewrites the script. Deferred as out of scope.

## Consequences

- The sub-agent status line renders for the first time. Verified by parsing the output
  with `json.loads` and confirming `\u001b` decodes to `\x1b`.
- **Known limitation, unchanged:** the final `printf '{"id":"%s","content":"%s"}'`
  interpolates `name` without escaping, so a task name containing `"` or `\` still
  produces invalid JSON. Fixing that requires the `json.dumps` rewrite above.
- The script still depends on `jq` and `bc`, which conflicts with the repo's
  "Python 3 stdlib + bash 3.2 only" guardrail. Tracked as a separate decision.

## References

- [[0003-adr-for-every-change]]
