# 0131 — 질문 하나가 결정 하나만 정하게 한다

`user/shared/CLAUDE.md` 1절 "Clarify" 항목에 두 문장을 더했다. 질문 하나는 결정 하나만 정하고, 추천이 서로 독립인 결정 여럿에 걸치면 결정마다 질문을 따로 낸다.

## 경위

- 다른 프로젝트의 세션이 inbox에 남긴 건의(ADR 0098)에서 왔다. grilling 중 질문 하나가 서로 독립인 결정 네 개를 묶었고, 사용자는 그 질문을 포함한 여러 질문을 "승인" 한 번으로 받았다.
- 네 결정 중 하나만 사용자 의도와 달랐다. 그 차이는 배포 뒤에야 드러났고, 되돌리는 commit 세 개와 code review 한 번이 더 생겼다.

## 결정

- **건의가 대상으로 잡은 `grilling` skill은 고치지 않는다.** `grilling`은 `copied` 항목이고 지금 upstream HEAD와 내용이 같다. 로컬 수정이 있으면 `bin/re-pin`이 이 항목을 건너뛰므로, 석 달 동안 일곱 번 re-pin된 이 skill을 매번 손으로 합쳐야 한다. ADR 0110과 같은 판단이다.
- **`user/shared/CLAUDE.md` 1절에 둔다.** 결정을 묶는 문제는 grilling 밖에서 사용자에게 묻는 질문에서도 생긴다.

## Consequences

- grilling 본문의 "Word each question so "yes" accepts your recommended answer."와 이 규칙이 함께 있을 때 실제로 결정마다 질문이 나뉘는지는 확인하지 않았다.
- upstream(mattpocock/skills)에 같은 문장을 건의하는 issue는 내지 않았다. 외부에 글을 올리는 일이라 사용자가 원할 때 한다.
