# 0104 — herdr가 settings.json에 넣은 SessionStart hook을 그대로 commit하고 declared로 기록

`herdr integration install claude`가 `~/.claude/hooks/herdr-agent-state.sh`를 쓰고, `user/shared/settings.json`에 그 스크립트를 실행하는 `SessionStart` 항목을 넣었다. 항목은 herdr가 쓴 그대로 commit하고, README § Scope 표에 declared로 넣어 이 명령을 그 항목과 스크립트를 만드는 방법으로 적었다.

## Context

- 스크립트는 herdr pane 안에서 Claude 세션이 시작되면 세션 ID와 transcript 경로를 herdr socket에 보낸다. `HERDR_ENV`가 없으면 바로 끝난다. herdr가 관리하는 파일이라 연동을 다시 설치하거나 업데이트하면 덮어쓴다.
- 이 repo의 다른 hook은 `$HOME`으로 경로를 쓰지만, 이 항목만 `/Users/ckyeon`으로 시작하는 절대 경로를 쓴다.
- herdr는 `settings.json`에서 자기 항목을 명령 문자열 전체가 같은지로 찾는다(herdrdev/herdr `src/integration/config_edit.rs`의 `ensure_command_hook`). 표기가 다르면 자기 항목으로 보지 않고 새 항목을 더한다.

## Considered Options

- **경로를 `$HOME`으로 바꾼다.** 다른 hook과 표기가 맞지만, 다음 설치나 업데이트 때 herdr가 절대 경로 항목을 하나 더 넣는다. repo가 도구와 계속 다투게 되므로 기각했다.
- **연동을 지운다.** 사용자가 herdr로 Claude 세션을 추적하려고 설치했으므로 기각했다.
- **그대로 commit한다 (채택).** 사용자는 이 설정을 Linux에서 쓰지 않으므로, 사용자 이름이 같은 Mac에서는 경로가 같다. 새 Mac에서 같은 명령을 실행하면 herdr가 기존 항목을 알아보고 스크립트만 쓴다.

## Consequences

- 이 명령을 아직 실행하지 않은 Mac에서는 세션을 시작할 때마다 스크립트를 찾지 못하는 hook 오류가 난다. 세션을 막지는 않는다. README에 이 순서를 적었다.
- 공개 repo의 `settings.json`에 이 기기의 홈 경로가 들어간다. 경로 속 사용자 이름은 GitHub 계정 이름과 같다.
- Linux에서 쓰게 되면 herdr가 `/home` 경로 항목을 따로 더해, 두 OS가 서로의 항목에서 오류를 낸다. 그때 이 결정을 다시 본다.
