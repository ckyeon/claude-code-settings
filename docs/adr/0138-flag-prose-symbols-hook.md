# 0138 — Markdown 산문의 세미콜론과 화살표를 쓰는 순간 알린다

`user/shared/hooks/flag-prose-symbols.py`를 PostToolUse hook으로 더했다. Write나 Edit로 Markdown 파일을 쓰면, 이번에 쓴 산문에서 절을 잇는 세미콜론과 화살표를 찾아 줄 번호와 함께 Claude에게 알린다. 막지는 않는다.

## 경위

- 다른 프로젝트의 세션이 inbox로 건의했다. 구현 agent가 CLAUDE.md에서 세미콜론으로 절을 이은 곳 여섯 군데를 남겼고, review가 이를 잡은 뒤에야 고치는 commit을 따로 만들었다.
- `user/shared/rules/korean-writing.md`의 "문장 연결" 규칙 가운데 세미콜론과 화살표는 기호 하나로 정해진다. 이 repo는 ADR 0116부터 이 기호를 `bin/check-integrity`로 잡지만 대상은 ADR뿐이다. 다른 Markdown에서는 review가 잡을 때까지 남는다.

## 결정

- 건의를 고쳐서 받았다. 고친 곳은 셋이다.
  - **Edit는 편집이 끝난 파일 전체로 판정한다.** 건의는 `new_string`만 따로 보자고 했다. 그러면 기존 code fence 안의 줄을 고칠 때 fence 표시 줄이 `new_string`에 없어서 code를 산문으로 읽는다. 그래서 code fence와 frontmatter는 파일 전체로 판정하고, 기호는 `new_string`이 차지한 자리에서만 찾는다. 원래 있던 글은 같은 줄에 있어도 지적하지 않는다. 알리는 줄 번호도 파일의 줄 번호가 된다.
  - **기호와 건너뛰는 곳을 `bin/check-integrity`에 맞춘다.** 기호는 `→ ← ⇒ ⇐ ↔ -> => ;`이다. 건너뛰는 곳은 code fence, 표 줄, 인용 줄, inline code, 큰따옴표 안, 링크 주소이고, 여기에 건의대로 frontmatter를 더했다.
  - **알리는 방법은 `hookSpecificOutput.additionalContext`다.** 공식 hooks 문서는 이 필드를 tool 결과와 함께 Claude의 context에 더하는 문자열로 설명한다. 막지 않고 알리기만 하려는 목적에 맞다.
- 대시와 슬래시는 건의대로 찾지 않는다. 규칙이 라벨 구분자, 제목 구분자, 경로, 단위에 이 기호를 허용하므로 기계로 가려내기 어렵다.
- hook은 Python 3.9에서도 돌게 썼다(ADR 0094).

## Consequences

- `tests/test_flag_prose_symbols.py`에 test 다섯을 더했다. Write가 산문 줄을 알리는지, 규칙이 허용하는 자리를 건너뛰는지, Edit가 새로 쓴 자리만 보는지, 기존 code fence 안의 Edit를 건너뛰는지, Markdown이 아닌 파일을 건너뛰는지를 본다. Python 3.15.2와 3.9.6에서 모두 통과했다.
- 설치된 경로에서도 확인했다. 이 세션에서 scratchpad의 `.md` 파일을 Write와 Edit로 쓰자, 산문의 세미콜론 줄과 새로 쓴 화살표 줄만 메시지로 들어왔다. inline code 안의 세미콜론과 Edit 전부터 있던 줄은 알리지 않았다.
- commit message와 PR 본문은 잡지 못한다. Bash의 heredoc이나 `--body-file`로 쓰기 때문이다. PR 본문을 먼저 Write로 파일에 쓰면 잡힌다.
- 기호 regex가 hook과 `bin/check-integrity` 두 곳에 있어서, 한쪽만 고치면 판정이 갈라진다. 한 곳으로 모으는 일은 따로 정한다.
