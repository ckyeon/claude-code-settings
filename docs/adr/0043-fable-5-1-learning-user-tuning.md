# 0043 — Fable 5.1 행동 편향을 학습자 관점으로 CLAUDE.md·rule에 반영

Anthropic의 "Prompting Claude Fable 5.1" 문서(platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1, 2026-09-02 열람)를 이 repo에 대조했다. progress update, tool-call batching, 자율 실행 블록, append-only 이력, compaction, 백그라운드 subagent는 Claude Code 하네스가 이미 구현하므로 여기서 할 일이 없다. 남는 모델 행동 편향(범위 확장·테스트 과잉, 파일 전체 재작성, 밀도 높은 산문, low effort에서 검색 생략, 인용 미표시)을 **학습 중인 사용자** 기준으로 걸러 `user/shared/CLAUDE.md`와 `korean-technical-writing.md`에 넣었다. settings.json의 effort(fable-5-1: high)는 문서 권고와 일치해 그대로 둔다.

## Considered Options

- **자율 실행 블록에 맞춰 CLAUDE.md § 1(Clarify first)을 완화** — throughput은 오르지만 학습자가 대안과 근거를 보지 못한다. 기각.
- **현행 유지 + 의도 명시 (채택)** — CLAUDE.md는 하네스 기본값에 대한 의도적 카운터웨이트다. 미래 세션이 이를 "충돌"로 보고 지우지 않도록 상단에 한 문장으로 적었다.

## Consequences

- CLAUDE.md § 3 추가: 요청 범위만 변경(인접 버그는 follow-up 보고), 테스트는 요청했거나 repo 관행이 있을 때만, 통째 재작성 대신 surgical edit, 라이브러리·API 사실은 문서로 검증하고 출처·인용 표시, 새 개념은 이름과 한 줄 정의, 막히면 `/ask-matt`. 학습자에겐 작은 diff와 follow-up 보고가 곧 읽을거리·연습거리가 된다는 판단이다.
- rule 파일에 "꾸민 산문(mannered prose)" 절을 언어 무관으로 추가하고 적용 범위 문장을 그에 맞게 고쳤다. 기존 "은유 압축" 항목의 일반형이다.
- effort를 medium으로 내리는 실험은 하지 않는다. 낮은 effort는 검색 대신 기억으로 답하는 경향이 있어, 오래된 답을 걸러내지 못하는 학습자에게 해롭다.
- `CLAUDE.md.provenance.json`에 self 항목을 추가했다(2026-05-24 재작성에 이은 두 번째 self 항목).
