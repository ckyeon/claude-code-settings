# 0142 — 산문 기호 hook의 PostToolUse 알림은 사용자 화면에 나오지 않는다

ADR 0138이 모른다고 남긴 점을 확인했다. 2026-11-25에 `"verbose": false`인 화면에서 사용자가 보니, Write와 Edit 뒤의 `additionalContext` 알림은 나오지 않았고 Bash를 막은 deny의 이유는 "Not run · permission denied" 아래에 첫 줄이 나왔다. 앞의 알림은 Claude가 고치게 하려는 것이라 바꿀 것이 없으므로, hook 설명에 이 사실만 적었다.
