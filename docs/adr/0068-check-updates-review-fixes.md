# 0068 — ADR 0064~0067 리뷰에서 나온 check-updates 수정

002049e 이후 변경을 Standards와 Spec 두 축으로 리뷰한 결과 중 세 가지를 고쳤다.

- **marketplace 조회 timeout:** marketplace clone과 `git show`가 timeout되면 예외가 잡히지 않아 fast check 전체가 traceback과 함께 exit 1로 끝났다. check-updates skill은 exit 1을 "outdated 있음"으로 읽는다. 이제 timeout도 조회 실패로 처리해 해당 항목을 `?`로 보고한다. `list_tracked_plugins` 호출에도 timeout과 return code 확인을 넣었고, 실패하면 stderr에 WARN을 출력한다.
- **stable tag 형식:** ADR 0065의 계획은 `vX.Y.Z` 형식이었는데, 정규식은 `v` 없는 `X.Y.Z`도 받았다. 계획에 맞춰 `v` 접두사를 필수로 했다. `track: "release"`를 쓰는 herdr와 agent-browser는 둘 다 `v` 접두사 태그를 쓴다.
- **낡은 설명:** script 헤더와 SKILL.md의 "no clone" 설명은 marketplace 기준 항목이 있으면 틀린다. 이 설명과 SKILL.md 첫 문단의 "behind HEAD"를 고쳤다. 새로 추가한 주석의 슬래시, 세미콜론, 괄호 안 완결 절도 말로 풀었다.

ADR 0063과 0065의 한국어 문장 교정, "재pin"과 "re-pin" 표기 통일은 이번에 하지 않았다.
