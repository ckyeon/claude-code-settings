# 0041 — check-integrity의 링크 검사가 템플릿 자리표시자를 건너뜀

`wayfinder` 스킬의 `[<closed ticket title>](link)`처럼 사용자에게 줄 모양을 보여주는 템플릿 자리표시자를 링크 검사가 깨진 링크로 오판했다. `copied` 스킬 파일을 고치면 재동기화 때 되돌아가므로 checker 쪽을 고쳤다: 링크 텍스트나 대상이 `<...>`이거나 대상이 `link`/`url`인 경우는 건너뛴다. 스킬 참조 검사에 이미 있던 `name`/`skill-name` 자리표시자 예외와 같은 원리다.
