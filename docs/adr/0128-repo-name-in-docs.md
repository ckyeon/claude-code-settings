# 0128 — README와 CLAUDE.md의 repo 이름을 claude-code-settings로 맞춘다

repo는 처음에 `~/workspace/toy-project/coding-agent-settings`에 있었고, 지금은 GitHub와 로컬 디렉터리 모두 `claude-code-settings`다. README의 제목, 설치 절차의 `cd coding-agent-settings`, `apply-template` 예시의 경로 placeholder, CLAUDE.md의 제목에 옛 이름이 남아 있었다. 특히 `git clone` 다음의 `cd`는 clone이 만든 디렉터리 이름과 달라 그대로 따라 하면 실패했다. 네 곳을 `claude-code-settings`로 바꿨다. 과거 ADR에 남은 옛 이름은 기록이므로 두었다.
