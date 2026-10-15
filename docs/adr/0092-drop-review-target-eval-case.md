# 0092 — `claude-md-review-target` case를 뺀다

ADR 0091에서 이 case의 무효 판정을 case 설계 문제로 봤다. 사고 문서를 branch commit에서 빼고 commit하지 않은 초안으로 둔 fixture로 다시 짜서, `claude-opus-5-5[1m]`, effort xhigh로 조건마다 5회 돌렸다. 결과는 켠 조건과 끈 조건 모두 0/5로 같았다.

10회 모두 `code-review` skill을 불렀고, 초안은 리뷰의 기준 문서로 썼다. 대화 맥락이 없는 상태에서 branch가 하나 있으면 "리뷰해."를 branch 리뷰로 읽는 것은 합리적이다. 원래 중단 기록의 대상이 둘로 갈린 것은 그 session이 처음부터 사고 이야기였기 때문인데, 한 turn짜리 `-p` 실행에서는 그 맥락을 재현할 수 없다. 그래서 이 case로는 CLAUDE.md의 Clarify가 효과 있는지 잴 수 없어 뺐다. case는 23개가 된다.

## 고려한 것

- **`code-review` skill을 고친다.** 하지 않는다. upstream에서 `copied`로 가져온 skill이라 로컬에서 고치면 `bin/re-pin`이 이 skill을 건너뛴다. 또 skill에는 기준점이 없으면 물으라는 단계가 이미 있는데, 모델이 skill을 부를 때 `main`을 직접 넘겨 그 단계를 건너뛰었다. 판단이 어긋나는 곳은 skill 안이 아니라 skill을 고르는 순간이다.
- **CLAUDE.md에 "skill을 고르기 전에도 묻는다"는 문장을 더한다.** 하지 않는다. 맥락 없는 "리뷰해."마다 대상을 묻게 되어 평소 branch 리뷰 요청에 쓸모없는 질문이 늘어난다.
- **case를 남겨 늘 무효로 나오는 기록으로 둔다.** 판정표를 읽을 때 헷갈리므로 빼는 쪽을 골랐다.
- 다시 짜면서 runner에 commit하지 않은 fixture 파일(`worktree/`)을 넣었는데, 이 case 말고는 쓰는 곳이 없어 되돌렸다.

## Consequences

- 대화 맥락을 따르는지는 이 eval의 범위 밖이다. `evals/README.md`의 한계에 적었다.
- `evals/history/`의 기준선 요약에는 이 case의 절이 남아 있지만 다음 모델과 비교하지 않는다고 적었다.
