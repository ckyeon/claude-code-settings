# 0095 — repo 밖 프로젝트만 쓰는 marketplace는 그 프로젝트에 선언한다

`claude plugin marketplace add`는 `--scope`를 주지 않으면 user settings에 marketplace를 선언하고, user settings는 이 repo의 `user/shared/settings.json`이다. 그래서 repo 밖 사이드 프로젝트 `~/workspace/app-in-toss`만 쓰는 `apps-in-toss` marketplace가 이 repo에 commit하지 않은 변경으로 남았다. 이런 marketplace는 그 프로젝트에서 `--scope project`로 선언하기로 하고, CLAUDE.md의 "Declare a plugin" 절에 적었다.

## 경위

- plugin `ait@apps-in-toss`는 2026-10-11에 project scope로 설치했다. marketplace는 `--scope` 없이 추가해서 user scope에 선언되었다.
- CLI 2.1.296의 `claude plugin marketplace add --help`는 "`--scope <scope>      Where to declare the marketplace: user (default), project, or local`"이라고 적는다. ADR 0059는 이 option을 다루지 않았다.
- 2026-10-20에 사용자가 app-in-toss 디렉터리에서 `--scope project`로 선언을 더한 다음, `marketplace remove apps-in-toss --scope user`로 user scope 선언을 뺐다. 그 뒤 app-in-toss의 `.claude/settings.json`에는 `enabledPlugins`와 `extraKnownMarketplaces`가 함께 있고, `claude plugin list`는 `ait@apps-in-toss`를 project scope와 enabled로 보여 준다.

## 순서

공식 문서(code.claude.com/docs/en/plugins/cli-reference)는 이렇게 적는다. "When you remove a marketplace from the last scope that declares it, Claude Code also deletes its cache and uninstalls every plugin you installed from it." 그래서 새 scope에 먼저 선언한 다음에 옛 scope에서 뺀다. `--scope` 없는 `remove`는 모든 scope에서 지우므로 plugin도 지워진다. `--help`는 plugin이 지워진다는 점을 적지 않으므로 CLAUDE.md에 남겼다.

## Considered Options

- **user scope 항목을 commit한다.** ADR 0059가 remotion에 쓴 방식이다. 이 repo가 선언하지 않은 plugin의 marketplace가 사이드 프로젝트마다 user scope에 쌓인다. `install.sh`는 선언된 plugin의 marketplace만 안내하므로 이 항목은 재현에 쓰이지 않는다.

## Consequences

- 이 repo가 선언하는 plugin의 marketplace는 지금처럼 user scope에 둔다. `openai-codex`, `understand-anything`, 그리고 template에서 쓰는 `remotion`이다. remotion을 template의 project scope에만 둘 수 있는지는 따로 정한다.
- app-in-toss는 git repo가 아니라서 그 settings는 어디에도 백업되지 않는다. 그 프로젝트가 따로 챙길 일이다.
