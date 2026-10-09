# 0072 — `resolving-merge-conflicts` skill을 제거한다

upstream mattpocock/skills가 `daa01d8`에서 이 skill을 대체 없이 삭제했다. CHANGELOG는 "It's no longer needed, and nothing replaces it"라고 적는다. ADR 0071에서 올린 새 `ask-matt`도 더는 이 skill을 안내하지 않고, 이 repo의 다른 파일도 참조하지 않는다. upstream이 없는 사본을 남겨 두면 `check-updates`가 mattpocock/skills를 계속 outdated로 보고하므로 `user/shared/skills/resolving-merge-conflicts`를 sidecar와 함께 지웠다.

## Consequences

- merge나 rebase conflict는 전용 skill 없이 agent가 직접 처리한다.
- 다시 필요해지면 `959a8e9f`의 `skills/engineering/resolving-merge-conflicts`에서 가져올 수 있다. 그 경우 upstream이 없으므로 `check-updates`가 다시 outdated로 보고한다.
