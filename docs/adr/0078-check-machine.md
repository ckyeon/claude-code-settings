# 0078 — `bin/check-machine`으로 기기가 repo와 같은지 확인하고, 그 통과를 재현 완료의 정의로 삼는다

repo가 선언한 plugin과 MCP server가 기기에 실제로 있는지 확인하는 도구가 없었다. 2026-10-09에는 임시 script로 한 번 비교했을 뿐이다. ADR 0074가 목적을 재현으로 정했으므로 "재현됐는가"에 답하는 도구가 필요하다. 읽기만 하는 `bin/check-machine`을 추가했다.

| 구분 | 항목 |
|---|---|
| 오류 | 소유 대상이 `~/.claude/`에서 이 repo로 symlink되어 있지 않다 |
| 오류 | user scope에서 활성화한 plugin이 설치돼 있지 않다 |
| 오류 | 선언한 MCP server가 user scope에 등록돼 있지 않다 |
| 경고 | 선언하지 않은 plugin이나 MCP server가 기기에 있다 |
| 경고 | repo에 commit하지 않은 변경이 있다 |
| 경고 | 원격에 없는 commit이 있다 |

오류가 없으면 통과이고 `--strict`를 주면 경고도 실패다. **새 기기에서 `install.sh`와 선언된 명령을 실행한 뒤 이 도구가 오류 없이 통과하는 것이 재현 완료의 정의다.** README의 "Quick start"를 그 절차로 다시 썼고 "Multi-machine workflow" 절을 거기에 합쳤다.

## 설계

- **`check-integrity`와 나눈 이유**: `check-integrity`는 repo만 읽고 Stop hook에서 돈다. 이 도구는 `~/.claude/plugins/installed_plugins.json`과 `~/.claude.json`을 읽어서 결과가 기기마다 다르다. 그래서 별도 도구로 두고 Stop hook에는 넣지 않았다.
- **소유 대상의 목록은 한 곳에 둔다.** `install.sh`에 있던 연결 목록을 `lib/common.sh`의 `list_owned_links`로 옮겼다. `install.sh`는 그 목록으로 연결하고 `check-machine`은 같은 목록을 검증한다.
- **template에서만 활성화한 plugin은 설치를 요구하지 않는다.** `typescript-lsp`처럼 프로젝트마다 설치하는 plugin이다.
- **`~/.claude.json`에서는 MCP server의 이름만 읽는다.** 항목 안에 API key가 있다. secret의 존재는 확인하지 않는다(ADR 0077).
- **commit하지 않은 변경과 push하지 않은 commit은 경고다.** 원격에 없는 것은 재현되지 않지만, push는 요청이 있을 때만 하므로(ADR 0073) 오류로 두면 작업 중에는 늘 실패한다.

## Consequences

- 원격에 없는 commit 수는 마지막으로 fetch한 원격 branch와 비교한 값이다. 도구는 network를 쓰지 않는다.
- Linux 쪽은 이 도구를 Linux 기기에서 돌려 검증할 수 있다. 아직 돌려 보지 않았다.
- test 22개를 `tests/run.sh`에 추가했다. 고친 `install.sh`를 임시 `HOME`에서 실행해 모든 소유 경로가 연결되는지도 확인한다.
- 2026-10-10 이 기기에서 돌린 결과는 소유 경로 11개, 선언한 plugin 11개, MCP server 5개에 오류가 없었다.
