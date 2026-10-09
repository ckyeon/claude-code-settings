# 0077 — 필요한 secret의 이름과 넣는 위치를 `docs/SECRETS.md`에 선언한다

secret의 값은 범위 밖이다(ADR 0074). 그런데 새 기기에서 재현할 때 가장 먼저 막히는 곳이 "어떤 key가 필요하고 어디에 넣는가"였고, 그 정보는 README 네 곳과 skill 본문에 흩어져 있었다. `docs/SECRETS.md`에 secret의 이름, 쓰는 곳, 넣는 위치를 표 하나로 모았다. 값은 적지 않고, 얻는 방법은 각 선언의 README를 가리킨다.

지금 필요한 것은 다섯 가지다. context7 API key, GitHub PAT, `DISCORD_BOT_TOKEN`, `transcribe` skill의 `GEMINI_TRANSCRIBE_API_KEY`, codex plugin의 OpenAI 로그인이다. Claude 계정과 Linear는 붙여 넣을 값이 없는 로그인이라 따로 적었다.

## Considered Options

- **`bin/check-machine`이 secret의 존재까지 확인하기**: 하지 않았다. 목록을 도구가 읽는 형식으로 만들어야 하고, 도구가 secret이 든 파일을 열게 된다. secret이 다섯 개뿐이라 문서로 충분하다고 보았다. 실제 재현에서 여기서 막히면 그때 추가한다.

## Consequences

- key가 빠져도 `bin/check-machine`은 통과할 수 있다. 이 한계를 `docs/SECRETS.md`에 적었다.
- 선언에 secret이 필요해지면 같은 변경에서 이 표에 행을 추가해야 한다. `CLAUDE.md`의 guardrail에 그 지시를 넣었다. 이 규칙을 확인하는 도구는 없다.
