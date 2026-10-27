# 0100 — to-tickets는 publish 전에 fresh context의 subagent가 ticket 초안을 리뷰한다

`to-tickets`의 4단계와 5단계 사이에 `4b` 단계를 넣었다. 사용자가 분할을 승인하면 초안을 파일로 쓰고, 대화를 물려받지 않은 subagent가 그 초안을 리뷰한 뒤에 publish한다. 이 수정은 upstream에 없으므로, 이 repo가 `copied` 항목에 의도한 local 수정을 남기는 첫 사례이고 그 기록 방식도 함께 정한다.

## 경위

- 다른 프로젝트의 세션이 남긴 건의(ADR 0098)에서 왔다. 그 세션에서는 초안을 쓴 agent가 같은 context에서 세 번 리뷰했지만 문제를 찾지 못했다. 대화를 모르는 subagent는 같은 초안에서 다섯 종류의 빈틈을 찾았다.
  - ticket이 가리키는 repo 상태가 commit되지 않았다.
  - 다른 ticket이 만드는 것을 쓰는데, 그 ticket이 blocker에 없었다.
  - spec이 요구하는 경로를 맡은 ticket이 없었다.
  - ticket에 외부 API의 기본 동작이 빠져 있었다.
  - 앞 ticket이 정하는 규약을 뒤 ticket이 읽을 곳에 적게 하는 완료 기준이 없었다.
- 초안을 쓴 agent의 context에는 ticket에 빠진 지식이 이미 있다. 그래서 그 agent가 읽으면 ticket이 완결돼 보인다.

## 결정

- **리뷰는 ticket 수와 상관없이 매번 돌린다.** 조건을 두면, 리뷰가 필요한지 판단하는 쪽이 대화의 지식을 다 가진 agent가 된다.
- **subagent는 fork가 아니어야 한다.** Claude Code의 fork는 대화 context를 물려받으므로, 문안에 "not a fork of this conversation"을 적었다. 건의 문안에서 뜻이 바뀐 곳은 이 문장 하나다. 문구만 다듬은 세 곳은 ADR 0101에 적었다.
- **발견은 must-fix, should-fix, nit로 나눈다.** `to-tickets`에서 blocker는 막는 ticket을 뜻하므로 그 말을 쓰지 않는다. must-fix는 모두 고치고, should-fix는 목록 하나로 만들어 사용자에게 묻는다.
- **수정은 블록 하나로 넣는다.** 번호를 `4b`로 두어 upstream의 `### 5.` 줄을 건드리지 않고, 리뷰 prompt도 그 블록 안에 둔다. 그러면 re-pin한 뒤 다시 넣을 곳이 하나가 된다.
- **`copied`를 유지한다.** 블록 하나는 `docs/PROVENANCE.md`의 정의 "with at most minor edits"에 들어가는 크기로 본다. 같은 문서의 "When in doubt, prefer `inspired-by`"는 출처 표시 기준을 낮추라는 말인데, 이 항목은 내용 대부분이 upstream 그대로라 출처가 분명하다. `inspired-by`로 바꾸면 re-pin이 내용을 받지 않으므로 upstream 변경을 매번 손으로 옮겨야 한다. `source: "self"` entry를 넣으면 `lib/sidecars.py`가 항목을 "no longer tracked"로 다루어 `check-updates`가 upstream 변경을 알리지 않는다.
- **기록은 세 곳에 둔다.** sidecar에 손으로 추가한 entry의 `notes`, 이 ADR, `docs/PROVENANCE.md` Edge cases 표의 한 줄이다. re-pin 절차는 PROVENANCE.md 표에만 적고, 나머지 두 곳은 그곳을 가리킨다.
- **이 항목은 `bin/re-pin`으로만 옮긴다.** ADR 0085 이후 `bin/re-pin`은 local 사본이 옛 pin과 다르면, 의도한 수정인지와 상관없이 덮어쓰지 않고 멈춘다. ADR 0008의 "Local edits to a `copied` item are erased on the next re-adoption"은 `bin/adopt`로 다시 들일 때 여전히 맞다. `bin/adopt`는 검사 없이 덮어쓴다.

## Considered Options

- **upstream에 제안**: mattpocock/skills #633과 #1051이 같은 취지의 구현 전 리뷰를 NOT_PLANNED로 닫았다. #633의 답은 "You can get an independent review by handing the spec to a fresh session yourself"다.
- **publish 뒤에 따로 돌리는 리뷰 skill**: 5단계가 `ready-for-agent` label을 붙여 publish하므로, 리뷰가 끝나기 전에 구현 agent가 ticket을 가져갈 수 있다.
- **ticket template에 인계 절을 넣는 안**: 구현 단계에는 인계를 쓸 시점이 없다. `implement`는 "Commit your work to the current branch."로 끝나고, `implement-spec`의 구현 subagent는 `implement`가 아니라 `tdd`를 부른다. 다음 ticket에 넘길 것은 모든 ticket을 본 쪽이 정해야 하므로 리뷰 prompt의 4번이 맡는다.

## Consequences

- `to-tickets`를 실행할 때마다 subagent 리뷰가 한 번 돌고, ticket이 기대는 외부 문서도 읽는다. ticket이 많으면 token 비용이 크다.
- upstream이 `to-tickets`를 바꿀 때마다 PROVENANCE.md의 절차대로 블록을 손으로 다시 넣어야 한다. 여러 항목을 한꺼번에 re-pin하면 이 항목은 매번 실패로 나온다.
- 열린 PR mattpocock/skills#1226은 5단계의 "Do NOT close or modify any parent issue." 한 줄만 바꾸므로 넣은 블록과 겹치지 않는다.
