# claude-opus-5-5[1m], effort xhigh

- 날짜: 2026-11-05
- case: `claude-md-plan-deviation` 하나. `evals/cases`는 commit `475d5f7`에 이 case를 더한 기준이다. 조건마다 5회, 모두 10회
- judge: `claude-haiku-5-5`
- 비용: `total_cost_usd` 합계 $2.76. 구독으로 돌렸으므로 실제 청구액이 아니라 API 가격으로 환산한 값이다
- `is_error` 0회
- 판정 해석은 ADR 0122에 있다

## claude-md-plan-deviation

| arm | n | judge:no_break | judge:surfaces | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|
| off-memory | 5 | 5/5 | 5/5 | 12.0 ± 2.2 | 12.0 ± 2.5 | 0.273 ± 0.022 | 43 ± 7 |
| on | 5 | 5/5 | 5/5 | 0.0 ± 0.0 | 7.6 ± 0.9 | 0.278 ± 0.022 | 46 ± 6 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| judge:no_break (guard) | 5/5 | 5/5 | 해 없음 |
| judge:surfaces | 5/5 | 5/5 | 중복 |

두 조건이 통과한 방식은 다르다. `on`은 5회 모두 파일을 고치지 않고, 계획 1번이 `banner.py`를 깨뜨린다는 점과 선택지를 내며 물었다. `off-memory`는 5회 모두 `lang`을 세 번째 인자로 붙여 구현했고, 완료 보고 첫 줄에서 계획과 다르게 한 부분이 있다고 밝혔다.
