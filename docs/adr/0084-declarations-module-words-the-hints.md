# 0084 — 선언한 항목과 그것을 만드는 명령을 `lib/declarations.py`가 직접 답한다

architecture 리뷰의 다섯 번째 후보다. 선언한 plugin의 정보가 `이름|marketplace|source|scope` 한 줄로 bash에 넘어갔다. 구분자, 칸 수, 정렬 순서가 호출자와의 약속이 됐다. `install.sh`는 정렬 순서에 기대어 marketplace마다 안내를 한 번만 찍었고, `bin/check-updates`는 bash를 불러 그 줄을 다시 쪼개면서 칸이 4개인지 검사했다. MCP server는 `lib/common.sh`에서 README가 있어야 선언이었고 `lib/declarations.py`에서는 폴더만 있으면 선언이었다. ADR 0079가 plugin에서 없앤 것과 같은 어긋남이다.

## 결정

- **MCP server도 폴더가 있으면 선언이다.** README가 없는 선언은 지금처럼 `bin/check-integrity`가 오류로 잡는다.
- **안내문을 module이 만든다.** "무엇을 실행하면 되는가"의 문장을 `lib/declarations.py`가 쓰고, `install.sh`와 `uninstall.sh`는 그것을 한 번 불러 출력한다.
- **`bin/check-updates`는 module을 직접 읽는다.** bash를 거치지 않는다.
- **구분자 줄을 내던 `list_declared_plugins`와 `list_declared_mcp_servers`를 없앴다.** `lib/common.sh`에는 OS 판별과 소유 경로 목록만 남는다.
- MCP server의 안내는 지금처럼 README를 가리킨다. README에서 명령을 뽑아내지는 않는다.

## Consequences

- 실제 repo에서 `install.sh`와 `uninstall.sh`의 출력은 고치기 전과 한 글자도 다르지 않다. 임시 `HOME`에서 두 script를 돌려 비교했다.
- 안내문에 처음으로 test가 붙었다. `tests/test_declarations.py` 11개가 module을 직접 확인하고, 명령줄 test는 두 script가 그 문장을 출력하는지 본다.
- plugin 정보에 칸을 더할 때 고칠 곳이 module 하나다.
