# 0071 — mattpocock/skills 24건을 `49dd158d`로 재pin하고 `implement-spec`, `pr`, `retro`를 adopt

ADR 0069에서 미뤄 둔 mattpocock/skills를 `959a8e9f`에서 `49dd158d`로 올렸다. 내용이 바뀐 17건과 pin만 뒤처진 7건을 재pin했고, upstream이 `skills/engineering`으로 승격한 신규 skill 3개를 adopt했다. 새 `ask-matt`가 세 skill을 주 흐름에서 안내하므로 함께 들였다.

## 실질 변경 요약

- **`CONTEXT.md`를 `GLOSSARY.md`로 rename** (upstream `006a52b`): `ask-matt`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `improve-codebase-architecture`, `setup-matt-pocock-skills`, `tdd`, `triage`, `wait-what` 9건이 이제 `GLOSSARY.md`와 `GLOSSARY-MAP.md`만 찾는다. `domain-modeling/CONTEXT-FORMAT.md`는 `GLOSSARY-FORMAT.md`가 됐다. 직접 작성한 `craft-goal`의 참조도 `GLOSSARY.md`로 맞췄다.
- **`ask-matt`**: `/implement-spec`, `/pr`, `/retro`를 안내하고 `/resolving-merge-conflicts`를 뺐다.
- **`setup-matt-pocock-skills`, `to-tickets`**: tracker seed에 sub-issue 작업이 생겼고, `to-tickets`는 원본 issue가 있으면 ticket을 그 sub-issue로 만든다.
- **`implement`**: ticket 참조를 받으면 tracker에서 가져와 제목을 먼저 말한다. `tdd`와 `code-review` 호출이 Skill tool 표기로 바뀌었다.
- **`code-review`, `wayfinder`, `diagnosing-bugs`, `tdd`, `grilling`, `handoff`, `teach`, `wizard`**: 절차를 다듬은 작은 변경이다.

## 신규 skill

- **`implement-spec`**: spec 전체를 한 번에 구현한다. worktree마다 implementer subagent를 돌리고 integration branch 하나에 합친다. 사용자가 호출할 때만 동작한다.
- **`retro`**: session을 회고해 agent 환경의 개선안을 낸다. 사용자가 호출할 때만 동작한다.
- **`pr`**: PR 본문을 쓸 때 model이 스스로 호출한다. frontmatter가 Humanlayer의 `show-me` skill을 출처로 밝힌다.
- `skills/in-progress/chief-of-staff`는 upstream이 beta로 분류해 들이지 않았다.

## 프로젝트의 용어집 파일 이름

`~/workspace`에서 `CONTEXT.md`를 쓰던 프로젝트는 8개였다. 개인 프로젝트 5개(`discord`, `newsletter`, `time-prototype-plan-layout`, `toego`, `world-agent`)는 같은 날 각 프로젝트의 agent가 파일을 `GLOSSARY.md`로 rename하고 현재 문서의 참조를 고쳤다. ADR, log, `.scratch/`는 기록이므로 그대로 두었다. 그 변경은 각 repo에서 따로 commit한다.

## 미결

- **`resolving-merge-conflicts`**: upstream이 `daa01d8`에서 대체 없이 삭제했다. local 사본은 `959a8e9f` pin 그대로 남아 있고, `check-updates`는 이 항목 때문에 mattpocock/skills를 계속 outdated로 보고한다. 삭제할지 남길지는 따로 정한다.
- **GiverGround 조직 repo 3개**: `gigr/phaser-template`, `gigr/playable-phaser-nhn-shinmatgo-falling`, `gigr/playable-phaser-template`은 팀과 함께 쓰는 repo라 옮기지 않았다. `gigr/phaser-template`은 source code와 test도 `CONTEXT.md`를 가리킨다.

## Consequences

- `user/shared/skills`는 `~/.claude/skills`로 symlink되어 있어 이 변경은 commit 전에도 모든 session에 적용된다.
- 파일 이름을 바꾸지 않은 프로젝트에서 `/domain-modeling`이나 `/grill-with-docs`를 돌리면 기존 `CONTEXT.md` 옆에 `GLOSSARY.md`가 새로 만들어질 수 있다. `domain-modeling`이 `GLOSSARY.md`가 없으면 첫 용어를 확정할 때 만들기 때문이다.
- `pr`이 user scope에 들어와 모든 프로젝트의 PR 본문 작성에 적용된다.
- 재adopt 전 local 사본은 모두 pin과 같았으므로 덮어쓴 local 수정은 없다.
