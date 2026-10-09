# 0081 — 리뷰에서 나온 문서 수정과, 합의와 다르게 둔 것의 기록

`8f93ba0` 이후의 변경을 Standards와 Spec 두 축으로 리뷰한 결과 가운데 문서에 관한 것을 고쳤다. 도구 쪽은 ADR 0079와 ADR 0080이 다룬다. 이 ADR은 고치지 않기로 한 것과, `/grill-with-docs`의 합의와 다르게 구현하고도 밝히지 않았던 것도 함께 적는다.

## 고친 것

- **한국어 작성 규칙 2, 접사로 만든 말**: ADR 0070, 0078, 0080의 "미commit", "미push", "미채택"을 풀어 썼다.
- **re-pin을 용어로 등록**: "재pin"과 "재adopt"도 같은 규칙에 걸린다. ADR 0050부터 써 온 말이지만 용어집에 없었다. `CLAUDE.md`와 도구가 이미 쓰는 원어 "re-pin"을 `GLOSSARY.md`에 올리고, ADR 0069부터 0080까지의 표기를 그것으로 맞췄다. 그 이전 ADR은 기록이므로 고치지 않았다.
- **한 개념에 한 용어**: ADR 0074와 0076에서 "command"와 "명령"이 섞여 있던 것을 "명령"으로 맞췄다.
- **과압축한 제목**: ADR 0069와 0071의 "실질 변경 요약"을 "바뀐 내용"으로 바꿨다.
- **세미콜론으로 이은 절**: `CLAUDE.md`와 `tests/run.sh`의 새 문장을 두 문장으로 나눴다.
- **추적의 정의**: `GLOSSARY.md`의 정의가 도구 code의 "tracked path"를 설명하지 못했다. upstream 경로를 pin과 비교해 지켜보는 일로 고치고 그 경로를 tracked path라고 부른다고 적었다.
- **빠뜨린 용어 교체**: ADR 0074는 문서 세 개와 script 두 개만 고쳤다. `user/shared/mcp/README.md`와 선언 README 16개에 "provenance-only"와 "tracked plugin"이 남아 있었고, `mcp/README.md`는 README에서 없앤 "deliberately does NOT manage" 절을 가리키고 있었다. 모두 고쳤다.
- **`CLAUDE.md`의 중복 설명**: "Check a machine" 절이 `bin/check-machine --help`의 내용을 다시 적고 있었다. 언제 돌리는지와 재현 완료의 정의만 남겼다. `--deep`과 re-pin 경고의 설명도 도구가 출력하는 내용을 나열하지 않게 줄였다. `check-updates` skill 문서가 scan의 한계를 두 번 적던 것은 한 번으로 줄였다.
- **`CLAUDE.md`의 Scope 절**: 합의는 분류 원칙 세 줄과 README를 가리키는 한 줄만 두는 것이었다. `list_owned_links` 지시가 그 절에 들어가 있어서, 그것이 쓰이는 "Add a self-authored item" 절로 옮겼다.
- **keybinding**: "keybinding 파일은 만들면 소유"라는 합의가 어디에도 적혀 있지 않았다. README의 Scope 절에 적었다.

## 합의와 다르게 두었고 여기서 밝히는 것

- **commit하지 않은 변경을 repo 전체에서 센다.** 합의는 "소유 경로의 변경"이었다. 범위를 좁히면 `bin/`의 도구나 `docs/SECRETS.md`의 변경이 빠지는데, 그것들도 원격에 없으면 재현되지 않는다.
- **README의 재현 절차에서 로그인이 2번 단계다.** 합의한 순서는 secret 입력 뒤였다. plugin을 설치하려면 session이 먼저 있어야 하므로 합의한 순서가 틀렸다.
- **"upstream branch가 없다"는 경고가 있다.** 합의한 경고 목록에 없었다. 없애면 upstream이 없는 repo에서 push하지 않은 commit을 세지 못한 채 조용히 통과한다.
- **`CLAUDE.md`가 "동작을 추가하거나 고칠 때마다 check를 추가한다"고 지시한다.** 합의는 "`bin/`을 고치면 `tests/run.sh`를 돌린다" 한 줄이었다. `lib/`도 도구 code라서 범위에 넣었고, check 추가 지시는 test가 도구와 함께 자라게 하려고 넣었다.

## 고치지 않은 것

- **`264ad77`에 `Source-Repo` trailer가 없다.** 새 skill 세 개를 adopt한 commit이라 `CLAUDE.md`가 요구하는 형식에 어긋난다. 이미 push한 commit이어서 고치려면 원격 history를 다시 써야 한다.
- **`pr/SKILL.md`의 frontmatter에 upstream의 credit이 있다.** "출처는 sidecar에만 둔다"는 guardrail의 문구에는 어긋나지만 upstream에서 복사한 내용이다. 고치면 upstream과 달라지고 다음 re-pin 때 덮어쓰인다.
- **template skill에 느슨한 `/token` 검사를 적용하지 않는다.** ADR 0076에 적은 이유 그대로다.

## Consequences

- 리뷰가 낸 29건 가운데 3건은 고치지 않았고, 4건은 구현을 두고 이 ADR에 사유를 적었다. 나머지는 ADR 0079, 0080과 이 ADR에서 고쳤다.
- ADR 0069부터 0080까지의 본문을 고쳤다. 바꾼 것은 표기뿐이고 결정의 내용은 그대로다.
