# 0042 — ask-matt와 그 라우팅 대상 12개를 mattpocock/skills@6654f6b6에서 채택

`ask-matt`는 그 repo 스킬 24개로 안내하는 라우터라, 라우팅 대상이 없으면 미해결 참조가 integrity 에러로 남는다. upstream에서 transitive closure를 계산하니 미채택은 정확히 12개였고(implement → code-review는 그 안, code-review/wayfinder → setup-matt-pocock-skills는 기채택) 더 끌려오는 의존성은 없어 13개를 한 번에 채택했다: implement, code-review, wayfinder, research, resolving-merge-conflicts, wizard, handoff, grill-me, to-questionnaire, wait-what, teach, writing-for-agents, ask-matt. user-scope 스킬은 13 → 26. 부분 채택은 라우터의 미해결 참조가 Stop hook에 계속 걸리고, 라우터를 로컬에서 잘라내면 `copied` 재동기화 때 되돌아가서 택하지 않았다.

## Consequences

- `code-review`는 Claude Code 내장 `/code-review`와 이름이 같다. 공식 문서(skills § Where skills live) 기준 user-scope 스킬이 번들 스킬을 조용히 대체하며, 번들은 alias `/review`로만 호출된다. 즉 `/code-review` = Matt 버전(Standards + Spec), `/review` = 내장.
- ADR 0037/0039 이전에 검토되지 않았던 "최초 pin → HEAD" 구간의 신규 스킬 감사(2026-09-02)에서 나온 후속 조치다. closure 밖 12개(in-progress/·misc/ 등)는 의도적으로 미채택.
