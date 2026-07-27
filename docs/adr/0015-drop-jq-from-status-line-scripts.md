# 0015 — status line 스크립트에서 jq/bc를 걷어내고 python3 stdlib으로 옮긴다

`user/{mac,linux}/statusline-command.sh`와 `subagent-statusline.sh`의 JSON 처리를 `jq`(+`bc`)에서 python3 stdlib으로 바꾼다. 파일명과 bash 래퍼는 유지해 `settings.json`과 `install.sh`를 건드리지 않는다. 부수적으로 [[0013-json-escapes-in-subagent-statusline]]이 미해결로 남긴 task 이름 이스케이프 결함이 함께 사라진다.

## Context

두 갈래의 통증이 한 원인으로 모인다.

**저장소 가드레일 위반.** 프로젝트 CLAUDE.md가 `Dependencies stay minimal: Python 3 stdlib + bash 3.2 only. Don't introduce yq, PyYAML, jq, or other external deps`로 정해두었는데, status line 스크립트 넷이 처음부터 `jq`를 썼고 `subagent-statusline.sh`는 `bc`까지 썼다.

**실제 고장.** Linux/WSL 머신에 `jq`가 없어 메인 status line이 빈 줄만 출력했다. 스크립트가 exit 0으로 끝나서 Claude Code가 조용히 무시했고, 무성 실패라 원인을 찾는 데 진단이 필요했다. 당시엔 `jq` 설치로 넘어갔지만 그것은 머신마다 반복되는 처방이지 해결이 아니다.

`0013`은 같은 스크립트의 JSON 이스케이프 결함을 고치면서 **task 이름을 이스케이프 없이 `printf`로 끼워 넣는 문제**를 "json.dumps 재작성이 필요하다"며 남겼다. 이번 이관이 그 재작성이다.

## Considered Options

**의존성 처리** — 머신마다 `jq` 설치 vs python3 이관. **이관**을 택했다. 설치는 새 머신마다 되풀이되고, 가드레일 위반은 그대로 남으며, 다음 머신에서 같은 무성 실패가 재현된다.

**이관 형태** — 세 가지를 놓고 갈랐다.

- **bash 래퍼 유지 + 내부만 python3** (채택). `settings.json`이 `bash ~/.claude/<name>.sh`로 호출하고 `install.sh:49-50`이 파일명으로 심볼릭 링크를 건다. 이름과 래퍼를 지키면 두 파일 다 무수정이다. 특히 `settings.json`에는 이 작업과 무관한 미커밋 변경이 있어 섞지 않는 편이 낫다.
- **`.py`로 바꾸고 `settings.json`·`install.sh`·`uninstall.sh` 수정.** 더 깔끔해 보이지만 세 파일을 함께 고쳐야 하고 얻는 것이 이름뿐이다.
- **`jq`만 걷고 `bc`는 남기기.** 절반만 해결이라 기각.

**필드 추출 방식**(`statusline-command.sh`) — 탭 구분 한 줄 vs 한 줄에 한 필드. **한 줄에 한 필드**를 택했다. `IFS=$'\t'`는 탭이 IFS 공백문자라 연속 탭을 하나로 합치고, 그러면 빈 필드가 사라져 뒤 변수들이 한 칸씩 밀린다. 줄 단위면 빈 필드가 빈 줄로 남아 위치가 보존된다.

**`statusline-command.sh`의 `\033` 색상 코드는 그대로 두었다.** 이 스크립트는 ANSI를 터미널로 직접 출력하고 `printf '%b'`가 확장하므로 정상이다. `0013`이 고친 것은 색상 코드가 **JSON 문자열 안으로** 들어가던 `subagent-statusline.sh` 쪽이고, 이번 이관으로 그 파일은 색상을 python 문자열로 들고 있다가 `json.dumps`가 알아서 이스케이프한다.

## Consequences

- `jq`와 `bc` 호출이 0건이 됐다. **`jq`가 없는 PATH로 실제 실행해 검증했다** — 양쪽 스크립트 모두 정상 출력, exit 0.
- **`0013`의 미해결 항목이 닫혔다.** 따옴표와 백슬래시가 든 task 이름(`fix "quoted" and C:\path`)으로 검증했고, 이전엔 파싱 자체가 실패하던 입력이 이제 유효 JSON으로 나온다.
- 깨진 입력·빈 입력·`tasks` 부재에서 조용히 exit 0으로 끝난다. 기존 동작과 같다.
- `git`, `grep`, `sed`, `date`는 여전히 쓴다. 가드레일이 지목한 것은 `jq`/`yq`/`PyYAML`급 외부 의존성이고 이들은 bash 3.2 환경의 기본 구성이라 범위 밖으로 뒀다.
- `startTime`을 epoch 초로 해석하는 기존 의미를 그대로 유지했다. 밀리초일 가능성은 이번 범위에서 다루지 않았다.
- mac/linux 네 파일은 여전히 바이트 단위로 동일하다. 언젠가 `user/shared/`로 합칠 여지가 남지만 별개 결정이다.

## References

- [[0013-json-escapes-in-subagent-statusline]]
- [[0003-adr-for-every-change]]
