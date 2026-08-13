# 0019 — 정적 정합성 검사기 `bin/check-integrity` 도입

adopt한 항목이 의존 대상 없이 남는 결함을 잡기 위해 `bin/check-integrity`를 추가했다. `bin/check-updates`가 최신성만 검증하고 작동 여부는 검증하지 않는다는 공백을 메운다. 정적·오프라인·결정적이라 LLM도 네트워크도 쓰지 않는다.

## Context

하네스 평가 방법을 논의하다가, 가장 싼 검사 계층(참조 무결성)이 이미 실제 결함을 갖고 있음이 드러났다. `grill-with-docs`의 본문은 한 줄("Run a `/grilling` session, using the `/domain-modeling` skill.")인데 두 스킬 모두 설치돼 있지 않았다. 이 스킬은 2026-05-25부터 2026-08-05까지 네 번 재동기화되는 동안 계속 죽은 상태였다.

`check-updates`는 pin이 upstream HEAD보다 뒤처졌는지만 본다. 죽은 항목도 최신 상태로 유지할 수 있다.

평가 계층을 비용순으로 놓으면 정합성 → context 비용 → 발동 정확도 → 효과(ablation)가 된다. context 비용은 측정해 보니 문제가 아니었다(상시 로드되는 description 합계 약 2,052자, 700토큰 수준). 효과 측정은 `claude plugin eval --ablation with-without`이 정확히 겨냥하지만 현재 early access 게이트에 막혀 있다. 따라서 확실히 회수되는 첫 계층만 구현했다.

## Considered Options

**참조 탐지 규칙.** 백틱 `` `/token` `` 을 전부 스킬 참조로 보면 `/tmp`, `/goal`, `/plan` 같은 경로·내장 커맨드가 섞여 오탐이 쏟아진다. CI 게이트에서 오탐은 채택을 죽인다.

명사 "skill(s)"이 뒤따르는 경우만 오류로 보는 규칙을 택했다. 실측 결과 오탐 0건, 실제 결함 3종(`grilling`, `domain-modeling`, `codebase-design`)을 정확히 잡았다. 다르게 표현된 참조를 놓치는 재현율 손실은 경고 계층으로 보완한다 — 알려진 스킬도 내장 커맨드도 경로도 아닌 `` `/token` `` 은 경고로 보고한다.

## Consequences

- 검사 항목: 스킬 상호참조, `SKILL.md` frontmatter(`name`이 폴더명과 일치, `description` 존재), 마크다운 상대링크, provenance 사이드카 유효성.
- 스킬 참조는 이 저장소의 `user/shared/skills/`뿐 아니라 설치된 플러그인이 vendoring한 스킬(`~/.claude/plugins/cache`)로도 해석된다. 머신 상태를 읽지만 없으면 그냥 건너뛰므로 CI에서도 돈다.
- **부수 발견:** `user/shared/CLAUDE.md.provenance.json`의 `"source": "self"` 항목이 필수 필드 검사에 걸렸다. `bin/adopt`가 만들지 않는 손으로 넣은 항목이고 PROVENANCE.md에도 없었다. upstream에서 의도적으로 갈라졌음을 기록하는 유효한 관행으로 판단해, 검사기가 `commit`/`path`/`license`를 면제하도록 하고 `docs/PROVENANCE.md` § "Edge cases"에 정식화했다.
- 도입 시점 기준 오류 0건, 경고 0건.

## References

- [[0020-adopt-missing-skill-dependencies]] — 이 검사기가 찾은 결함의 해소
- [[0003-adr-for-every-change]]
