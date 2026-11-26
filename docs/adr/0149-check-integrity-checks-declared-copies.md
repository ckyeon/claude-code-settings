# 0149 — 2026-11-26 check-integrity가 skill 안의 rule 복사본이 rule과 같은지 검사

[[0148-korean-review-copies-rule-into-skill]]로 `korean-review`의 SKILL.md에 rule 복사본이 생겼다. 그런데 rule만 고쳐서 복사본이 어긋나도 잡는 검사가 없었다. 이제 `claude-ai/copies.json`에 복사본이 있는 절과 일부러 뺀 부분을 적는다. `bin/check-integrity`는 rule에서 그 부분을 뺀 결과를 복사본과 비교하고, 다르면 error를 낸다.

## 비교 방법

- rule의 제목(level 1 heading)은 복사본의 절 제목에 해당하므로 비교에서 뺀다. rule의 나머지 heading은 복사본의 절 제목보다 한 단계 아래로 내려 비교한다.
- `drop_sections`에 적은 절은 rule에서 통째로 뺀다. `replace`의 각 쌍은 rule의 문구를 복사본의 문구로 바꾼다. 빈 문자열로 바꾸면 그 문구를 뺀 것이다.
- `replace`의 문구가 rule에 정확히 한 번 나오지 않으면 error다. rule의 그 부분이 바뀐 것이므로, 복사본에 무엇을 옮길지 사람이 정해야 한다.
- 줄 끝 공백과 연속된 빈 줄은 비교하지 않는다.
- error 메시지에는 두 쪽이 처음 갈라지는 곳의 앞뒤 문구를 보인다.

## Considered Options

- **뺀 부분을 `bin/check-integrity`에 적는다**: 기각. 복사본에서 더 뺄 때마다 `bin/`을 고치고 `tests/run.sh`를 돌려야 한다.
- **뺀 부분을 SKILL.md 안의 주석으로 적는다**: 기각. SKILL.md는 claude.ai에 올라가고, skill을 쓸 때 context에 들어간다. provenance를 sidecar에만 두는 것과 같은 이유다.
- **`claude-ai/copies.json`에 적는다**: 채택. upload zip과 `bin/check-machine`이 보는 `claude-ai/skills/<name>/` 밖에 있으므로 claude.ai에 올라가지 않는다.
- **복사본의 줄이 모두 rule에 있는지만 본다**: 기각. 뺀 부분이 한 줄의 일부라서 줄이 그대로 맞지 않는다. 게다가 rule에 새로 생긴 줄을 복사본에 옮기지 않은 경우를 잡지 못하는데, 이 검사가 잡으려는 것이 바로 그 경우다.

## 검증

- 지금 repo는 검사를 통과한다.
- repo 사본에서 rule의 괄호 항목에 문장을 더했더니, error가 복사본의 절 위치와 더한 문장을 보였다. 과압축 절의 전례 날짜를 바꿨더니, 뺀 문구가 rule에 없다는 error와 비교 error가 함께 났다.
- `tests/run.sh`에 시험 5개를 더했다. 전체 184개가 통과한다.

## Consequences

- Stop hook이 `bin/check-integrity`를 돌리므로, rule만 고치고 끝내려는 세션은 끝나기 전에 복사본을 맞추게 된다.
- 복사본에서 더 빼려면 `claude-ai/copies.json`에도 적어야 한다. 적지 않으면 error가 난다.
- 복사본까지 맞춰도 claude.ai에 다시 올리는 일은 남는다. 올리지 않은 차이는 `bin/check-machine`이 warning으로 알린다.
