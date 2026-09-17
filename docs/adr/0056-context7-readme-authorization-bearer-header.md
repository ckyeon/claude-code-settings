# 0056 — context7 README의 등록 예제를 upstream이 안내하는 Authorization: Bearer header로 맞춤

ADR 0055의 check-updates에서 드러난 문서 표류를 고쳤다. 로컬 README는 legacy 이름인 `CONTEXT7_API_KEY` header를 예제로 쓰고 `X-Context7-API-Key`를 canonical이라 설명했지만, upstream README는 `Authorization: Bearer <key>`만 안내한다. 서버 코드(`packages/mcp/src/index.ts`, pin `4416fb85`)를 확인하니 여섯 가지 이름을 모두 받으므로 동작 문제는 없었고, 예제와 설명만 upstream 안내에 맞췄다. 이미 `CONTEXT7_API_KEY`로 등록된 machine은 재등록하지 않는다.
