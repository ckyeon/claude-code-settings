# 0144 — understand-anything은 쓰는 프로젝트에 local scope로 설치한다

understand-anything plugin이 user scope에 켜져 있어서, 모든 세션에 skill 9개와 agent 10개의 설명이 들어왔다. 사용자는 이 plugin을 특정 프로젝트에서만 쓰려고 한다. 그래서 user scope에서 plugin과 marketplace 선언을 지우고, `user/shared/plugins/understand-anything/`의 선언도 지웠다. 앞으로는 ADR 0095의 `ait`처럼 그 plugin을 쓰는 프로젝트가 소유한다.

## 경위

- `/understand`의 출력인 `.ua/knowledge-graph.json`은 `~/workspace/newsletter`(2026-09-26)와 `~/workspace/gigr/playable-phaser-template`(2026-09-09)에만 있었다. 두 곳 모두 그 뒤로 graph가 갱신되지 않았다.
- 사용자는 지금 어느 프로젝트에도 설치하지 않기로 했다.

## 다시 쓸 때

그 프로젝트 디렉터리에서 아래 순서로 실행한다. local scope는 `.claude/settings.local.json`에 적히므로 그 repo의 협업자에게 퍼지지 않는다.

```
claude plugin marketplace add Lum1104/Understand-Anything --scope local
claude plugin install understand-anything@understand-anything --scope local
```

## Considered Options

- **template에 넣는다.** ADR 0062가 clangd-lsp에 쓴 방식이다. 이 plugin은 특정 프로젝트 종류에 묶이지 않아 맞는 template이 없다.
- **선언만 남긴다.** 어느 settings에서도 켜지지 않아 `bin/check-integrity`와 `install.sh`가 경고를 계속 낸다. ADR 0062가 같은 이유로 택하지 않았다.
- **project scope로 설치한다.** `.claude/settings.json`에 적혀 commit 대상이 된다. 혼자 쓰는 분석 도구를 그 repo의 협업자에게 안내할 이유가 없어서 local scope를 택했다.

## Consequences

- 새 기기를 이 repo로 재현해도 understand-anything은 설치되지 않는다.
- `user/shared/plugins/remotion/README.md`에서 understand-anything marketplace를 언급하던 부분을 고쳤다.
- 두 프로젝트의 `.ua/` 디렉터리는 gitignore되어 있고 그대로 두었다.
