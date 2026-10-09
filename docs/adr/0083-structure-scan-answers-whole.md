# 0083 — 구조 scan의 답 전체를 `lib/structure.py`가 낸다

architecture 리뷰의 두 번째 후보다. ADR 0080은 두 번째 pass만 `lib/structure.py`로 옮겼다. sibling pass는 `bin/adopt`와 `bin/check-updates`에 따로 남았고, 호출자가 sibling pass를 먼저 돌려 그 결과를 넘겨야 두 번째 pass를 쓸 수 있었다. 호출 순서가 interface에 새어 나온 셈이다. 두 사본은 서로 달랐다. `check-updates`는 사라진 항목이 adopt한 것이면 `** adopted here **`를 붙였고 `adopt`는 붙이지 않았다.

이제 "두 commit 사이에 upstream 구조가 어떻게 바뀌었나"를 module이 통째로 답한다. 호출자는 pin이 움직이는 path들과 그 source에서 추적하는 path 전체만 넘긴다. 답은 record의 목록이다. sibling record는 옆에 생긴 것과 사라진 것, 사라진 것 가운데 이 repo가 추적하는 것을 담고, elsewhere record는 다른 곳에 생긴 skill과 plugin을 담는다.

## 바뀐 동작

- `bin/adopt`의 구조 경고가 사라진 항목에 `** adopted here **`를 붙인다.
- sibling pass가 ASCII가 아닌 이름도 그대로 읽는다. 전에는 두 번째 pass만 그랬다.

## test

- `tests/test_structure.py`가 module의 interface를 건넌다. 12개다.
- 가짜 upstream은 `tests/upstream.py` 하나가 만든다. module test는 이것을 import하고 `tests/run.sh`는 script로 실행해 같은 repo를 쓴다.
- 구조 scan의 경우들을 `adopt`와 `check-updates`의 출력으로 각각 확인하던 명령줄 check 10개를 지웠다. 명령줄 쪽에는 두 도구가 답을 제대로 출력하는지만 남겼다.

## Consequences

- `deep.json`의 `structure` record는 모양이 그대로다.
- 삭제 보고나 제외 규칙을 바꿀 때 고칠 곳이 `lib/structure.py` 하나다.
