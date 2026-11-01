# 0110 — 다른 세션에 주는 지시서에 자기 commit trailer 값을 적지 않는다

`user/shared/CLAUDE.md` 3절에 한 항목을 더했다. 다른 Claude Code 세션에게 일을 맡기는 지시서에 자기 trailer 값(`Claude-Session` 등)을 옮겨 적지 않고, 그 세션이 자기 system reminder가 준 trailer를 쓰게 한다.

## 경위

- 다른 프로젝트의 세션이 inbox에 남긴 건의(ADR 0098)에서 왔다. 그 세션은 herdr로 띄운 agent들에게 지시서를 주면서 자기 `Claude-Session` 줄을 그대로 적었고, agent들은 지시대로 그 값을 commit에 붙였다. 건의에 따르면 그날 agent가 만든 commit 수십 개가 실제로 작업한 세션이 아니라 지시한 세션의 것으로 기록됐다. 건의가 인용한 commit 셋을 열어 trailer가 지시한 세션의 값임을 확인했다.

## 결정

- **건의가 대상으로 잡은 herdr skill은 고치지 않는다.** `skills/herdr`는 `copied` 항목이다. 로컬 수정이 있으면 `bin/re-pin`이 그 항목을 건너뛰므로, herdr release마다 손으로 다시 넣어야 한다.
- **`user/shared/CLAUDE.md`에 둔다.** 이 문제는 herdr뿐 아니라 다른 Claude Code 세션에게 지시서를 쓰는 모든 경우에 생기고, agent 하나만 띄워도 생긴다.
