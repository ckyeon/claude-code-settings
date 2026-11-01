# 0114 — adopt trailer는 adopt만 하는 commit에 붙인다

CLAUDE.md "Adopt an external item" 3단계의 문구를 관행에 맞췄다. trailer는 항목 하나를 adopt하기만 하는 commit에 붙인다. `--commit-now`가 만드는 commit이 여기에 해당한다. 여러 항목을 adopt하는 commit과, project template 추가처럼 더 큰 변경의 일부로 adopt하는 commit은 항목 이름을 메시지에 적는다.

## 경위

- 이전 문구는 "a commit that adopts one item"이었다. template과 함께 plugin 하나를 adopt한 commit 넷(2873e87, 4647f3a, 002049e, f2394c7)은 모두 trailer를 붙이지 않았고, adopt만 한 65b3fd0은 붙였다.
- ADR 0113의 리뷰는 f2394c7을 이 문구의 위반으로 보고했다. 관행은 일관되었고 문구가 그것과 달랐다.
- 출처는 sidecar에 기록되므로, trailer가 없어도 잃는 정보는 없다.
