# 0070 — 구조 scan이 추적 디렉터리 밖의 새 skill과 plugin도 보고한다

2026-10-09 점검에서 `check-updates --deep`은 mattpocock/skills의 신규 항목을 3건으로 보고했지만 실제로는 4건이었다. `skills/in-progress/chief-of-staff`가 빠졌다. ADR 0037의 구조 scan은 추적 path의 부모 디렉터리만 비교하는데, 이 repo가 mattpocock에서 adopt한 항목은 `skills/engineering`과 `skills/productivity`에만 있기 때문이다. 같은 이유로 vercel/next.js의 `.agents/skills/docs-diagrams`도 보이지 않았다. 보고서는 scan 범위를 밝히지 않았고, 그래서 "신규 5건"이 전체처럼 읽혔다.

구조 scan에 repo 전체를 보는 두 번째 pass를 더했다. pin과 head에서 `git ls-tree -r`로 전체 경로를 뽑고, marker 파일인 `SKILL.md`나 `.claude-plugin/plugin.json`이 새로 생긴 디렉터리를 `NEW … (outside tracked dirs)`로 보고한다. 다음 셋은 뺀다.

- 첫 번째 pass가 이미 `NEW`로 보고한 항목과 그 안쪽
- 추적 path 안쪽. 해당 항목의 diff가 다룬다.
- 다른 skill이나 plugin 안에 중첩된 항목. 바깥 항목이 새것이면 그것만 보고하고, 예전부터 있던 것이면 adopt하지 않기로 한 단위의 일부다.

`deep.json`의 `structure` record에는 `scope` 필드가 생겼다. 첫 번째 pass는 `sibling`, 두 번째 pass는 `elsewhere`다. 기존 key는 그대로다.

`bin/adopt`의 re-pin 경고(ADR 0039)에도 같은 비교를 넣었다. 두 도구가 같은 구조 검사를 한다는 전제를 유지하기 위해서다.

`check-updates` skill 문서는 두 가지를 요구하도록 고쳤다. 신규 항목마다 adopt 여부를 따로 묻고, 구조 변경 보고 끝에 scan이 본 범위를 한 줄로 밝힌다.

## Considered Options

- **부모의 형제 디렉터리까지 넓히기**: mattpocock에는 맞는다. 하지만 추적 path의 부모가 repo 최상위 바로 아래인 next.js(`skills`)와 claude-plugins-official(`plugins`)에서는 최상위 디렉터리 전부가 대상이 되어 예외 규칙이 필요하다. 기각했다.
- **scan 범위만 출력하기**: 변경이 가장 작지만 새 skill을 찾아 주지 않는다. 기각했다.
- **beta 디렉터리를 거르는 ignore 목록**: 넣지 않았다. pin 대비 비교라서 같은 항목은 pin을 옮기기 전까지만 뜬다. 설정을 하나 더 만들 만큼의 잡음이 아니다.

## Consequences

- upstream의 beta 디렉터리나 기여자용 skill이 새로 생기면 한 번씩 보고된다. 어떤 디렉터리인지는 판단 subagent가 README를 읽어 덧붙인다.
- marker 파일이 없는 agent, command, hook, MCP server는 여전히 추적 path의 부모 디렉터리 안에서만 잡힌다. skill 문서가 보고에 이 한계를 적게 한다.
- 한 source의 항목 여러 개를 `bin/adopt`로 연달아 re-pin하면 같은 `(outside tracked dirs)` 경고가 항목마다 반복된다.
- source마다 `git ls-tree -r`이 두 번 더 돈다. tree만 읽으므로 blobless clone에서 blob을 받지 않는다.

## 검증

- 실제 mattpocock/skills(`959a8e9f`에서 `49dd158d`)로 돌려 `chief-of-staff`가 `(outside tracked dirs)`로 나오고, `implement-spec`, `pr`, `retro`가 한 번씩만 나오며, 예전부터 있던 `skills/misc`와 `skills/in-progress`의 나머지는 나오지 않는 것을 확인했다.
- 가짜 `file://` upstream으로 경계 사례를 확인했다. 추적 path 안의 새 `SKILL.md`, 예전부터 있던 adopt하지 않은 plugin 안의 새 skill, adopt하지 않은 skill 안에 중첩된 새 skill은 보고되지 않는다. 새 plugin은 안쪽 skill과 묶여 한 줄로 나온다. ASCII가 아닌 경로도 잡힌다. 첫 adopt와 구조 변화가 없는 re-pin은 경고하지 않는다.
