# 0115 — template 종류 목록을 `bin/check-integrity`가 검사한다

`bin/check-integrity`가 손으로 관리하는 종류 목록 네 곳을 `project-templates/`의 디렉터리와 비교한다. 네 곳은 `apply-project-template` skill의 description과 종류 표, `README.md`의 `apply-template` 주석과 tree다. 목록에 빠진 종류와, 디렉터리 없이 목록에만 남은 종류를 모두 오류로 낸다.

## 경위

- ADR 0111에서 rust template을 더할 때, 목록이 어디 있는지 몰라 `cpp`를 grep해서 네 곳을 찾았다. ADR 0113의 리뷰는 이것을 Shotgun Surgery로 짚었다.
- skill의 description이나 표에서 종류가 빠지면 Claude는 그 template을 제안하지 않는다. 오류도 나지 않아서 아무도 알아채지 못한다.

## 결정

- 정해진 형식의 목록이라 규칙 문서 대신 검사로 막는다. Stop hook이 `bin/check-integrity`를 실행하므로, 따로 연결할 것은 없다.
- 목록을 생성하는 방식은 택하지 않았다. README와 skill은 사람과 Claude가 직접 읽는 글이라, 생성 단계를 끼우면 고칠 곳만 바뀌고 수는 줄지 않는다.
- 파일은 있는데 목록을 찾지 못하면 오류로 낸다. 문구를 바꿔 검사가 목록을 놓치는 일을 막기 위해서다. 파일이 없으면 검사하지 않는다. `tests/run.sh`의 sandbox에는 README와 이 skill이 없다.
- `tests/run.sh`에 시험 넷을 더했다. 목록이 모두 맞는 경우, 한 목록에서 빠진 경우, 디렉터리가 없는 종류가 목록에 있는 경우, 목록을 찾지 못한 경우다.
