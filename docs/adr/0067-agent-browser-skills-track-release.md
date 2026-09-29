# 0067 — agent-browser의 `core`와 `dogfood`를 release 기준으로 추적한다

agent-browser skill은 CLI 명령과 환경변수를 설명하므로, 아직 release되지 않은 main의 내용을 가져오면 설치된 CLI와 어긋난다. 2026-09-29에는 main에만 있는 Browser Use 환경변수 설명 때문에 `core` 업데이트를 보류했다(ADR 0063). 그래서 두 sidecar에 `"track": "release"`를 넣어, check-updates가 새 stable release가 나올 때만 outdated로 보고하게 했다. 현재 pin `aff6125c`는 v0.38.1 tag commit과 같으므로 re-pin이나 내용 변경은 없다.
