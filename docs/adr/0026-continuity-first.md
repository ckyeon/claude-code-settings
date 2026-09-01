# 0026 — 백업의 목적을 "작업 연속성"으로 좁히고 재개 지점을 문서화

/grilling 인터뷰로 백업의 진짜 목적이 확인됐다: 진행 중인 개인 프로젝트 4개(llm-wiki·toego·agent·claude-code-settings)의 미완 작업을 초기화 후 이어가는 것. 이에 따라 [runbook](../migration-2026-08-31.md)을 개정한다.

## 결정

- **연속성의 주 수단은 각 repo의 문서, 세션 아카이브는 보조.** 세션 resume은 경로·도구 버전에 묶이고 오래된 컨텍스트는 요약으로 열화된다. 조사 결과 llm-wiki(`humanities-index.md` 백로그)·toego(`PROJECT.md` 5.5 심사 대기)·claude-code-settings(ADR 로그)는 이미 repo 문서가 재개 지점을 담고 있었고, 유일한 구멍으로 보였던 agent의 `docs/curriculum-review-2` 머지 판단도 **이미 PR #6(2026-08-18)으로 머지되어 있었다** — 낡은 로컬 refs가 만든 착시였다(llm-wiki PR #49와 같은 패턴). handoff 문서는 결국 하나도 새로 쓸 필요가 없었고, runbook §5에 재개 지점만 모아 둔다.
- **목적 밖 세션(cs231n·hackers·toy-project 등)과 자료 보관(비-git 디렉터리)은 유지** — 비용이 사실상 0이라 좁힌 목적이 버릴 이유가 되지 않는다.
- **새 맥은 개인 계정 + username `ckyeon`.** 회사 계정의 claude.ai 대화·커넥터·구독은 반출 불가로 간주. llm-wiki의 매일 09:00 자동 유지보수 routine은 개인 계정 소유로 확인되어 퇴사와 무관하게 생존한다 (이 세션 계정의 routine 목록은 0개 — 교차 확인).
- **아카이브 저장은 개인 클라우드 + 암호화**, 외장 사본은 선택.

## References

- [[0025-offboarding-revision]]
