# 0101 — ADR 0099와 ADR 0100 리뷰에서 나온 수정

`2704aa5` 이후의 변경, 곧 ADR 0099와 ADR 0100을 Standards와 Spec 두 축으로 리뷰하고 그 결과를 반영했다. 가장 큰 수정은 ADR 0100이 ADR 0008의 범위를 잘못 좁힌 것이다. `bin/adopt`로 다시 들이면 local 수정이 검사 없이 지워지므로, local 수정을 둔 항목은 `bin/re-pin`으로만 옮긴다고 고쳤다.

## 고친 것

- **local 수정을 둔 `copied` 항목** (ADR 0100)
  - `bin/re-pin`은 의도한 수정인지와 상관없이 local 차이가 있으면 멈추고, `bin/adopt`는 검사 없이 덮어쓴다. 이 사실을 ADR 0100과 PROVENANCE.md 표에 그대로 적었다.
  - re-pin 절차는 PROVENANCE.md 표 한 곳에만 두고, sidecar `notes`와 ADR 0100은 그곳을 가리키게 했다. 블록은 덮어쓰기 전 파일(`git show HEAD:<path>`)에서 다시 넣는다.
  - CLAUDE.md의 Re-pin 절에 sidecar `notes`와 PROVENANCE.md § Edge cases를 가리키는 문장을 넣었다. `bin/re-pin`과 `check-updates`는 `notes`를 출력하지 않아서, CLAUDE.md만 따르는 agent는 블록을 덮어쓸 수 있었다.
  - sidecar의 `notes`를 2026-10-09 entry에서 떼고, 같은 commit에 `adopted-at`이 2026-10-28인 entry를 손으로 추가해 거기에 달았다. `adopted-at`은 entry를 기록한 날이므로, 10-09 entry가 그 뒤에 생긴 수정을 설명하면 안 된다.
  - ADR 0100에 PROVENANCE.md의 "When in doubt, prefer `inspired-by`"를 다루는 문장을 넣었다.
- **4b 블록 문구**: 뜻은 그대로 두고 세 곳을 고쳤다.
  - must-fix와 should-fix의 정의를 괄호 안 문장으로 넣던 것을 when 절로 바꿨다.
  - "lean on it"을 "depend on it"으로 바꿨다.
  - "take any fix that needs a commit or push to the user"는 "push to the user"로 읽힐 수 있어서 "Ask the user before any fix that needs a commit or push."로 바꿨다.
- **ADR 0098**: 요약의 과거형 "바로 바뀌었다"를 "바로 바뀐다"로 바꿨다. 직접 수정 경로는 지금도 있다.
- **ADR 0099의 기록**
  - 처리 절차는 버린 건의뿐 아니라 모든 건의에 이유를 말하게 한다. 그렇게 고쳐 적었다.
  - skill 1단계에 새로 생긴 trigger와 "남은 일" 절의 이름 변경을 적었다.
  - "테스트"와 "모듈"을 다른 ADR이 쓰는 "test"와 "module"로 맞췄다. 실행 경로를 뜻하던 "경로"는 파일 경로와 구별하려고 "분기"로 바꿨다.
- **inbox가 범위 밖인 근거**: ADR 0099는 CLAUDE.md § Scope 규칙 3을 "Claude가 쓰는 상태"라고 따옴표 안에 적었지만, 원문은 "State that Claude Code or the account writes"이고 inbox는 `bin/suggest-setting`이 쓴다. 근거를 README § Scope가 이미 범위 밖으로 둔 Memory("per-machine working state")와 같은 기기별 작업 상태라는 것으로 바꾸고, GLOSSARY와 ADR 0099를 함께 고쳤다.
- **ADR 0100 문장**: "ticket이 외부 API의 기본 동작을 몰랐다"는 무생물 주어에 인식 동사를 쓴 번역투여서 "ticket에 외부 API의 기본 동작이 빠져 있었다"로 바꿨다.
- **`SOURCES.md`**: sidecar entry가 늘어 다시 만들었다. ADR 0092 때 반영되지 않았던 `user/shared/CLAUDE.md`의 2026-10-15 self entry도 함께 들어갔다.

## 고치지 않은 것

- **`bin/adopt`에 local 수정 검사를 넣지 않았다.** CLAUDE.md는 이미 "`bin/adopt` records an item for the first time, and `bin/re-pin` moves the pin of one already recorded."라고 두 도구의 역할을 나눈다. 이번에는 문서에 적는 데서 그치고, `bin/adopt`로 기존 항목을 다시 들이는 일이 실제로 생기면 도구를 고친다.
- **`ea25262`의 commit 메시지**는 "give a reason for a dropped suggestion"이라고 적었다. commit을 다시 쓰지 않으려고 그대로 두었고, 정확한 내용은 ADR 0099에 있다.
