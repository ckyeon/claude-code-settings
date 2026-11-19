# 0127 — check-machine이 claude.ai skill의 동기화된 사본을 repo 원본과 비교한다

[[0126-korean-writing-rule-and-review-skill]]은 `claude-ai/skills/`의 skill을 claude.ai에 다시 올리는 것을 잊어도 잡는 검사가 없다고 기록했다. `bin/check-machine`이 `~/.claude/skills/synced/` 아래의 사본을 찾아 repo의 원본과 바이트 단위로 비교하게 했다.

## 판정

- 선언한 skill이 동기화되지 않았으면 error다. 선언한 MCP server가 등록되지 않았을 때와 같은 기준이다. 올리지 않은 skill이 있는 기기는 재현된 기기가 아니다.
- 동기화된 사본이 원본과 다르면 warning이다. 올린 직후에도 Claude Code는 세션 중 약 10분, 쉬는 동안 약 40분마다 변경을 확인하므로(code.claude.com/docs/en/skills, "Where synced skills load") 잠시 다를 수 있다.
- 원본의 symlink가 끊겼으면 error다. 비교하려면 파일을 읽어야 하므로 이 경우를 따로 다룬다.

## 비교 방법

- upload zip과 같은 범위를 본다. symlink를 따라가고, `evals/`와 `.DS_Store`는 뺀다.
- 원본에 있는 파일만 비교한다. claude.ai가 사본에 다른 파일을 더해도 차이로 보지 않는다.
- `synced/` 아래 계정별 폴더 이름은 문서에 없어서 `synced/*/<name>/`으로 찾는다. 사본이 여럿이면 하나라도 같을 때 통과한다.

## Consequences

- 2026-11-19에 `korean-review`를 처음 올려 확인했다. claude.ai는 올린 파일을 바이트 그대로 내려준다. 동기화된 사본에는 `SKILL.md`와 `references/korean-writing.md`만 있었고, 둘 다 repo 원본과 같았다. check-machine도 error와 warning 없이 통과했다.
- `syncClaudeAiSkills`를 끈 기기에서는 선언한 claude.ai skill마다 error가 난다. 이 repo의 settings 파일은 이 값을 쓰지 않으므로, 기기의 `settings.local.json`이 끄지 않는 한 동기화가 켜져 있다.
- `tests/run.sh`에 시험 7개를 더했다.
