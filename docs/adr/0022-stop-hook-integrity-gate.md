# 0022 — 프로젝트 스코프 Stop hook으로 adopt 밖 변경까지 검사

`bin/adopt`를 거치지 않는 변경(직접 작성한 스킬, 손으로 고친 `SKILL.md`, 참조 대상 삭제)을 덮기 위해 `.claude/settings.json`에 `Stop` hook을 추가했다. 세션이 끝날 때 `bin/check-integrity`를 실행하고, 실패하면 한 번 block해서 오류를 모델에게 되돌린다.

## Context

ADR 0021이 adopt 경로를 닫았지만 그건 전체의 일부다. 이 저장소의 변경 대부분은 adopt를 거치지 않는다 — ADR 0019~0021을 만든 세션조차 커밋 3건 중 2건이 adopt 밖이었다(`CLAUDE.md`, `bin/adopt`, ADR 파일들).

사용자는 "내가 직접 고칠 일은 없을 것 같다"고 했다. 맞는 관찰이지만 결론은 반대다. 편집이 사라지는 게 아니라 주체가 에이전트로 바뀐다는 뜻이고, 에이전트는 참조하는 쪽을 확인하지 않고 스킬을 지우는 일을 사람보다 더 잘 한다. 가장 위험한 건 삭제다 — 지우는 경로에는 아무 도구도 없다.

## Considered Options

**CI(GitHub Actions)**를 먼저 놓는 안을 검토했지만 순서를 뒤집었다. CI는 push 시점에 뛰므로 결함을 만든 세션이 이미 끝난 뒤다. 그 빨간 X를 읽고 고치는 건 사람이고, 이는 사용자가 피하려는 바로 그 작업이다. Stop hook은 에이전트가 아직 살아 있을 때 뛴다 — ADR 0021에서 검사를 `bin/adopt` 안으로 옮긴 것과 같은 원리다.

**pre-commit hook**은 `git config core.hooksPath` 설정이 필요해 이 저장소 가드레일에 걸린다.

**hookify 플러그인** 형식도 가능하지만, 한 줄짜리 hook에 플러그인 의존을 더할 이유가 없어 순수 `settings.json`을 썼다.

## Consequences

- 스크립트는 `.claude/hooks/check-integrity-stop.sh`. 자기 위치에서 REPO_ROOT를 구하고, 커맨드는 `${CLAUDE_PROJECT_DIR:-.}` 형태라 이 변수가 주입되든 아니든 동작한다(둘 다 검증).
- **루프 방지:** `stop_hook_active`가 이미 설정된 호출에서는 block하지 않고 `systemMessage`로 낮춘다. 고칠 수 없는 오류가 세션을 물고 늘어지지 않는다.
- **절대 non-zero로 끝나지 않는다.** hook 자체의 고장이 세션을 막으면 안 된다. 잘못된 stdin을 받아도 exit 0.
- 정상일 때는 출력이 없다.
- 검증한 경로: 정상(무음), 결함+최초 호출(block + 실행 가능한 reason), 결함+`stop_hook_active`(block 없음), 잘못된 stdin(exit 0), 서로 다른 cwd 3가지.
- **주의:** 세션 시작 시점에 `.claude/settings.json`이 없었다면 설정 watcher가 이 디렉터리를 감시하지 않아 hook이 다음 세션부터 적용된다. `/hooks`를 한 번 열거나 재시작하면 즉시 로드된다.
- **여전히 남는 공백:** 다른 머신에서의 push, GitHub 웹 편집. CI가 덮을 영역이지만 CI에는 `~/.claude/plugins/cache`가 없어 플러그인 vendoring 스킬 참조에서 오탐이 날 수 있다. 해당 사례가 생기면 그때 결정한다.

## References

- [[0021-adopt-runs-integrity-check]] — adopt 경로 쪽 방어
- [[0019-static-integrity-checker]]
- [[0003-adr-for-every-change]]
