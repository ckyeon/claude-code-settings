# 0090 — eval 과제를 24개로 넓히고, skill은 trigger만 한 조건으로 잰다

pilot의 4개 case만으로는 판정을 내릴 수 없었다(ADR 0087). 과제를 CLAUDE.md 규칙, 한국어 rule, skill trigger에 걸쳐 넓혔다.

## 결정

- **중단 기록에서 3개를 가져왔다.** session 197개의 중단 44건 가운데 모델 행동이 어긋난 것은 4건이었다. 나머지는 사용자가 요청을 보충하려고 멈췄거나, 생각을 바꿨거나, 실수였다. 직후에 "plz continue"류를 적은 경우를 실수로 봤다. 4건 가운데 3건을 case로 만들었다.
  - `claude-md-review-target`: 대상이 둘로 읽히는 "리뷰해."
  - `claude-md-review-together`: 자동 review script가 있는 repo에서 "같이 리뷰해보자". fixture의 script는 실제로 돌 수 있게 허용했다.
  - `claude-md-install-scope`: scope를 정하지 않은 plugin 설치 요청
  - 나머지 1건은 hookify를 쓰지 않고 hook을 만든 일인데, 사용자에 따르면 불만이 아니라 궁금해서 물은 것이어서 뺐다.
- **CLAUDE.md 규칙에서 4개를 더했다.** 막연한 목표, 의존성 유혹, 과한 설계 요청, 여러 파일 변경 뒤의 보고다. "새 개념은 처음 쓸 때 정의한다"는 `claude-md-ambiguous`의 rubric으로 넣었다. public API 변경은 의존성 case와 같은 "Ask first" 문장에 속해 뺐고, test 관례는 pilot에서 두 조건이 같아서 뺐다.
- **한국어 case를 하나 더했다.** `korean-compare`는 장단점 비교라 슬래시를 부르기 쉽다. 한글 사이 슬래시 검사를 두 한국어 case에 넣었다.
- **skill은 trigger만, `on` 한 조건으로 잰다.** skill을 끈 조건에서는 skill이 불릴 수 없어 비교할 것이 없다. 조건이 하나인 case는 통과율이 0.8 이상이면 통과, 0.2 이하면 실패로 판정한다. `max_turns`는 5로 묶었다. 대상은 모델이 부를 수 있는 8개다(`code-review`, `writing-for-agents`, `domain-modeling`, `tdd`, `transcribe`, `grilling`, `research`, `craft-goal`). 아무 skill도 불리면 안 되는 요청 3개를 함께 둔다.
- **사용자만 부를 수 있는 skill은 eval하지 않는다.** `implement`, `ask-matt`, `grill-me`, `handoff`, `to-questionnaire`, `wait-what`은 `disable-model-invocation: true`라 trigger를 잴 수 없다. 그중 40일 동안 쓰이지 않은 4개는 사용 기록을 보고 사용자가 정한다.
- **`skill_called`는 이름이 정확히 같아야 통과한다.** user skill `code-review`와 plugin skill `engineering:code-review`가 콜론 뒤 이름이 같다. `no_skill` 검사를 더했다.

## 확인한 것

haiku로 24개를 조건마다 한 번씩, 모두 37회 돌렸다. runner 오류는 없었다. trigger case에서 불리지 않은 4건은 skill을 부르기 전에 끊긴 것이 아니라 skill 없이 일을 시작한 것이었다.

## Consequences

- `claude-opus-5-5[1m]`과 effort xhigh로 조건마다 5회 돌리면 185회 실행이다.
- skill의 출력 효과는 `pr`만 잰다. 다른 skill은 trigger가 통과한 것 가운데 필요한 것을 골라 효과 case를 더한다.
