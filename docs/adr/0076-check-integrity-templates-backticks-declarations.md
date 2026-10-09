# 0076 — check-integrity가 template skill, backtick 호출, 선언의 완결성을 검사한다

ADR 0074에서 정한 범위가 지켜지는지를 도구가 확인하도록 `bin/check-integrity`를 세 가지로 넓혔다.

- **template skill의 참조 검사**: 지금까지는 `user/shared/skills`의 30개만 검사했다. `project-templates/*/.claude/skills/`의 47개도 소유 대상이므로 skill 참조 검사를 적용한다. template skill의 참조는 같은 template의 skill과 user scope의 skill로 풀고, user scope의 skill은 template의 skill로 풀지 않는다.
- **backtick으로 쓴 Skill tool 호출**: `Skill tool with "tdd"`처럼 큰따옴표로 쓴 호출만 인식했는데, upstream mattpocock/skills가 `` Skill tool with `tdd` ``처럼도 쓰기 시작했다. `implement-spec`과 `retro`의 호출 3건이 검사 밖에 있었다.
- **선언의 완결성**: ADR 0074의 분류 원칙은 선언에 목록과 만드는 command가 함께 있어야 한다고 정한다. `user/shared/mcp/<name>/`의 README에 `claude mcp add`가, `user/shared/plugins/<name>/`의 README에 `plugin install`이 없으면 오류다. 선언한 plugin이 어느 `settings.json`에서도 활성화돼 있지 않거나, user scope에서 활성화한 plugin에 선언이 없으면 경고한다.

## template skill에는 참조 검사만 적용한다

user scope skill에 하는 frontmatter 검사, link 검사, 느슨한 `/token` 경고는 template skill에 적용하지 않았다. 전부 적용해 보니 오류 5건과 경고 1건이 나왔고, 모두 upstream에서 복사해 온 내용이었다.

- nextjs template의 `composition-patterns`, `react-best-practices`, `react-view-transitions`는 frontmatter의 name이 `vercel-`로 시작해 폴더 이름과 다르다. upstream의 폴더와 name이 원래 다르다.
- phaser template의 `cameras`와 `sprites-and-images`에서 link 검사가 `references/REFERENCE..//SKILL.md`를 깨진 link로 잡았다.
- `next-cache-components-adoption`의 `/about`은 route 예시인데 skill 참조 후보로 경고됐다.

이것들을 고치려면 복사본을 upstream과 다르게 만들어야 하고, 다음 재adopt 때 다시 덮어쓰인다. 그래서 template에는 이 repo가 책임질 수 있는 검사, 곧 참조가 풀리는지만 적용했다. 위 5건을 어떻게 할지는 정하지 않았다.

## Considered Options

- **선언에 없는 활성 plugin을 오류로 두기**: 경고로 두었다. `bin/check-machine`이 기기에서 같은 상황을 경고로 다루기로 했고(ADR 0078), `/plugin install` 직후 선언을 쓰기 전의 중간 상태에서 Stop hook이 막지 않게 하려는 것이다.
- **`/plugin install` 문자열만 인정하기**: `remotion`의 README는 `claude plugin install remotion@remotion --scope project`로 안내한다. 두 형식을 모두 인정하도록 `plugin install`을 찾는다.

## Consequences

- 출력의 "Checked N skills" 줄이 검사한 폴더마다 하나씩 나오고, 선언 개수를 적은 줄이 추가됐다. Stop hook과 `bin/adopt`는 종료 code만 보므로 영향이 없다.
- test 21개를 `tests/run.sh`에 추가했다.
