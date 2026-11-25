# 0147 — 2026-11-25 check-integrity가 굵은 글씨와 slash 없는 backtick으로 쓴 skill 참조도 검사

`bin/check-integrity`는 `` `/name` skill ``과 "Skill tool" 근처의 이름만 skill 참조로 읽었다. 그래서 auto-editor skill이 쓰는 `**auto-editor-transitions** skill` 같은 참조는 검사 밖에 있었다. ADR 0145에서 auto-editor 세 항목을 head로 옮길 때 `auto-editor-transitions`를 함께 들이지 않았다면, 세 곳의 참조가 경고 없이 끊겼을 것이다(ADR 0124 후속). 이제 굵은 글씨나 slash 없는 backtick으로 쓴 이름 뒤에 "skill"이라는 명사가 오면 skill 참조로 읽고, 해석되지 않으면 error를 낸다. 기존 `SKILL_REF`와 같이 user scope와 template scope 모두에 적용한다.

## 고려한 방법

- **check-integrity에 패턴 추가** (채택): 결과가 매번 같고, `bin/re-pin`, `bin/adopt`, Stop hook이 이미 이 검사를 돌리므로 re-pin하는 시점에 잡는다. 적용 전 repo에서 두 표기는 16건이었고 모두 설치된 skill로 해석되어 잘못 잡히는 것이 없었다. `auto-editor-transitions`를 지운 복사본에서 끊긴 참조 3곳을 모두 error로 잡는 것을 확인했다.
- **업데이트할 때 upstream skill 이름 목록으로 검사**: 표기와 상관없이 잡지만 `check-updates --deep`과 `bin/re-pin`에서만 돌고, `core`나 `vercel`처럼 짧은 이름이 일반 단어와 겹친다. 표시 없는 표기로 실제로 놓치는 일이 생기면 다시 본다.
- **check-updates subagent 판단에 맡기기**: 이번에는 잡았지만 결과가 매번 같다는 보장이 없다.

## 한계

- 표시 없이 쓴 이름("see the foo skill")은 잡지 않는다. "the follow-up skill" 같은 일반 단어와 구분할 수 없다.
- 한 줄씩 검사하므로 이름과 "skill"이 줄바꿈으로 갈라지면 놓친다. 기존 `SKILL_REF`와 같은 한계다.
- 로컬이 아니라 CLI가 제공하는 skill을 이 표기로 가리키면 error가 난다. 그런 이름을 허용하는 목록은 아직 없다.
