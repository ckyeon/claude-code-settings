# 0024 — 노트북 초기화 runbook을 docs/에 기록

2026-08-31 노트북 초기화를 앞두고 마이그레이션 스냅샷과 새 맥 복원 절차를 [docs/migration-2026-08-31.md](../migration-2026-08-31.md)로 기록한다. 이 repo가 새 머신에서 가장 먼저 clone하는 부트스트랩 지점이므로 복원 문서도 여기에 둔다.

같은 세션의 부수 결정:

- `user/shared/settings.json`의 미커밋 수정분(model·language·effortLevel·voice 선호 + GiverGround 관련 autoMode 블록)은 커밋하지 않고 폐기한다 — 개인 repo에 회사 컨텍스트를 넣지 않기 위함. 폐기 목록은 runbook §5에 남겨 새 맥에서 재설정할 수 있게 한다.
- mattpocock-skills의 미추적 `.agents/`·`skills-lock.json`은 `setup-matt-pocock-skills` 설치기의 산출물(원본과 바이트 동일 확인)이라 커밋 대신 삭제한다.
