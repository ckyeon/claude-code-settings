# 0059 — remotion plugin README에 설치 함정 두 가지 기록

`video-edit-test` 프로젝트에 remotion plugin을 설치하다가 나온 두 가지를 `user/shared/plugins/remotion/README.md`에 적었다. 첫째, plugin 출처가 `github` 형식이라 SSH clone이 `~/.ssh/known_hosts`에 github.com key가 없으면 실패하고, `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`로 HTTPS clone을 강제하면 설치된다. 둘째, `claude plugin marketplace add`가 user settings의 `extraKnownMarketplaces`에 marketplace를 기록하는데, user settings가 이 repo의 `user/shared/settings.json`이므로 그 변경은 commit해서 남긴다. 기존 third-party marketplace(`openai-codex`, `understand-anything`)와 같은 방식이다.
