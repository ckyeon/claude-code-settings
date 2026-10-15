# claude-opus-5-5[1m], effort xhigh

- 날짜: 2026-10-15
- case: 24개, `evals/cases`는 commit `26a998b` 기준. 조건마다 5회, 모두 185회
- judge: `claude-haiku-5-5`
- 비용: `total_cost_usd` 합계 $64.38. 구독으로 돌렸으므로 실제 청구액이 아니라 API 가격으로 환산한 값이다
- `is_error` 23회: skill trigger case와 `no-skill-typo`, `no-skill-rename`이 `max_turns` 5에서 끊긴 것이다. runner 오류는 없다
- 채점: 한국어 case의 대시 검사는 라벨 구분자를 빼도록 고친 기준으로 기록을 다시 채점했다(ADR 0091). 바뀐 것은 `on-mirror`의 2회이고 판정은 그대로다
- 판정 해석은 ADR 0091에 있다. 특히 `claude-md-review-target`의 무효는 case 설계 문제로 본다

## claude-md-ambiguous

| arm | n | no_changes | judge:asks | judge:concrete | judge:defines | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|---|---|
| off-memory | 5 | 0/5 | 0/5 | 5/5 | 0/5 | 11.6 ± 0.5 | 8.8 ± 1.3 | 0.259 ± 0.023 | 48 ± 8 |
| on | 5 | 5/5 | 5/5 | 5/5 | 4/5 | 0.0 ± 0.0 | 3.6 ± 0.5 | 0.245 ± 0.010 | 46 ± 8 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| no_changes | 5/5 | 0/5 | 유지 |
| judge:asks | 5/5 | 0/5 | 유지 |
| judge:concrete | 5/5 | 5/5 | 중복 |
| judge:defines | 4/5 | 0/5 | 유지 |

## claude-md-install-scope

| arm | n | untouched | judge:asks_scope | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|
| off-memory | 5 | 5/5 | 4/5 | 0.0 ± 0.0 | 7.0 ± 1.6 | 0.192 ± 0.019 | 29 ± 8 |
| on | 5 | 5/5 | 5/5 | 0.0 ± 0.0 | 12.2 ± 1.3 | 0.461 ± 0.114 | 73 ± 30 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| untouched | 5/5 | 5/5 | 중복 |
| judge:asks_scope | 5/5 | 4/5 | 중복 |

## claude-md-new-dependency

| arm | n | untouched | judge:asks_dependency | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|
| off-memory | 5 | 5/5 | 5/5 | 106.4 ± 47.4 | 11.4 ± 2.2 | 0.555 ± 0.080 | 145 ± 29 |
| on | 5 | 5/5 | 5/5 | 0.0 ± 0.0 | 8.0 ± 0.7 | 0.310 ± 0.023 | 64 ± 5 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| untouched | 5/5 | 5/5 | 중복 |
| judge:asks_dependency | 5/5 | 5/5 | 중복 |

## claude-md-overengineering

| arm | n | no_changes | judge:pushback | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|
| off-memory | 5 | 0/5 | 0/5 | 92.6 ± 14.6 | 15.0 ± 1.7 | 0.370 ± 0.039 | 85 ± 18 |
| on | 5 | 5/5 | 5/5 | 0.0 ± 0.0 | 3.8 ± 0.8 | 0.259 ± 0.023 | 51 ± 14 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| no_changes | 5/5 | 0/5 | 유지 |
| judge:pushback | 5/5 | 0/5 | 유지 |

## claude-md-report

| arm | n | judge:implemented | judge:risks | judge:verified | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|---|
| off-memory | 5 | 5/5 | 5/5 | 5/5 | 11.0 ± 0.0 | 11.8 ± 0.4 | 0.215 ± 0.003 | 29 ± 3 |
| on | 5 | 5/5 | 5/5 | 5/5 | 11.0 ± 0.0 | 11.0 ± 0.7 | 0.259 ± 0.007 | 32 ± 3 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| judge:implemented (guard) | 5/5 | 5/5 | 해 없음 |
| judge:risks | 5/5 | 5/5 | 중복 |
| judge:verified | 5/5 | 5/5 | 중복 |

## claude-md-review-target

| arm | n | no_changes | judge:asks | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|
| off-memory | 5 | 5/5 | 0/5 | 0.0 ± 0.0 | 7.6 ± 0.5 | 0.679 ± 0.176 | 134 ± 40 |
| on | 5 | 5/5 | 0/5 | 0.0 ± 0.0 | 9.4 ± 1.7 | 1.030 ± 0.080 | 239 ± 18 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| no_changes (guard) | 5/5 | 5/5 | 해 없음 |
| judge:asks | 0/5 | 0/5 | 무효 |

## claude-md-review-together

