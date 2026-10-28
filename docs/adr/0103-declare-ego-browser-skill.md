# 0103 — ego lite 앱이 만드는 ego-browser skill을 gitignore하고 declared로 기록

ego lite 앱이 `~/.claude/skills/ego-browser`를 앱 안의 skill 폴더로 링크했다. `~/.claude/skills`가 `user/shared/skills`의 symlink라서 이 링크가 repo 안에 생겼다. 다른 기기에서도 쓸 skill이므로 링크는 gitignore하고, README § Scope 표에 declared 항목으로 넣어 앱 설치와 onboarding을 그 링크를 만드는 방법으로 적었다.

## Context

- 링크는 `~/.local/share/ego/ego-skills`를 거쳐 `/Applications/ego lite.app` 안의 버전 폴더로 이어진다. 이 기기의 절대 경로라서 commit하면 다른 기기에서는 깨진 링크가 된다.
- 링크가 생긴 시각(2026-10-26 02:15)은 앱이 만든 `~/.local/bin/ego-browser` 링크와 같다.
- `bin/check-integrity`와 `bin/check-machine` 모두 이 링크를 문제로 보지 않으므로, gitignore가 없으면 `git add -A` 한 번으로 공개 repo에 들어간다.

## Considered Options

- **gitignore만 하고 범위 밖으로 둔다.** [[0061-ignore-local-artifacts-and-commit-opus-5-5-effort]]가 `synced/`를 처리한 방식이다. 사용자가 다른 기기에서도 쓴다고 했으므로, 새 기기에서 이 repo만 보고 같은 환경을 만들 수 있도록 declared로 올렸다.
- **[[0049-adopt-herdr-skill]]처럼 `copied`로 채택한다.** SKILL.md는 실행 때마다 `ego-browser skill`의 출력을 따르라고만 하고, 실제 지침은 설치된 앱이 출력한다. 파일을 고정해도 동작은 고정되지 않으므로 택하지 않았다.

## Consequences

- README에 설치 순서를 적었다. `install.sh`는 기존 `~/.claude/skills`를 `.backup-<시각>`으로 옮기고 나서 링크하므로, ego lite를 먼저 설치하면 그 링크가 백업 폴더로 함께 옮겨진다.
- skill 내용은 앱 업데이트를 따라 바뀌고, 이 repo는 그 버전을 기록하지 않는다. README § Scope가 플러그인 버전을 범위 밖으로 둔 것과 같은 처리다.
- skill의 description은 브라우저가 필요하면 다른 도구보다 ego-browser를 먼저 쓰라고 한다. 사용자 지시가 없어 이 우선순위는 그대로 두었다.
- `install.sh`는 ego lite 설치 안내를 출력하지 않는다. 플러그인과 MCP 서버처럼 안내가 필요해지면 그때 넣는다.
