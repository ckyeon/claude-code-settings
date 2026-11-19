# claude.ai skills

Skills that run on claude.ai and keep their source here. They are declared: this repo holds each skill's source and the steps to upload it, and a person uploads it. claude.ai then syncs the skill back into Claude Code, where it is listed under "claude.ai sync". That is why `install.sh` does not link `claude-ai/skills/` into `~/.claude/skills`: a local link would show the same skill twice.

| Skill | Shares a file with | Upload again when |
|---|---|---|
| `korean-review` | `references/korean-writing.md` is a symlink to `user/shared/rules/korean-writing.md` | its `SKILL.md` or the Korean rule changes |

## Upload a skill

Zip the skill's folder, leaving out its `evals/`:

```bash
cd claude-ai/skills
zip -r ~/Downloads/korean-review.zip korean-review -x 'korean-review/evals/*'
```

`zip` follows symlinks, so a linked file goes into the archive as its contents. Upload the zip in claude.ai under [Customize > Skills](https://claude.ai/customize/skills). The archive holds the skill folder at its root, the layout claude.ai expects.

## Test a skill

Each skill's `evals/` holds test cases in the layout `skill-creator` and `claude plugin eval` read: a prompt, input files, and one grader per expected finding.