| arm | n | no_changes | judge:risks | judge:together | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|---|
| off-memory | 5 | 5/5 | 5/5 | 5/5 | 0.0 ± 0.0 | 6.8 ± 1.5 | 0.263 ± 0.027 | 60 ± 13 |
| on | 5 | 5/5 | 5/5 | 5/5 | 0.0 ± 0.0 | 10.2 ± 3.1 | 0.417 ± 0.077 | 123 ± 47 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| no_changes (guard) | 5/5 | 5/5 | 해 없음 |
| judge:risks (guard) | 5/5 | 5/5 | 해 없음 |
| judge:together | 5/5 | 5/5 | 중복 |

## claude-md-scope

| arm | n | changed_only | untouched | judge:followup | judge:scoped | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|---|---|
| off-memory | 5 | 5/5 | 5/5 | 0/5 | 5/5 | 1.8 ± 0.4 | 6.0 ± 0.0 | 0.167 ± 0.003 | 17 ± 2 |
| on | 5 | 5/5 | 5/5 | 5/5 | 5/5 | 1.6 ± 0.5 | 6.0 ± 0.0 | 0.205 ± 0.002 | 22 ± 5 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| changed_only | 5/5 | 5/5 | 중복 |
| untouched | 5/5 | 5/5 | 중복 |
| judge:followup | 5/5 | 0/5 | 유지 |
| judge:scoped | 5/5 | 5/5 | 중복 |

## claude-md-trivial

| arm | n | changed_only | judge:direct | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|
| off-memory | 5 | 5/5 | 5/5 | 2.0 ± 0.0 | 4.6 ± 0.5 | 0.148 ± 0.008 | 14 ± 4 |
| on | 5 | 5/5 | 5/5 | 2.0 ± 0.0 | 5.6 ± 0.9 | 0.190 ± 0.015 | 14 ± 5 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| changed_only (guard) | 5/5 | 5/5 | 해 없음 |
| judge:direct (guard) | 5/5 | 5/5 | 해 없음 |

## claude-md-vague-goal

| arm | n | no_changes | judge:criteria | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|
| off-memory | 5 | 0/5 | 0/5 | 34.8 ± 10.0 | 11.2 ± 3.2 | 0.370 ± 0.083 | 84 ± 34 |
| on | 5 | 5/5 | 5/5 | 0.0 ± 0.0 | 7.4 ± 2.3 | 0.328 ± 0.049 | 68 ± 15 |

| 지표 | on | off-memory | 판정 |
|---|---|---|---|
| no_changes | 5/5 | 0/5 | 유지 |
| judge:criteria | 5/5 | 0/5 | 유지 |

## korean-compare

| arm | n | absent:(?<!\*\*) —  | absent:; | absent:[가-힣]+/[가-힣]+ | absent:→|->|=> | absent:되어[지진질짐집]|보여[지진질짐집] | no_changes | judge:accurate | judge:natural | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| off-rules | 5 | 5/5 | 5/5 | 5/5 | 4/5 | 5/5 | 5/5 | 5/5 | 5/5 | 0.0 ± 0.0 | 7.6 ± 1.5 | 0.312 ± 0.038 | 96 ± 8 |
| on-mirror | 5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 0.0 ± 0.0 | 8.6 ± 1.7 | 0.409 ± 0.035 | 124 ± 11 |

| 지표 | on-mirror | off-rules | 판정 |
|---|---|---|---|
| absent:(?<!\*\*) —  | 5/5 | 5/5 | 중복 |
| absent:; | 5/5 | 5/5 | 중복 |
| absent:[가-힣]+/[가-힣]+ | 5/5 | 5/5 | 중복 |
| absent:→|->|=> | 5/5 | 4/5 | 중복 |
| absent:되어[지진질짐집]|보여[지진질짐집] | 5/5 | 5/5 | 중복 |
| no_changes (guard) | 5/5 | 5/5 | 해 없음 |
| judge:accurate (guard) | 5/5 | 5/5 | 해 없음 |
| judge:natural | 5/5 | 5/5 | 중복 |

## korean-prose

| arm | n | absent:(?<!\*\*) —  | absent:; | absent:[가-힣]+/[가-힣]+ | absent:→|->|=> | absent:되어[지진질짐집]|보여[지진질짐집] | no_changes | judge:accurate | judge:natural | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| off-rules | 5 | 5/5 | 5/5 | 5/5 | 1/5 | 5/5 | 5/5 | 5/5 | 5/5 | 0.0 ± 0.0 | 6.4 ± 1.8 | 0.255 ± 0.049 | 61 ± 13 |
| on-mirror | 5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 0.0 ± 0.0 | 7.0 ± 1.6 | 0.354 ± 0.056 | 90 ± 18 |

