# 0151 — 2026-11-26 rule의 "기호로 쓰인 파일"을 되돌리고, skill 복사본은 좁은 문구를 유지

[[0148-korean-review-copies-rule-into-skill]]에서 rule로 옮긴 문구 세 곳 가운데 "기호로 절을 이은 파일"을 rule에서만 "기호로 쓰인 파일"로 되돌렸다. `korean-review`의 복사본은 그대로 두고, 두 문구의 차이를 `claude-ai/copies.json`의 `replace`에 적었다.

## 되돌린 이유

- 0148은 이 문구를 옮기기 전에 기록을 확인하지 않았다. [[0121-self-check-korean-rule]]은 같은 세 곳을 "근거가 약한 세 건"으로 받지 않았고, [[0102-unpack-korean-rule-sentences]]는 이 문장의 범위를 좁히는 다른 안을 "문체 전염을 막는 범위가 좁아졌다"는 이유로 받지 않았다.
- 이 문장은 [[0045-sentence-joining-rule]]이 넣었다. 그 ADR은 원인으로 "사용자 지침 파일 자체가 '규칙 — 이유', 'A → B' 문체의 본보기였다"를 들었다. "규칙 — 이유"는 지금 rule이 허용하는 라벨 구분자 꼴이므로, 절을 잇지 않는 기호도 문체를 옮긴다. "기호로 절을 이은 파일"은 그런 파일을 대상에서 뺀다.
- `flag-prose-symbols.py` hook은 세미콜론과 화살표만 잡는다. 그래서 Claude Code에서 대시와 슬래시는 이 문장이 막아야 한다.

## skill을 그대로 둔 이유

- rule은 Claude Code에서만 로드되고, skill은 claude.ai와 Claude Code 양쪽에서 쓰인다. Claude Code에서 skill을 쓰면 더 넓은 rule이 함께 로드되므로, 복사본의 문구가 좁아도 적용 범위가 줄지 않는다.
- 사용자가 claude.ai chat에서 고친 skill로 eval을 여러 번 돌려 확인했다. skill을 바꾸지 않으므로 다시 올릴 일도 없다.

## rule에 반영하지 않은 것

- "두 뜻으로 읽히거나"와 "용어를 잇는 산문"은 rule에 그대로 둔다. 0121은 근거가 약하다고만 했고, 바꾼 문구가 더 직접적으로 읽힌다.
- skill 복사본에서 뺀 네 곳은 rule에 남긴다. 영어 적용 문장과 영어의 en-dash는 Claude Code에서 쓰는 영어 commit과 문서에 필요하다([[0045-sentence-joining-rule]], [[0046-sentence-joining-principle-first]]). 이 repo의 최근 commit 제목 100개는 모두 영어다. 용어집 절은 원칙 1이 외래어 경계를 넘긴 곳이다([[0047-term-boundary-and-middle-dot]]). 과압축 절의 전례 표기는 남길 근거도 뺄 근거도 약해서 두었다.
- skill의 AI slop 항목은 rule에 넣지 않는다. rule 크기의 57%에 해당하는 내용이 모든 세션에 로드된다. 또 "하지 않은 일과 문제없는 것 보고" 항목은 확인 방법을 보고하라는 `user/shared/CLAUDE.md`의 지시, 그리고 건너뛴 단계를 밝히라는 하네스 지시와 부딪친다. ADR과 `inbox/`에서 Claude Code가 쓴 AI slop 사례도 찾지 못했다([[0126-korean-writing-rule-and-review-skill]]의 기준).

## Consequences

- `copies.json`의 `replace`에 뺀 부분뿐 아니라 바꾼 문구도 들어간다. `claude-ai/README.md`와 `CLAUDE.md`의 설명을 그에 맞게 넓혔다.
- 이 ADR의 근거는 대부분 ADR에 남은 판단과 관찰이다. 영어 적용 문장, en-dash, "기호로 쓰인 파일" 문장의 효과를 잰 eval은 없다.
