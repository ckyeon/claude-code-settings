# 0091 — `claude-opus-5-5[1m]` 기준선을 남기고, 확인하다 찾은 채점 문제를 고친다

ADR 0090의 case 24개를 `claude-opus-5-5[1m]`, effort xhigh로 조건마다 5회, 모두 185회 돌렸다. 요약은 `evals/history/2026-10-15-claude-opus-5-5_1m_-xhigh.md`에 남긴다. 판정을 받아들이기 전에 기록을 직접 읽었고, 그 과정에서 채점 기준 하나를 고쳤다.

## 판정

| 구성요소 | 판정 | 근거 |
|---|---|---|
| CLAUDE.md 1. Clarify | 유지 | 모호한 요청에 질문 5/5 대 0/5, 막연한 목표에 완료 기준 확인 5/5 대 0/5, 과한 설계 요청에 반론 5/5 대 0/5 |
| CLAUDE.md "Name what you use" | 유지 | 용어 정의 4/5 대 0/5 |
| CLAUDE.md 3. 범위 밖 발견은 summary로 | 유지 | follow-up 언급 5/5 대 0/5. 범위를 지키는 것 자체는 두 조건 모두 5/5라 중복 |
| CLAUDE.md "Ask first" 의존성 | 중복 | 두 조건 모두 의존성을 더하지 않았다. 다만 끈 조건은 코드를 먼저 쓰고 나중에 선택지를 말했다 |
| CLAUDE.md 보고 형식 | 중복 | 검증 방법과 위험을 두 조건 모두 5/5로 보고했다 |
| CLAUDE.md plugin 설치 scope 질문 | 중복 | 5/5 대 4/5 |
| CLAUDE.md "같이 리뷰" | 중복 | 두 조건 모두 5/5 |
| CLAUDE.md 단순 작업 | 해 없음 | 두 조건 모두 바로 고쳤다 |
| 한국어 rule | 일부 유지 | 흐름 설명의 화살표가 끈 조건에서 4/5 나왔다. 대시, 세미콜론, 슬래시, 이중피동은 두 조건 모두 없었다 |
| `pr` skill | 유지 | template 5/5 대 0/5 |
| skill trigger 8개 | 통과 | 모두 5/5 |
| skill이 불리면 안 되는 요청 3개 | 통과 | 모두 5/5 |

`claude-md-review-target`은 두 조건 모두 0/5로 무효가 나왔지만 설정의 문제로 보지 않는다. "리뷰해."가 10회 모두 `code-review` skill을 불렀고, skill은 branch의 diff를 리뷰 대상으로 정한다. 그런데 fixture의 사고 문서가 같은 branch commit에 들어 있어서, branch를 리뷰하면 사고 문서도 함께 리뷰된다. 원래 중단 기록에서 두 대상을 갈랐던 대화 맥락이 한 turn짜리 실행에는 없다. 이 case는 fixture를 다시 짜거나 빼야 한다. 결과에서 확인한 것은 하나다. skill이 불리면 skill의 절차가 CLAUDE.md의 Clarify보다 앞선다. 대상을 묻게 하려면 고칠 곳은 `code-review` skill이다.

## 비용

`total_cost_usd`를 조건별 평균으로 비교했다. 구독으로 돌렸으므로 API 가격으로 환산한 값이다.

- CLAUDE.md를 켜면 질문으로 멈추는 case에서는 더 싸다. 의존성 case는 $0.31 대 $0.56이다.
- 그대로 일하는 case에서는 20~59% 더 든다. plugin 설치 case는 2.4배인데, 켠 조건이 문서를 WebFetch로 확인했기 때문이다("Verify, don't recall").
- 한국어 rule을 켜면 31~39% 더 든다.

## 고친 것

- **대시 검사가 라벨 구분자를 위반으로 셌다.** `**LRU**(least recently used) — 설명`처럼 굵은 용어 뒤에 괄호가 붙으면 기존 패턴의 lookbehind가 라벨을 알아보지 못했다. rule은 라벨 구분자를 허용한다. `score_checks`가 본문에서 라벨 구분자의 대시를 빼고 검사한다. 기존 기록을 다시 채점하니 `on-mirror`의 2회만 바뀌었고 판정은 그대로였다.
- **하위 process가 실행한 쪽의 Claude Code 환경 변수를 물려받았다.** 이 기준선은 Claude Code session 안에서 띄웠으므로 `CLAUDECODE`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_EFFORT` 같은 값이 eval과 judge 모두에 들어갔다. 결과에 영향이 있었다는 근거는 찾지 못했다. Opus에 scratchpad 경로를 물어보니 두 환경 모두 없다고 답했다. 그래도 terminal에서 띄운 실행과 환경이 달라지므로, runner가 이 변수들을 빼고 하위 process를 띄운다.

## 확인한 것

- 핵심 판정의 기록을 조건마다 읽었다. judge의 채점은 기록과 맞았다. `claude-md-ambiguous`의 `defines`는 judge가 `dict`, `stdlib`까지 정의를 요구해 켠 조건 1회를 떨어뜨렸다. 엄격한 쪽으로 틀렸으므로 판정은 그대로 둔다.
- 28회가 repo 밖에 검증용 script를 썼다. `--work-root`를 이 session의 scratchpad 아래로 줬기 때문에, 모델이 경로의 `scratchpad`를 보고 그 상위 디렉터리에 썼다. Bash가 막혀 있어 이 script들은 실행되지 않았고 변경 집계에도 들어가지 않는다.

## Consequences

- 다음 모델은 같은 case로 돌리고 이 요약과 비교한다. `claude-md-review-target`을 고치면 그 case만 이 모델로 다시 돌려 기준선을 맞춘다.
- 중복으로 나온 CLAUDE.md 문장을 지울지는 사용자가 정한다. 지금 모델에서 차이가 없다는 것이지 해가 있다는 것은 아니다. 문장이 짧으면 context 비용도 작다.
