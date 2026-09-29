# 0064 — check-updates deep scan은 commit log 대신 내용으로 변경을 판정한다

`bin/check-updates --deep`은 `git log <pin>..<head> -- <path>`에 commit이 있으면 "changed"로 판정했다. 이 방식은 pin이 head의 조상이 아닐 때 틀린다. 2026-09-29 scan에서 herdr가 "changed"로 나왔지만 실제로는 내용이 같았다. pin인 v0.9.1이 side branch에서 만든 release commit이고, 같은 편집이 main에는 다른 commit으로 들어갔기 때문이다. 반대로 pin 쪽 branch에만 있는 변경은 `pin..head`에 잡히지 않으므로 내용이 달라도 "pin-only"로 판정될 수 있다. 그래서 pin과 head에서 tracked path의 tree 또는 blob SHA를 비교해 판정하도록 바꿨다. SHA가 같으면 pin-only, 다르면 changed다.

## Consequences

- tree 객체는 blobless clone에도 있으므로 파일 내용을 추가로 내려받지 않는다.
- 두 SHA 중 하나라도 구할 수 없으면(path가 한쪽에 없음) 예전처럼 log로 판정한다.
- 내용은 다른데 `pin..head` log가 비어 있으면 `log.txt`에 `--left-right <pin>...<head>` log를 쓴다. `<`가 pin 쪽 commit이다.
- 가짜 upstream repo로 확인했다. side branch pin에 같은 편집이 main에 들어간 경우와 pin 쪽에만 변경이 있는 경우에서 예전 판정은 각각 오탐과 미탐이었고, 새 판정은 둘 다 맞았다. 실제 repo에서는 herdr가 pin-only로 바뀌었고 나머지 판정은 그대로였다.
- herdr는 여전히 fast check에서 outdated로 나온다. 비교 기준이 upstream HEAD이기 때문이며, ADR 0065에서 다룬다.
