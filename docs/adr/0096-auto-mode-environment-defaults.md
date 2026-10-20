# 0096 — auto mode environment는 기본값에 이 repo의 공개 여부만 더한다

`/auto-mode-setup`이 만든 `autoMode.environment` 25개 항목을 `"$defaults"`와 항목 하나로 바꿨다. 더한 항목은 이 repo가 public이라는 사실이다. auto mode는 `autoMode`를 user settings에서만 읽으므로 이 블록은 모든 프로젝트의 세션에 적용되는데, 초안은 이 repo를 재료로 만들어져서 Trusted repo와 Source control을 이 repo로 고정했다.

## 경위

- 공식 문서(code.claude.com/docs/en/auto-mode-config)는 "The classifier doesn't read `autoMode` from project settings in `.claude/settings.json` or `.claude/settings.local.json`."라고 적는다. `/auto-mode-setup`은 지금 프로젝트의 CLAUDE.md, README, remote, 최근 세션을 읽어 초안을 만들고, 받아들이면 `~/.claude/settings.json`에 쓴다. 이 기계에서 그 파일은 `user/shared/settings.json`을 가리키는 symlink다.
- 고치기 전에 `~/workspace/app-in-toss`와 `/tmp`에서 `claude auto-mode config`를 실행했더니 Trusted repo가 `ckyeon/claude-code-settings`로 나왔다.
- 초안은 `"$defaults"` 없이 저장되었다. 기본 항목 21개 중 9개를 줄여 쓰면서 기본 문구의 단서가 빠졌다. visibility가 secret과 민감 데이터를 어느 repo에도 허용하지 않는다는 문장, 다른 repo는 private으로 간주한다는 규칙, instance-metadata credential은 task credential이 아니라는 단서가 그 예다.

## 결정

- `"$defaults"`를 넣어 기본 문구를 쓰고, 이후 Claude Code가 기본 목록을 고치면 그것을 따른다. 신뢰 범위는 세션마다 그 세션의 repo가 된다.
- 이 repo가 public이라는 항목은 남긴다. 문서에 따르면 classifier는 명령만 읽고 그 출력은 읽지 않으므로 `gh repo view` 결과로는 이 사실이 전달되지 않는다. repo 이름을 직접 적었으므로 어느 프로젝트에서 읽어도 맞다.
- 이 repo에만 해당하는 맥락(`bin/` 도구가 routine이라는 것, secret을 다루는 방식)은 CLAUDE.md에 이미 있고, classifier도 CLAUDE.md를 읽는다.
- 초안에 있던 다른 작업 디렉터리 이름 목록은 뺐다. 기본 Trusted repo 문구가 같은 규칙을 이미 담고 있고, 이 repo는 public이라 commit하면 이름이 공개된다.

## Consequences

- 고친 뒤 이 repo와 app-in-toss에서 `claude auto-mode config`의 environment는 22개다. 기본 21개가 원문 그대로 있고 더한 항목이 하나다. `allow`, `soft_deny`, `hard_deny`는 기본값 그대로다.
- `/auto-mode-setup`을 다시 돌리면 같은 모양의 초안이 나올 수 있다. 받아들이기 전에 Trusted repo와 Source control이 특정 repo로 고정되었는지 본다.
