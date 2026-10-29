# 0107 — mattpocock/skills 27건을 `a496f551`로 re-pin

mattpocock/skills를 `49dd158d`에서 `a496f551`로 올렸다. 내용이 바뀐 8건과 pin만 뒤처진 19건이다. upstream에 새로 생기거나 사라진 skill은 없다.

## 바뀐 내용

- **sub-agent를 새 context window로 시작** (upstream `7739eae`): `code-review`, `codebase-design`, `grilling`, `implement-spec`, `improve-codebase-architecture`, `research`, `wayfinder` 7건이다. sub-agent나 background agent를 띄울 때 부모 대화를 fork하지 말고 새 context window로 시작하라는 문구가 들어갔다. upstream commit은 일부 Codex model이 subagent를 띄울 때 부모 대화를 fork한다는 점을 이유로 든다. Claude Code에도 대화 context를 물려받는 fork가 있으므로 여기서도 뜻이 있다.
- **`implement-spec`** (upstream `a496f55`): ticket마다 새 implementer subagent를 하나씩 띄운다. code review에서 나온 문제도 새 implementer subagent 하나가 고친다.
- **`setup-matt-pocock-skills`** (upstream `ed0de59`, `59db609`):
  - legacy `CONTEXT.md`와 `CONTEXT-MAP.md`가 있으면 `GLOSSARY` 이름으로 `git mv`하자고 제안한다.
  - GitHub나 GitLab tracker를 고르면 그 host를 가리키는 `git remote`가 있어야 다음으로 넘어간다.
  - GitHub template은 blocking 관계에 `gh`의 `--blocked-by` flag를 쓰고, issue를 닫을 때 comment를 먼저 단 다음 닫는다. 이미 닫힌 issue에 `gh issue close --comment`를 쓰면 comment가 사라지고 exit code는 0이기 때문이다.
  - issue는 사용자의 repo에만 만들고 `mattpocock/skills`에는 만들지 않는다. 첫 `gh issue create` 전에 대상 repo를 확인한다.
  - GitLab template은 `glab`의 JSON 출력 flag, child ticket을 map에 연결하는 방법, frontier query를 고쳤다.

`/name` 참조와 Skill tool 호출 문구는 새로 생기거나 사라진 것이 없다. 위임 대상 skill은 모두 `user/shared/skills/`에 있다.

## to-tickets

ADR 0100에서 넣은 local 수정(`4b` 블록) 때문에 `bin/re-pin`이 이 항목에서 멈췄다. 이번 구간에서 upstream의 `to-tickets`는 바뀌지 않았다. `docs/PROVENANCE.md` Edge cases의 절차대로 `--overwrite-local`과 `--notes`를 주어 이 항목만 re-pin하고, HEAD의 `SKILL.md`로 블록을 되돌렸다. 그래서 `SKILL.md`는 그대로이고 sidecar에 entry 하나만 붙었다.

upstream이 sub-agent를 fork 대신 새 context로 띄우도록 바꾼 방향은 `4b` 블록이 "not a fork of this conversation"으로 이미 정한 방향과 같다.
