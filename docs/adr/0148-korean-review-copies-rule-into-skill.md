# 0148 — 2026-11-26 korean-review는 rule 사본을 SKILL.md에 두고, chat에서 고친 rule 문구를 rule에도 반영

사용자가 claude.ai chat에서 `korean-review`를 리뷰하고 고쳤다. 고친 SKILL.md는 `references/korean-writing.md`를 가리키지 않고, rule 본문을 "한국어 글쓰기 규칙" 절에 복사해 넣었다. 이 구조를 그대로 받았다. repo의 SKILL.md를 동기화된 사본과 바이트 단위로 같게 만들고 symlink를 지웠다. 이 skill에서는 [[0126-korean-writing-rule-and-review-skill]]의 symlink 결정이 더는 유효하지 않다.

## chat에서 바뀐 내용

- 빼도 독자가 잃는 정보가 없는 문장을 찾는 "AI slop 검사 항목"을 더했다.
- 글쓴이가 Claude인지에 따라 검사 기준의 적용 범위를 나눴다. 짧은 항목의 기호를 판단하는 절도 따로 두었다.
- 보고 형식을 템플릿으로 바꿨다. 표의 "지금" 열은 "원문"으로, "문장 밖에서 확인할 것" 절은 "확인할 내용"으로 이름을 바꿨다.
- 복사한 rule에서 리뷰에 쓰지 않는 네 곳을 뺐다. 영어로 쓸 때의 적용 문장, 영어의 범위 표기(en-dash), 과압축 절의 전례 표기, 프로젝트 용어집 컨벤션 절이다.
- 복사한 rule의 문구 세 곳을 고쳤다.

## Considered Options

- **symlink를 유지하고 rule 절만 reference 안내로 되돌린다**: 기각. rule이 한 벌로 남지만, 리뷰에 쓰지 않는 부분을 skill에서만 뺄 수 없다.
- **복사본을 그대로 받는다**: 채택. skill 안의 rule을 리뷰 용도에 맞게 줄일 수 있다. 사용자가 이 구조를 골랐다.

## rule 문구 반영

chat에서 고친 문구 세 곳을 `user/shared/rules/korean-writing.md`에도 옮겼다. 이제 rule과 복사본은 위에서 뺀 네 곳만 다르다.

- 원칙 1 끝 문장의 "두 의미를 떠안거나 … 원어로 복귀한다"를 "두 뜻으로 읽히거나 … 원어로 쓴다"로 바꿨다. "의미를 떠안다"는 rule이 피하라고 하는 꾸민 표현이다.
- 원칙 4 제목의 "연결 산문"을 "용어를 잇는 산문"으로 바꿨다.
- 문장 연결 절의 "기호로 쓰인 파일"을 "기호로 절을 이은 파일"로 바꿨다. 이 절이 다루는 것은 절을 잇는 기호다.

## Consequences

- rule과 skill의 복사본은 따로 바뀐다. rule을 고치면 복사본도 손으로 고치고 skill을 다시 올려야 한다. 이 절차는 `claude-ai/README.md`와 `CLAUDE.md`에 적었다. 둘이 어긋나도 잡는 검사는 없다. `bin/check-machine`은 claude.ai의 사본과 repo의 SKILL.md만 비교한다.
- repo의 SKILL.md가 동기화된 사본과 같으므로 지금 다시 올릴 필요는 없다. claude.ai에는 SKILL.md가 더는 가리키지 않는 `references/korean-writing.md`가 남아 있다. repo로 만드는 zip에는 이 파일이 없다.
- frontmatter 값에 따옴표가 붙고 파일 끝에 줄바꿈이 없는 것은 claude.ai가 저장한 형태다. 바이트 단위 비교를 통과하도록 그대로 두었다.
- `evals/board-titles/case.yaml`의 열 이름을 "원문"으로 고쳤다. AI slop 항목과 보고 템플릿을 검사하는 eval case는 아직 없다. 고친 skill을 이 repo의 eval로 다시 돌려 보지는 않았다.
