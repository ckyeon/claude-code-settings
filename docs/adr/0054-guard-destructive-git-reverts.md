# 0054 — 넓게 지우는 git 되돌리기를 PreToolUse hook으로 막는다

커밋하지 않은 작업을 한 번에 지우는 git 명령을 Bash tool 앞에서 막는 hook을 더했다. `user/shared/hooks/guard-destructive-git.py`가 판단하고, `settings.json`의 `hooks.PreToolUse`가 모든 Bash 호출에 건다. 이 repo의 첫 hook이다.

계기는 `ckyeon/gizzard`에서 두 번 난 같은 종류의 사고다. 2026-09-17에 뮤테이션 검사 스크립트의 `git checkout -- src/`가 커밋하지 않은 소스 6개를 한 번에 날렸고, 그 전 티켓에서도 파일 하나를 날렸다가 복원했다. 두 번 다 원인은 같다. 고쳤다가 되돌리는 검사를 커밋하지 않은 작업 트리에서 돌렸고, 되돌리는 명령의 범위가 고친 범위보다 넓었다. 그 저장소는 티켓마다 이 검사를 하므로 관행이 남아 있는 한 사고도 남는다.

판단은 명령 문자열만 보는 정적 검사다. 저장소 상태를 읽지 않으므로 어느 디렉터리에서 실행하든 같은 결과가 나오고, 스크립트가 `cd`로 옮겨 간 저장소에서도 같은 기준이 적용된다.

## Consequences

- 막는 것은 넷이다. `git reset --hard`, `git clean -f`, `git checkout --force`, 그리고 `git checkout`과 `git restore`로 경로를 되돌리는데 되돌릴 commit을 적지 않았거나 경로가 디렉터리나 glob이라 여러 파일에 걸치는 경우다.
- 막지 않는 것은 `git checkout HEAD -- <파일>`처럼 되돌릴 commit과 파일을 둘 다 적은 명령, branch 이동, `git checkout -b`, 그리고 `git restore --staged`처럼 index만 되돌리는 명령이다. 마지막 것은 작업 트리를 건드리지 않으므로 지울 것이 없다. 고쳤다가 되돌리는 검사는 이 좁은 형태로 쓴다. 되돌릴 commit을 적으라고 요구하는 쪽이 `git checkout -- <파일>`보다 낫다. 후자는 index 내용으로 되돌리므로 무엇으로 되돌아가는지 명령만 보고 알 수 없다.
- 셸 스크립트 파일을 만들어 그 안에서 실행하면 실행하는 순간에는 명령 문자열이 보이지 않는다. 다만 그 파일을 만드는 heredoc은 Bash tool을 지나므로 만드는 자리에서 걸린다. 실제 사고도 이 모양이었고 시험에서 걸리는 것을 확인했다. Write tool로 스크립트를 만들면 걸리지 않으므로 이 hook은 마지막 방어선이 아니다. 근본 대책은 되돌리기가 필요한 작업을 커밋한 tree에서 하는 것이고, `ckyeon/gizzard`는 `scripts/mutate.py`로 그렇게 한다.
- 거절 메시지가 이유와 대안을 함께 준다. Claude Code는 거절당한 호출을 그대로 다시 하지 않고 고쳐서 하므로, 막는 것만으로 끝나지 않고 안전한 형태로 넘어간다.
- 모든 Bash 호출에 python3 프로세스 하나가 붙는다. stdlib만 쓰고 저장소를 읽지 않아 수십 밀리초다. "Dependencies stay minimal" guardrail을 지킨다.
- 이 hook을 끄려면 `settings.json`의 `hooks`를 지우거나 `/hooks`에서 끈다. 한 번만 넘기고 싶으면 명령을 좁은 형태로 바꾸는 쪽이 낫다.
- `git restore`는 `git checkout`과 달리 위치 인자가 언제나 경로다. 그래서 `git restore <파일>`은 `--`가 없어도 경로로 보고, 되돌릴 commit은 `--source`나 `-s`로만 읽는다. 처음 판은 `--` 없는 `git restore <파일>`을 통과시켰는데, 같은 뜻인 `git checkout -- <파일>`은 막으면서 이것만 통과시키는 것은 앞뒤가 맞지 않아 커밋 전 검토에서 고쳤다.
- 시험은 26가지 명령으로 했다. 사고 명령, 그 스크립트를 만드는 heredoc, `cd`로 옮겨 간 뒤의 같은 명령을 막고, 안전한 되돌리기와 branch 이동과 `git diff ... -- src/`는 통과한다. 설치된 symlink 경로에서 실제로 발동하는 것도 확인했다. 시험 명령 목록을 heredoc으로 넘기려던 Bash 호출을 이 hook이 막았으므로 heredoc 안의 명령도 걸린다는 점은 실제로 확인된 셈이다. 시험 스크립트는 Write tool로 만들어 돌렸다.
- `bin/check-integrity`는 clean이다. 이 파일은 upstream에서 가져온 것이 아니라 직접 쓴 것이므로 provenance sidecar를 두지 않는다.
