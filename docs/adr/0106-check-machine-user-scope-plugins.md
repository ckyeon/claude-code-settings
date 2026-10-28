# 0106 — check-machine은 user scope에 설치된 plugin만 선언 여부를 검사

`bin/check-machine`은 설치된 plugin이 `user/shared/plugins/`에 선언돼 있지 않으면 scope를 보지 않고 경고했다. 그래서 다른 프로젝트에 project scope로 설치한 `ait@apps-in-toss`가 계속 경고에 나왔다. [[0095-project-only-marketplace-scope]]에 따르면 한 프로젝트만 쓰는 plugin은 그 프로젝트에 속하므로, 이 repo가 선언할 대상이 아니다. 이제 user scope에 설치된 plugin만 검사하고, 경고 문구에도 "at user scope"를 넣었다.

## Consequences

- 고치지 않으면 가짜 경고가 매번 떠서, 진짜 경고도 함께 흘려 보게 된다.
- project scope나 local scope에만 설치된 plugin은 이제 이 검사에서 빠진다. 그런 plugin의 선언은 그 프로젝트가 맡는다.
- `tests/run.sh`에 project scope로만 설치된 plugin은 경고하지 않는다는 검사를 더했다. 고치기 전 코드에서는 이 검사가 실패했다.
- 이 기기에서 `bin/check-machine`을 돌리면 plugin 경고가 더는 나오지 않는다.
