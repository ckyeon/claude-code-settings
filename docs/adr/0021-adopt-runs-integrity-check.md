# 0021 — `bin/adopt`가 정합성 검사를 스스로 실행

의존 스킬 누락(ADR 0020)의 재발 방지를 문서에서 도구로 옮겼다. `bin/adopt`가 adopt 직후 `bin/check-integrity`를 실행하고, 실패하면 커밋 제안을 출력하기 전에 경고한다. `--no-check`로 끌 수 있다.

## Context

ADR 0019에서 검사기를 만들고 CLAUDE.md에 "adopt 후 실행하라"고 적었다. 그런데 이건 ADR 0020을 만든 것과 같은 종류의 방어다 — 실행하는 쪽이 기억해야 작동한다. 원래 adopt도 위임 대상을 확인해야 했지만 그럴 절차가 없었고, 그래서 `grill-with-docs`가 네 번의 재동기화를 죽은 채로 통과했다.

`bin/adopt`는 이미 `bin/sources-index`를 자동 실행한다. 같은 자리에 검사를 붙이는 것이 구조적으로 일관된다.

## Considered Options

**실패로 처리(exit 1)하는 안**은 버렸다. 의존 사슬을 adopt할 때 중간 상태는 정당하게 빨갛다 — 3개 중 첫 번째를 가져온 시점에 나머지 2개는 아직 없다. 여기서 실패하면 도구가 정상 작업을 막는다. adopt 자체는 성공했으므로 exit는 0으로 두고, 경고만 크게 낸다.

**pre-commit hook**은 이 저장소 가드레일(`git config` 변경 금지)에 걸린다. 커밋된 hooks 디렉터리를 쓰려면 `core.hooksPath` 설정이 필요하다.

경고 위치는 커밋 제안 **앞**으로 잡았다. 뒤에 두면 사용자가 커밋 명령부터 복사해 실행한다.

## Consequences

- 로컬 픽스처 저장소로 end-to-end 검증했다. 위임 대상이 없는 스킬을 adopt하면 커밋 제안 전에 경고가 뜨고, `--no-check`는 검사 출력을 완전히 억제한다.
- 경고문은 두 가지를 명시한다 — 죽은 항목은 `check-updates`가 영원히 "up to date"로 보고한다는 점, 그리고 위임 대상이 upstream의 다른 카테고리에 있을 수 있으니 저장소 전체를 찾으라는 점(ADR 0020의 실제 원인).
- **남는 공백:** adopt를 거치지 않는 변경은 여전히 잡히지 않는다. 직접 작성한 스킬, 손으로 고친 `SKILL.md`, 참조 대상을 지우는 변경 등이다. 이를 덮으려면 CI에서 `bin/check-integrity`를 돌려야 하는데, 이 저장소엔 아직 `.github/workflows/`가 없어 별도 결정으로 남긴다.

## References

- [[0019-static-integrity-checker]]
- [[0020-adopt-missing-skill-dependencies]] — 이 변경이 막으려는 결함
- [[0003-adr-for-every-change]]
