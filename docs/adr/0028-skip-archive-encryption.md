# 0028 — 백업 아카이브 암호화 생략

[runbook](../migration-2026-08-31.md) §2의 "클라우드 업로드 전 암호화" 권고를 사용자 결정으로 생략한다. 결정 전에 아카이브 내용물을 흔한 secret 형식(Anthropic·GitHub·AWS 키, private key 블록, Slack 토큰)으로 스캔했다: `history.jsonl` 0건, 세션·subagent transcript에서 매치 1개 파일 — 내용은 subagent가 읽어온 외부 프로젝트 README에 제3자가 노출한 GitHub PAT로, 본인 자격증명이 아니다. 패턴 스캔은 산문에 적힌 비밀번호까지 잡지는 못한다는 한계는 인지한 채의 결정이다.

## References

- [[0026-continuity-first]]
