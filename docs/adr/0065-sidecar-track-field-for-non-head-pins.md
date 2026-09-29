# 0065 — sidecar의 `track` 필드로 HEAD가 아닌 비교 기준을 지정한다

`bin/check-updates`는 모든 pin을 upstream HEAD와 비교했다. 그래서 일부러 HEAD가 아닌 곳에 pin한 항목은 영원히 outdated로 나왔다. herdr는 stable release에만 pin하고(ADR 0051), hyperframes는 `claude-plugins-official` marketplace가 가리키는 sha를 따른다. 2026-09-29 scan에서 이 둘이 outdated로 나와 fast check의 개수를 믿을 수 없었다. sidecar 최상위에 선택 필드 `track`을 두고, check-updates가 그 값에 따라 비교 기준을 구하도록 했다. `"release"`는 source의 최신 stable `vX.Y.Z` tag를, `"marketplace"`는 plugin의 marketplace가 `marketplace.json`에 적은 `sha`를 기준으로 삼는다. 두 sidecar에 이 필드를 넣은 뒤 두 항목은 up to date로 나오고 outdated는 10개에서 7개로 줄었다.

## Considered Options

- **`hold` 필드로 비교에서 제외**: 코드는 짧지만 새 release가 나와도 알려 주지 않는다. ADR 0051의 "다음 stable release 때 재pin"을 사람이 기억해야 하므로 택하지 않았다.
- **도구는 두고 skill 단계에서 거르기**: 코드 변경은 없지만 fast check 숫자가 계속 틀리고, 매번 subagent가 README와 ADR을 다시 읽어야 한다.

## Consequences

- `track`은 `provenance[]` 항목이 아니라 최상위 key다. `append_provenance`가 다른 key를 보존하므로 `bin/adopt`로 재pin해도 남는다. `bin/adopt`는 이 필드를 읽지 않으므로 재pin할 때는 check-updates가 출력한 target을 `--commit`으로 넘겨야 한다.
- `docs/PROVENANCE.md`는 sidecar에 marketplace를 적지 않기로 했으므로 `track`에는 정책 이름만 둔다. marketplace는 `lib/common.sh`의 `list_tracked_plugins`로 찾는다. 이 함수는 install.sh와 같은 방식으로 `enabledPlugins`와 `extraKnownMarketplaces`를 읽는다. built-in marketplace는 settings에 repo가 없으므로 `claude-plugins-official`의 URL을 check-updates에 상수로 두었다.
- target을 구하지 못하면 이유와 함께 `?`로 보고한다. HEAD로 대체하지 않는다. `track` 값의 오타도 여기에 해당한다.
- marketplace 기준 항목이 있으면 fast check가 marketplace repo를 depth 1, blobless로 한 번 clone한다.
- deep scan도 HEAD 대신 target과 비교한다. `deep.json`의 `head` 필드는 이 target을 뜻한다.
- 가짜 repo로 확인한 사항은 다음과 같다. annotated tag는 commit SHA로 풀린다. rc, beta, preview tag는 제외된다. 옛 release에 pin된 항목은 outdated로 나온다. third-party marketplace의 sha를 읽는다. sha가 없는 marketplace 항목, 어느 settings에도 없는 plugin, 알 수 없는 `track` 값은 `?`로 나온다.
