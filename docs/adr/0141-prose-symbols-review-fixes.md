# 0141 — 산문 기호 hook의 리뷰 지적을 고친다

ADR 0138~0140을 `code-review`로 리뷰한 뒤, 사용자가 고르기로 한 지적을 고쳤다.

## 결정

- **HTML 주석을 건너뛴다.** 닫는 `-->`를 화살표 `->`로 읽고 있었다. Bash 경로는 명령을 막으므로, PR template에 흔한 `<!-- ... -->`가 든 PR 생성까지 막혔다. 한 줄 주석은 줄 안에서, 여러 줄 주석은 줄 단위로 건너뛴다.
- **code fence는 여는 줄과 같은 문자로, 같거나 더 긴 줄이 와야 닫힌다.** 물결표 fence 안을 산문으로 읽었고, backtick 넷으로 연 fence 안에 backtick 셋 줄이 있으면 판정이 어긋나 그 뒤 산문을 놓쳤다.
- **frontmatter는 닫는 `---`가 있을 때만 인정한다.** 첫 줄이 구분선이고 닫는 줄이 없으면 파일 끝까지 건너뛰고 있었다.
- **Edit은 이번에 더한 줄에 걸친 자리만 본다.** `new_string`과 같은 글이 파일 앞쪽에 이미 있으면 그 줄도 알리고 있었다. 이제 `tool_response`의 `structuredPatch`에서 더한 줄을 읽고, 그 줄에 걸친 자리만 남긴다. 공식 hooks 문서는 Edit의 `tool_response` 모양을 적지 않는다. 그래서 이 세션의 transcript에 기록된 Edit 결과에서 이 필드를 확인했고, 실제 hook에서도 앞쪽의 같은 문장을 알리지 않는 것을 보았다. 필드가 없으면 전처럼 모든 자리를 본다.
- **`gh`와 git의 옵션 자리를 넓힌다.**
  - `gh`는 `gh -R <repo> pr create`나 `gh pr -R <repo> create`처럼 `pr`과 하위 명령 앞에 오는 옵션을 건너뛰고, `create`의 별칭 `new`도 본다. 별칭은 `gh pr create --help`의 ALIASES에서 확인했다.
  - git은 값을 띄어 쓰는 전역 옵션으로 `-C`, `-c`에 더해 `--git-dir`, `--work-tree`, `--namespace`, `--config-env`, `--attr-source`를 건너뛴다. 이 목록은 git 2.54.0에서 띄어 쓴 형태가 통하는지 돌려 보고 정했다.
- **같은 명령 안에서 먼저 만드는 파일은 한계로 적는다.** `cat > m.txt <<EOF` 다음에 `git commit -F m.txt`를 하면 hook이 도는 시점에는 파일이 아직 없고, 같은 이름의 옛 파일이 있으면 그 내용을 본다. 명령을 실행하지 않고는 알 수 없으므로 hook 설명에 한계로 적었다.
- `user/shared/rules/korean-writing.md`에 어긋난 표현을 고쳤다.
  - ADR 0138의 다섯 곳과 hook 설명의 한 곳에서 Edit 뒤 조사를 발음에 맞게 고쳤다(Edit으로, Edit은, Edit이, Edit을). 원칙 1에 어긋났다.
  - ADR 0139의 "repo 구조를 이미 알고 있으므로"를 "repo 안에서 돌므로"로 고쳤다. 번역투 표의 무생물 주어와 인식 동사에 해당했다.

## Consequences

- test 둘을 더하고 기존 test 넷에 사례를 더했다. 12개가 Python 3.15.2와 3.9.6에서 모두 통과했다. 고치기 전 hook에 같은 입력 아홉 가지를 넣으면 아홉 모두 결과가 달랐다.
- ADR 0139가 적은 "첫 줄이 `---`이면 frontmatter로 본다"는 이 결정으로 "닫는 `---`가 있으면"으로 바뀌었다.
- 리뷰의 나머지 지적은 고치지 않았다.
  - 규칙이 기호를 허용하는 자리라면 감싸라는 알림 문장은 그대로 둔다. 규칙도 인용과 코드를 표시하라고 하므로 우회법이 아니라 올바른 처리로 본다.
  - 판단 사항으로 나온 것들이다. "commit message"와 "commit 메시지"가 섞인 것, test 파일 첫 줄 docstring이 Bash 경로를 말하지 않는 것, 두 test class의 겹치는 준비 코드, git 인자 처리가 `guard-destructive-git.py`와 겹치는 것, `COMMAND_OPTIONS` 값에 이름과 종류 표시가 섞인 것, `HEREDOC_LABEL`과 `__HEREDOC_` 접두어의 이름, `check-integrity` 중간의 import, 새 hook 항목에 `statusMessage`가 없는 것이다.
  - URL 안의 세미콜론이나 HTML entity처럼 산문이 아닌 세미콜론도 commit을 막는다. backtick으로 감싸면 통과한다.
