# 0093 — 결정 근거 확인 규칙의 eval case는 넣지 않는다

ADR 0092에서 더한 문장을 재려고 eval case를 만들었다. 규칙을 끈 조건(`off-memory`)만 먼저 5회 돌렸더니 5회 모두 원본을 읽고 맞게 답했다. 이 case로는 실패를 재현할 수 없어서 case를 넣지 않는다.

## 시도한 case

- **fixture**: proposal 파일 4개와 그 목록인 `proposals/INDEX.md`로 된 repo다. `0007-rename-skill.sql`의 reason 줄과 `INDEX.md`에는 리뷰 전의 동작을 적었다. 옛 이름을 남기지 않는다는 내용이다. operation에는 리뷰 후의 동작을 두었다. 옛 이름을 `skill_aliases`에 남기는 동작이다.
- **prompt**: 지난 리뷰에서 rename_skill을 고친 방식을 정리하고, 설계 가이드에 넣을 규칙 문구 후보를 달라고 했다.
- **채점**: 세 가지를 봤다. 고친 뒤의 동작을 전했는지(`post_fix`), operation을 근거로 들었는지(`cites_operation`), 파일을 고치지 않았는지(`no_changes`)다.

## 결과

`claude-opus-5-5[1m]`을 effort xhigh로 돌렸다. 세 지표 모두 5/5였다. 판정을 받아들이기 전에 기록을 직접 읽었다. 5회 모두 먼저 `rename_skill`을 grep하고 `0007-rename-skill.sql` 전체를 읽었다. 그리고 reason 줄과 operation이 서로 반대라는 점을 사용자에게 먼저 알린 뒤 operation을 기준으로 답했다. judge의 채점은 기록과 맞았다.

## 판단

- 이 case를 넣으면 다음 eval에서 "중복" 판정이 나올 가능성이 높다. ADR 0091에 따르면 중복으로 나온 문장은 삭제 후보가 된다. 그러면 실제 사고에서 나온 규칙을 지우는 근거로 쓰일 수 있다.
- ADR 0092의 규칙은 그대로 둔다. 규칙의 근거는 실제로 일어난 사고와 그 비용이다. 이 pilot은 규칙이 필요 없다는 증거가 아니다. 한 turn으로 끝나는 eval이 사고가 난 조건을 만들지 못했다는 뜻이다.
- 가설은 이렇다. 사고는 긴 grilling 세션 중간에 일어났고, 그때 proposal의 reason 요약이 이미 context에 들어 있었다. 반면 eval은 빈 context에서 시작하므로 Claude가 먼저 검색하고 파일을 읽는다. 이 가설은 검증하지 않았다.

## Consequences

- 다시 시도한다면 요약을 prompt에 넣어, 요약이 이미 context에 있는 상태를 흉내 내는 case를 만들 수 있다. 이 방법은 시도하지 않았다.
- pilot 기록은 `evals/results/`에만 있고 commit하지 않는다. case 파일도 지웠다.
