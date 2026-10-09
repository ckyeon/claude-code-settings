# 0086 — `check-updates`의 판정을 `lib/updates.py`로 옮기고, 보고는 그 결과의 표현으로 둔다

architecture 리뷰의 네 번째 후보다. `bin/check-updates`는 heredoc 하나 안에서 판정과 출력을 함께 했다. 판정 결과는 열을 맞춘 text로만 나왔고, `check-updates` skill이 읽는 `deep.json`은 내부 dict를 그대로 내보낸 것이었다. 그래서 같은 값이 `target`과 `head` 두 이름으로 들어 있었고, 여러 pin에서 본 같은 구조 변화는 화면에 찍을 때만 중복을 걸러 JSON에는 중복이 남았다.

## 결정

- **판정은 `lib/updates.py`가 한다.** `check()`는 현재 pin마다 비교 대상과 상태를 담은 record를 낸다. `investigate()`는 뒤처진 pin을 들여다보고, 추적 path의 내용이 바뀌었는지와 upstream 구조가 어떻게 바뀌었는지를 record로 낸다.
- **화면 보고와 `deep.json`은 같은 record의 두 표현이다.** `bin/check-updates`는 record를 text로 찍고 `deep.json`으로 쓴다. 중복 제거는 record를 만들 때 한다.
- **비교 대상의 이름은 `target` 하나다.** HEAD가 아닌 대상도 있으므로 `head`를 없앴다. item record와 structure record 모두 해당한다.
- **record의 필드가 skill과의 interface다.** `check-updates` skill 문서의 2단계가 필드를 나열한다. 필드를 바꿀 때는 module과 그 문서를 함께 고친다.

## Consequences

- `bin/check-updates`는 516줄에서 150줄이 됐다. ADR 0082부터 이 ADR까지 sidecar 읽기, 구조 scan, 비교 대상, 판정이 차례로 `lib/`으로 나갔다.
- 실제 repo에서 fast와 deep의 화면 출력은 고치기 전과 같다. `deep.json`은 item record에서 `head`가 빠진 것만 다르다.
- `tests/test_updates.py` 12개가 판정을 직접 확인한다. pin이 side branch에 있는 두 경우, 곧 내용이 다르면 changed이고 다른 commit으로 같은 내용에 닿았으면 pin-only인 것에 처음으로 test가 붙었다. upstream에 없는 pin이 error가 되는 것도 그렇다. module을 세 군데 고쳐서 해당 test가 실패하는 것을 확인했다.
- 명령줄 test에는 source에 닿지 못할 때 종료 code가 2인 것을 추가했다.
- fast만 돌릴 때는 지금도 `deep.json`이 없다. fast의 record를 파일로 내는 옵션은 쓸 곳이 없어 만들지 않았다.
