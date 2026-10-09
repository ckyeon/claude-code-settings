# 0085 — `bin/re-pin`을 두고, 비교 대상을 정하는 일을 한 곳에 모은다

architecture 리뷰의 세 번째 후보다. re-pin은 이 repo에서 가장 자주 하는 일인데(ADR 0055에서 42건, 0069에서 26건, 0071에서 24건) interface가 일보다 컸다. `bin/adopt`에 `--from`, `--commit`, `--path`, `--to`, `--mode`, `--license`를 넘겨야 했고, 그중 다섯은 sidecar에 이미 적혀 있었다. 항목마다 clone을 따로 해서 2026-10-09에는 mattpocock/skills를 27번 clone했다.

비교 대상을 아는 것은 `bin/check-updates`뿐이었다. ADR 0065는 `bin/adopt`가 `track`을 읽지 않는다고 정했고, 그래서 `track`을 둔 항목을 `--commit` 없이 옮기면 경고 없이 HEAD로 갔다.

## 결정

- **`bin/re-pin <항목>...`을 둔다.** 옮길 항목을 local 경로로 받는다. source, path, mode, license는 sidecar의 현재 pin에서 읽는다. `bin/adopt`는 항목을 처음 들일 때 쓴다.
- **commit을 주지 않으면 비교 대상으로 간다.** 비교 대상을 정하는 logic을 `bin/check-updates`에서 `lib/targets.py`로 꺼냈다. `check-updates`가 "뒤처졌다"고 판단한 지점과 `re-pin`이 가는 지점이 같은 답이다. 이것으로 ADR 0065의 "`bin/adopt`는 `track`을 읽지 않는다"가 바뀐다. 비교 대상을 찾지 못한 항목은 HEAD로 대신 가지 않고 실패한다.
- **덮어쓰기 전에 local 사본을 옛 pin과 비교한다.** 내용을 복사해 온 항목은 re-pin하면 local 사본이 통째로 바뀐다. 지금까지는 "local 수정이 없는가"를 사람이나 agent가 매번 확인했다(ADR 0031, 0063, 0069, 0071). 이제 도구가 옛 pin의 upstream 내용과 비교하고, 다르면 그 항목을 두고 무엇이 다른지 알린다. `--overwrite-local`을 줘야 덮어쓴다. git이 무시하는 파일은 사본의 일부로 보지 않는다.
- **항목마다 결과를 따로 낸다.** 한 항목의 실패가 다른 항목을 막지 않고, 하나라도 실패하면 종료 code가 1이다. `SOURCES.md` 갱신과 `check-integrity`는 끝에 한 번 돈다.
- **source마다 한 번 clone하고 구조 변화도 한 번 알린다.**
- **clone, 복사, 정리, entry 추가를 `lib/adoption.py`에 둔다.** `bin/adopt`와 `bin/re-pin`이 같은 code를 쓴다. `bin/adopt`가 bash로 하던 sparse checkout과 복사가 이 module로 옮겨졌다.
- **trailer는 항목 하나를 처음 adopt하는 commit에만 쓴다.** re-pin은 여러 source에 걸칠 수 있고, 어느 source의 어느 시점인지는 sidecar에 남는다. `bin/re-pin`은 commit 안내를 출력하지 않는다.

## Considered Options

- **`bin/adopt`의 인자를 생략 가능하게 하기**: 기각했다. sidecar가 있으면 선택이고 없으면 필수인 인자가 다섯 개 생겨 interface가 더 복잡해진다. 용어집도 adopt와 re-pin을 다른 일로 구분한다.
- **"뒤처진 것 전부"를 옮기는 옵션**: 만들지 않았다. 검토하지 않은 항목까지 한꺼번에 옮겨지는 길을 열지 않기 위해서다.
- **built-in marketplace의 주소를 환경 변수로 바꾸기**: `lib/targets.py`가 주소 목록을 인자로 받게 했다. test는 `file://` 주소를 넣는다.

## Consequences

- `bin/adopt`를 기존 항목에 다시 돌리는 방식은 계속 동작한다. `track`이 있는 항목에 `--commit` 없이 불리면 `bin/re-pin`을 안내하는 경고를 낸다.
- `bin/adopt`가 환경 변수 `TMPDIR`을 덮어쓰던 것이 없어졌다.
- test는 `tests/test_targets.py` 9개와 `tests/test_adoption.py` 26개다. adoption 쪽은 module을 네 군데 고쳐서 해당 test가 실패하는 것을 확인했다. 명령줄 test에는 `bin/re-pin`의 흐름과 파일 하나짜리 항목의 adopt를 추가했다.
- 실제 upstream으로는 repo의 사본에서 확인했다. 8개 항목, 2개 source를 23초에 처리했고, release를 따르는 `herdr`와 marketplace를 따르는 `hyperframes`는 이미 비교 대상에 있다고 답했다.
- 여러 source를 가진 항목은 source마다 pin이 따로 움직이는데, 결과는 항목 하나에 하나만 보고된다. 그런 항목은 지금 없다.
