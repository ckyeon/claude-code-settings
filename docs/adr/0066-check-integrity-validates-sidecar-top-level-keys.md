# 0066 — check-integrity가 sidecar의 최상위 key와 `track` 값을 검증한다

ADR 0065의 `track`은 key 이름이 틀리면(`"trak"`) 어떤 도구도 읽지 않으므로, 아무 경고 없이 HEAD 기준 비교로 돌아간다. 그래서 `bin/check-integrity`가 `provenance`와 `track` 외의 최상위 key를 error로 보고하고, `track` 값이 `release`나 `marketplace`가 아니면 역시 error로 보고하도록 했다. 두 경우 모두 설정이 틀린 것이 확실하므로 error의 높은 정밀도 원칙에 맞는다. 추가 당시 sidecar 88개 중 위반은 없었다. 허용 값 목록은 `bin/check-updates`와 같아야 하며, 코드 주석에 이를 적어 두었다.