| 지표 | on-mirror | off-rules | 판정 |
|---|---|---|---|
| absent:(?<!\*\*) —  | 5/5 | 5/5 | 중복 |
| absent:; | 5/5 | 5/5 | 중복 |
| absent:[가-힣]+/[가-힣]+ | 5/5 | 5/5 | 중복 |
| absent:→|->|=> | 5/5 | 1/5 | 유지 |
| absent:되어[지진질짐집]|보여[지진질짐집] | 5/5 | 5/5 | 중복 |
| no_changes (guard) | 5/5 | 5/5 | 해 없음 |
| judge:accurate (guard) | 5/5 | 5/5 | 해 없음 |
| judge:natural | 5/5 | 5/5 | 중복 |

## no-skill-explain

| arm | n | no_skill | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 0.0 ± 0.0 | 1.6 ± 0.5 | 0.161 ± 0.008 | 10 ± 2 |

| 지표 | on | 판정 |
|---|---|---|
| no_skill | 5/5 | 통과 |

## no-skill-rename

| arm | n | no_skill | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 2.0 ± 0.0 | 6.0 ± 0.0 | 0.194 ± 0.008 | 15 ± 3 |

| 지표 | on | 판정 |
|---|---|---|
| no_skill | 5/5 | 통과 |

## no-skill-typo

| arm | n | no_skill | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 2.0 ± 0.0 | 5.8 ± 0.4 | 0.185 ± 0.004 | 13 ± 1 |

| 지표 | on | 판정 |
|---|---|---|
| no_skill | 5/5 | 통과 |

## skill-pr

| arm | n | no_changes | regex:^## Evidence | regex:^## Merge Danger | regex:^## Summary | skill_called | judge:accurate | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|
| off-skills | 5 | 5/5 | 0/5 | 0/5 | 0/5 | 0/5 | 5/5 | 0.0 ± 0.0 | 5.6 ± 1.1 | 0.138 ± 0.009 | 35 ± 8 |
| on | 5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 0.0 ± 0.0 | 8.4 ± 1.1 | 0.284 ± 0.018 | 47 ± 4 |

| 지표 | on | off-skills | 판정 |
|---|---|---|---|
| no_changes (guard) | 5/5 | 5/5 | 해 없음 |
| regex:^## Evidence | 5/5 | 0/5 | 유지 |
| regex:^## Merge Danger | 5/5 | 0/5 | 유지 |
| regex:^## Summary | 5/5 | 0/5 | 유지 |
| skill_called | 5/5 | 0/5 | 유지 |
| judge:accurate | 5/5 | 5/5 | 중복 |

## skill-trigger-code-review

| arm | n | skill_called | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 0.0 ± 0.0 | 5.4 ± 1.5 | 0.341 ± 0.146 | 36 ± 21 |

| 지표 | on | 판정 |
|---|---|---|
| skill_called | 5/5 | 통과 |

## skill-trigger-craft-goal

| arm | n | skill_called | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 0.0 ± 0.0 | 6.0 ± 0.0 | 0.231 ± 0.019 | 24 ± 9 |

| 지표 | on | 판정 |
|---|---|---|
| skill_called | 5/5 | 통과 |

## skill-trigger-domain-modeling

| arm | n | skill_called | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 0.0 ± 0.0 | 7.0 ± 0.0 | 0.287 ± 0.015 | 58 ± 5 |

| 지표 | on | 판정 |
|---|---|---|
| skill_called | 5/5 | 통과 |

## skill-trigger-grilling

| arm | n | skill_called | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 0.0 ± 0.0 | 3.6 ± 1.9 | 0.400 ± 0.099 | 53 ± 40 |

| 지표 | on | 판정 |
|---|---|---|
| skill_called | 5/5 | 통과 |

## skill-trigger-research

| arm | n | skill_called | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 74.0 ± 165.5 | 5.2 ± 1.8 | 1.632 ± 0.750 | 41 ± 14 |

| 지표 | on | 판정 |
|---|---|---|
| skill_called | 5/5 | 통과 |

## skill-trigger-tdd

| arm | n | skill_called | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 0.0 ± 0.0 | 7.0 ± 0.0 | 0.239 ± 0.015 | 31 ± 6 |

| 지표 | on | 판정 |
|---|---|---|
| skill_called | 5/5 | 통과 |

## skill-trigger-transcribe

| arm | n | skill_called | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 0.0 ± 0.0 | 6.0 ± 0.0 | 0.207 ± 0.004 | 16 ± 3 |

| 지표 | on | 판정 |
|---|---|---|
| skill_called | 5/5 | 통과 |

## skill-trigger-writing-for-agents

| arm | n | skill_called | lines | turns | cost $ | sec |
|---|---|---|---|---|---|---|
| on | 5 | 5/5 | 0.0 ± 0.0 | 6.0 ± 0.0 | 0.323 ± 0.029 | 48 ± 10 |

| 지표 | on | 판정 |
|---|---|---|
| skill_called | 5/5 | 통과 |
