# 0035 — Close the 2026-08-31 migration runbook as executed

The new-machine restore (runbook §4) completed on 2026-09-01 with four deviations worth keeping: staged history-merge instead of a plain tar extract (preserves the restore session's own history), a `brew install uv node` prerequisite for the stdio MCP servers, personal preferences folded into the managed settings.json instead of ad-hoc `/config` (ADR 0032), and upstream-verified registration docs for context7/github (ADR 0031, 0034). §7 of the runbook records these; the runbook is now closed.
