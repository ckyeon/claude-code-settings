# 0105 — `remoteControlAtStartup: true`를 user settings에 commit

Claude Code가 `user/shared/settings.json`에 `"remoteControlAtStartup": true`를 기록했다. settings reference는 이 키를 "Connect Remote Control automatically when a session starts"로 설명하고, 어느 settings 파일에서든 쓸 수 있다고 한다. 개인 선호 설정이므로 owned 파일에 그대로 commit한다. [[0061-ignore-local-artifacts-and-commit-opus-5-5-effort]]가 `effortLevel`을 commit한 것과 같은 처리다.

## Consequences

- 모든 기기에서 모든 세션이 시작할 때 Remote Control에 연결되고, 같은 계정의 claude.ai와 모바일 앱에서 그 세션을 볼 수 있다. 사용자가 이 동작을 확인하고 commit에 동의했다.
- 한 프로젝트에서만 끄려면 그 프로젝트의 `.claude/settings.json`이나 `.claude/settings.local.json`에 `false`를 둔다. settings 문서의 managed 우선순위 예외 표에 따르면 프로젝트 파일의 `false`는 managed의 `true`보다도 우선한다.
