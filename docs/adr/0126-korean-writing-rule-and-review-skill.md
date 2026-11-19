# 0126 — 한국어 rule을 일반 글쓰기 rule로 넓히고, 그 rule로 리뷰하는 claude.ai skill을 이 repo에서 관리한다

`korean-technical-writing.md`의 이름을 `korean-writing.md`로, 제목을 "한국어 글쓰기"로 바꿨다. 같은 rule을 검사 기준으로 쓰는 리뷰 skill `korean-review`를 `claude-ai/skills/`에 두고 claude.ai에 올려 쓴다. 이 repo의 범위를 claude.ai skill 가운데 원본이 여기 있는 것까지 넓히고, 그런 skill은 선언(declared) 항목으로 분류한다.

## Context

- 사용자가 claude.ai 채팅에 rule 파일을 붙여 넣고 기술 글이 아닌 한국어 문서를 리뷰하게 했더니 효과가 컸다. 그 리뷰가 쓴 기준은 원칙 2, 원칙 3, 과압축, 번역투, 꾸민 산문이었다. 기술 글에만 맞는 원칙 1은 쓰이지 않았다. rule의 적용 문장은 이미 모든 한국어 산문을 가리켰으므로 "기술 문서"라는 이름이 실제 범위보다 좁았다.
- 그 리뷰는 rule에 없는 문제도 잡았다. 빠진 성분, 가리키는 말이 없는 지시어, 서술어와 맞지 않는 주어나 목적어, 뜻이 너무 넓은 말이다. 지시어 항목은 [[0102-unpack-korean-rule-sentences]]가 관측 사례가 없다는 이유로 미룬 후보다.
- claude.ai에는 `~/.claude/rules`가 로드되지 않는다. claude.ai에서 rule을 쓰려면 skill로 올려야 한다.

## Considered Options

- **rule을 skill로 옮긴다** — 기각. skill 본문은 쓸 때만 로드된다(code.claude.com/docs/en/skills). 이 rule은 거의 모든 응답에 적용되는데, Claude가 매 응답마다 skill을 부른다는 보장이 없다. 2026-10-15 eval의 `korean-prose` case에서 rule을 끈 arm은 화살표가 없는 응답이 5회 중 1회였고, 켠 arm은 5회 중 5회였다.
- **claude.ai에서만 skill을 만들고 repo 밖에 둔다** — 기각. rule 본문이 두 벌이 된다. rule은 지금까지 13번 바뀌었으므로 두 벌을 손으로 맞추는 부담이 크다.
- **repo가 원본을 관리하고 claude.ai에 올린다** — 채택. claude.ai skill은 같은 계정의 Claude Code로 동기화된다. `user/shared/skills/`에 두면 Claude Code에 같은 skill이 두 번 보이므로 `claude-ai/skills/`에 두고 링크하지 않는다.
- **repo 이름을 바꾼다** — 하지 않았다. skill 하나 때문에 `~/.claude`의 symlink 9개, auto memory 경로, auto mode 문구까지 바꿀 이유가 약하다. claude.ai 쪽 항목이 여럿으로 늘면 다시 본다.

## 결정 내용

- rule은 Claude Code에서 계속 상시 로드한다. 글을 쓸 때 문제를 막는 일은 rule이 맡고, 이미 쓴 글을 검사하는 일은 skill이 맡는다. [[0012-korean-technical-writing-rule]]이 미뤄 둔 탐지 단계에 해당한다.
- skill의 `references/korean-writing.md`는 rule 파일을 가리키는 symlink다. `zip`은 symlink를 따라가므로 올리는 zip에는 rule 원문이 들어간다.
- 새 검사 항목 넷은 skill에만 넣었다. 남이 쓴 글에서 나온 사례이기 때문이다. 상시 rule은 Claude가 직접 쓴 글에서 나온 사례가 있을 때만 넓힌다.
- 남이 쓴 글에 rule을 댈 때 원칙 1은 기술 글에만, 기호 규칙은 산문 문단에만 적용한다. 맞춤법과 띄어쓰기는 보지 않는다.
- claude.ai skill은 선언 항목이다. repo를 고쳐도 사람이 다시 올리기 전에는 claude.ai의 skill이 바뀌지 않는다. 올리는 방법은 `claude-ai/README.md`에 적었다.

## 검증

- skill-creator 절차로 과제 3개를 skill이 있을 때와 없을 때 한 번씩 돌렸다. 검사 28개 가운데 skill이 있을 때 28개, 없을 때 23개를 통과했다.
- 심어 둔 문제를 찾는지 묻는 검사 20개는 양쪽 모두 통과했다. subagent에도 상시 rule이 로드되어, skill이 없는 쪽도 rule은 있는 상태였기 때문으로 보인다. 차이는 표 형식, 반영 전 확인, 문제가 적은 글에서 고칠 곳을 늘리지 않는 태도에서 났다.
- skill이 없는 쪽은 문장 밖의 내용 문제를 더 깊이 짚었다. 이를 받아 SKILL.md에 내용 문제를 찾아 질문으로 따로 적는 줄을 더했다. 이 변경 뒤에는 다시 돌려 보지 않았다.
- 과제 입력 두 개의 요일이 달력과 맞지 않았다. 양쪽 모두 이 실수를 잡았고, 입력을 고쳤다.

## Consequences

- rule을 고치면 `korean-review`를 claude.ai에 다시 올려야 한다. 잊으면 claude.ai와, 거기서 동기화된 Claude Code의 skill이 옛 rule로 리뷰한다. 이 차이를 잡는 검사는 아직 없다. `bin/check-machine`이 동기화된 사본과 repo의 원본을 비교하는 방법이 후보다.
- `bin/check-integrity`는 `claude-ai/skills/`를 보지 않으므로 symlink가 끊겨도 잡지 못한다.
- README의 범위 문장, Scope 표, tree와 CLAUDE.md의 범위 문장을 고쳤다.
- 과거 ADR에 남은 `korean-technical-writing`이라는 이름은 기록이므로 두었다.
