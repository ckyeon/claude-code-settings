# 0061 — claude.ai 동기화 skill과 Codex 생성 파일을 gitignore, Opus 5.5 effort 설정 commit

`.gitignore`에 `user/shared/skills/synced/`, `AGENTS.md`, `.agents/`, `.codex/`를 추가했다. 앞의 것은 Claude Code가 claude.ai 계정의 skill을 `~/.claude/skills/synced/`에 동기화한 캐시인데, `~/.claude/skills`가 `user/shared/skills`의 symlink라서 repo 안에 생긴다. 뒤의 셋은 Codex 설치 때 이 repo의 CLAUDE.md, check-updates skill, Stop hook을 "Claude Code"에서 "Codex"로 단어만 바꿔 복사한 Codex용 project 파일이다. 둘 다 머신마다 생기는 파일이고, 지우면 동기화된 skill과 Codex 설정이 깨지므로 지우지 않고 무시한다.

같은 정리에서 `user/shared/settings.json`에 commit하지 않고 쌓여 있던 변경도 commit했다. Claude Code가 새 model인 Opus 5.5의 `effortLevel`을 `xhigh`(claude-opus-5와 같은 값)로 기록하면서 statusLine 블록의 위치를 옮긴 것이다. 되돌리면 Opus 5.5의 effort가 기본값으로 돌아가므로 남겼다.
