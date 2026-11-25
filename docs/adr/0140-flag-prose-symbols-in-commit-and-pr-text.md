# 0140 — commit message와 PR 제목, 본문의 세미콜론과 화살표는 실행 전에 막는다

`user/shared/hooks/flag-prose-symbols.py`가 Bash의 PreToolUse에서도 돈다. `git commit`의 message와 `gh pr create`, `gh pr edit`의 제목과 본문에서 절을 잇는 세미콜론과 화살표를 찾으면, 명령을 막고 고칠 줄을 알린다. ADR 0138이 잡지 못한다고 남긴 글이다.

## 결정

- **알리지 않고 막는다.** Markdown 파일은 이미 쓴 뒤에 보므로 알리는 수밖에 없다. 하지만 PR은 만들어지는 순간 알림이 나가므로, 게시 전에 고치게 하려면 실행 전에 막아야 한다. commit도 막으면 amend가 필요 없다.
- **글은 명령 문자열에서 읽는다.** heredoc 본문, `-m`, `--message`, `--title`, `--body` 같은 옵션 값, `-F`와 `--body-file`이 가리키는 파일이다. heredoc 본문을 먼저 떼어 낸 다음 나머지를 `shlex`로 나눈다. 본문 안의 작은따옴표 때문에 `shlex`가 실패하지 않게 하려는 것이다.
- **같은 hook 파일에 둔다.** 판정은 Markdown 검사와 같은 `findings()`가 한다. 그래서 code fence, inline code, 큰따옴표 안은 commit message에서도 건너뛴다.
- 두 경로가 알림의 끝 문장을 같이 쓴다. 규칙이 기호를 허용하는 자리라면 backtick이나 큰따옴표로 감싸라고 고쳤다. 감싸면 이 검사가 건너뛰기 때문이다.

## Consequences

- `tests/test_flag_prose_symbols.py`에 test 다섯을 더했다. heredoc으로 넘긴 commit message, 옵션으로 넘긴 commit message, PR 제목과 본문과 본문 파일, 규칙이 허용하는 자리, 검사 대상이 아닌 명령을 본다. Python 3.15.2와 3.9.6에서 10개가 모두 통과했다.
- ADR 0126 이후의 commit 15개를 heredoc 형태로 넣어 보았는데 하나도 걸리지 않았다.
- 이 세션에서 scratchpad의 임시 repo에 세미콜론이 든 message로 commit하려 하자 막혔고, 깨끗한 message는 통과했다.
- 막으면 한 줄로 이은 명령 전체가 실행되지 않는다. 앞에 붙인 `git add`도 다시 실행해야 한다.
- 보지 못하는 글이 남는다.
  - 편집기로 쓰는 message와 변수에 담아 넘기는 message는 명령 문자열에 없다.
  - `cd`로 옮긴 뒤 상대 경로로 넘긴 파일은 세션의 작업 디렉터리를 기준으로 찾으므로 놓칠 수 있다.
  - PR comment, review, issue는 대상에 넣지 않았다.
- Bash를 실행할 때마다 Python이 한 번 더 뜬다. 명령에 `commit`도 `gh`도 없으면 바로 끝난다.
