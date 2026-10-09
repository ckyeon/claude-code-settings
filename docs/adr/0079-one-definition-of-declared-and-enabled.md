# 0079 — 선언과 활성화의 판정을 한 곳에 두고, 리뷰에서 나온 `check-machine`의 결함을 고친다

`8f93ba0` 이후의 변경을 Standards와 Spec 두 축으로 리뷰했다. 이 ADR은 그 결과 가운데 선언한 plugin과 활성화 여부를 판정하는 code에 관한 것을 다룬다.

## 고친 것

- **"선언한 plugin"의 정의가 둘이었다.** `bin/check-integrity`는 `user/shared/plugins/` 아래 폴더가 있으면 선언으로 쳤고, `lib/common.sh`는 sidecar까지 있어야 쳤다. `enabledPlugins`를 읽는 code도 두 곳에 있었다. 판정을 `lib/declarations.py`로 모으고 `lib/common.sh`, `bin/check-integrity`, `bin/check-machine`이 모두 그것을 읽게 했다. 선언은 폴더가 있으면 성립한다. 공개 upstream이 없어 sidecar가 없는 선언도 선언이다.
- **꺼 둔 plugin을 활성화된 것으로 쳤다.** `enabledPlugins`의 값을 보지 않아서 `"x@m": false`인 plugin에 `check-machine`이 "설치되지 않음" 오류를 냈고, `check-integrity`는 그 항목을 활성화로 인정했다. 이제 값이 참일 때만 활성화로 친다. marketplace는 값과 무관하게 key에서 알 수 있으므로 `install.sh`의 설치 안내는 그대로 나온다.
- **`check-machine`이 sidecar 없는 선언과 선언 없는 plugin을 놓쳤다.** plugin 목록을 선언에서 가져왔기 때문이다. user scope에서 활성화한 plugin은 선언 여부와 무관하게 `settings.json`에서 직접 읽어 설치를 확인한다. 선언이 없다는 사실은 `check-integrity`가 경고한다.
- **`uninstall.sh`가 소유 경로 목록을 따로 갖고 있었다.** ADR 0078은 목록이 `list_owned_links` 한 곳에만 있다고 적었지만 사실이 아니었다. `uninstall.sh`도 그 목록을 읽게 했다.
- **함수 이름을 용어에 맞췄다.** `list_tracked_plugins`와 `list_tracked_mcp_servers`를 `list_declared_plugins`와 `list_declared_mcp_servers`로 바꿨다.
- **`check-integrity`의 skill 검사 loop**가 module 수준의 `skills_dir`과 `skill_names`를 loop 변수로 다시 쓰고 `full`을 다섯 번 검사했다. loop 변수에 자기 이름을 주고 `full` 검사를 두 번으로 줄였다.

## Consequences

- `bin/` 도구가 `lib/`의 Python module을 import한다. 실행할 때 `PYTHONDONTWRITEBYTECODE=1`을 주므로 `lib/`에 `__pycache__`가 생기지 않는다.
- `check-machine`의 요약 줄이 "declared plugins" 대신 "plugins enabled at user scope"의 수를 센다.
- 실제 repo에서 `list_declared_plugins`의 출력은 바꾸기 전과 한 줄도 다르지 않다. 11개 plugin 모두 sidecar가 있고 꺼 둔 항목이 없기 때문이다.
- test 15개를 추가했다. 값이 `false`인 항목, sidecar 없는 선언, 선언 없는 활성 plugin, 다른 곳을 가리키는 symlink, 대상이 repo에서 사라진 symlink, `uninstall.sh`의 연결 해제와 backup 복원이다.
