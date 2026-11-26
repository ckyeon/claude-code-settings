# claude.ai skills

Skills that run on claude.ai and keep their source here. They are declared: this repo holds each skill's source and the steps to upload it, and a person uploads it. claude.ai then syncs the skill back into Claude Code, where it is listed under "claude.ai sync". That is why `install.sh` does not link `claude-ai/skills/` into `~/.claude/skills`: a local link would show the same skill twice.

| Skill | Copies content from | Upload again when |
|---|---|---|
| `korean-review` | `SKILL.md` § "한국어 글쓰기 규칙" is a copy of `user/shared/rules/korean-writing.md`, trimmed for reviewing | its `SKILL.md` changes |

A copy does not follow its source. When `user/shared/rules/korean-writing.md` changes, make the same change in the skill's copy, then upload the skill again. `claude-ai/copies.json` declares the copy and where it differs from its source, as trimmed or reworded text, and `bin/check-integrity` fails when the copy no longer equals its source with those differences applied. To trim or reword more in a copy, add the difference there.

## Upload a skill

Zip the skill's folder, leaving out its `evals/`:

```bash
cd claude-ai/skills
zip -r ~/Downloads/korean-review.zip korean-review -x 'korean-review/evals/*'
```

Upload the zip in claude.ai under [Customize > Skills](https://claude.ai/customize/skills). The archive holds the skill folder at its root, the layout claude.ai expects.

Once a Claude Code session has synced it, `bin/check-machine` compares the synced copy under `~/.claude/skills/synced/` with the source here. A declared skill that has not synced is an error. A synced copy that differs is a warning to upload again.

## Test a skill

Each skill's `evals/` holds test cases in the layout `skill-creator` and `claude plugin eval` read: a prompt, input files, and one grader per expected finding.
