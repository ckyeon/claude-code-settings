# 0082 — sidecar를 읽고 쓰고 검증하는 일을 `lib/sidecars.py` 한 곳에 둔다

2026-10-10 architecture 리뷰의 첫 후보다. sidecar를 다섯 곳이 각자 읽고 있었다. `bin/check-updates`, `bin/sources-index`, `bin/check-integrity`, `lib/structure.py`, `bin/adopt`다. 쓰기는 `lib/provenance.sh`에, 검증은 `bin/check-integrity` 안에 있었다. 읽는 곳마다 뜻이 달랐다.

- **현재 pin**: `check-updates`는 마지막 entry를, `adopt`는 source가 같은 것 중 가장 새 entry를 썼다.
- **tracked path**: `check-updates`는 각 항목의 마지막 entry의 path를, `lib/structure.py`는 지난 entry까지 모든 path를 썼다.
- **source의 비교**: `check-updates`는 URL을 글자 그대로 비교했다. sidecar 4개는 같은 repo가 `.git`이 붙은 것과 안 붙은 것 두 가지로 적혀 있다.

## 결정

- **현재 pin은 source마다 가장 새 entry다.** source는 끝의 `.git`과 `/`를 떼고 비교한다. 가장 새 entry가 `self`인 항목은 upstream과 갈라선 것이므로 pin이 없다.
- **tracked path는 현재 pin의 path다.** upstream이 skill을 옮겨 이 repo가 새 path를 따라갔다면 옛 path는 더는 지켜보는 경로가 아니다.
- **읽기, entry 추가, 검증을 `lib/sidecars.py`가 맡는다.** sidecar가 어디 있고 어느 항목을 설명하는지, 필드 이름과 필수 항목이 무엇인지 아는 곳이 하나가 된다. `lib/provenance.sh`는 없앴다.
- **읽지 못한 sidecar는 함께 돌려준다.** `check-updates`와 구조 scan은 지금까지 깨진 sidecar를 말없이 건너뛰어서 그 항목이 점검에서 조용히 빠졌다. 이제 도구가 한 줄 경고를 내고 계속한다. 오류로 판정하는 일은 그대로 `check-integrity`가 한다.
- **module은 `unittest`로 직접 test한다.** `tests/test_sidecars.py`의 20개가 module의 interface를 건넌다. `tests/run.sh`가 이것까지 함께 돌린다. sidecar 검증의 세부를 명령줄 출력으로 확인하던 check 하나는 지우고, 도구가 오류로 끝나는지만 남겼다.

## Consequences

- 지금 있는 sidecar 90개에서는 판정이 달라지지 않는다. 서로 다른 upstream 둘을 가진 항목과 upstream path가 중간에 바뀐 항목이 없기 때문이다.
- `SOURCES.md`와 `check-integrity`의 출력은 고치기 전과 같다. `check-updates`의 fast 출력은 한 source에 속한 항목 이름의 순서만 달라졌다. 전에는 파일 시스템이 돌려주는 순서였고 이제는 경로순이다.
- `SOURCES.md`의 "By source"는 여전히 URL을 적힌 그대로 묶는다. 출력을 바꾸지 않으려고 그대로 두었다.
- `bin/adopt`는 아직 bash로 clone과 복사를 한다. 이 ADR에서는 옛 pin 찾기와 entry 추가만 module로 옮겼다.
