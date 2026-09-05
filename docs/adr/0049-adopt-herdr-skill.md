# 0049 — herdr skill을 herdrdev/herdr@9eb52145(v0.8.2 release)에서 채택

Herdr pane 안에서 실행 중인 agent가 `herdr` CLI로 pane, tab, workspace를 조작하고 다른 agent를 띄우는 방법을 담은 `skills/herdr/SKILL.md`를 `copied`로 채택했다. upstream이 권장하는 `npx skills add herdrdev/herdr --skill herdr -g`는 `~/.claude/skills/`에 직접 써서 이 repo의 symlink와 provenance를 우회하므로 택하지 않았다. 설치된 herdr 0.8.2가 `herdr --skill`로 출력하는 파일과 채택본은 바이트 단위로 동일하다.

## Consequences

- pin은 master HEAD가 아니라 v0.8.2 release commit이다. upstream 정책(AGENTS.md, pre-commit hook)상 이 파일은 stable release 때만 바뀌므로, release commit에 고정하면 `check-updates`가 release 사이의 무관한 commit을 "outdated"로 보고하더라도 tracked path는 바뀌지 않았다고 판정할 수 있다.
- skill은 시작 전에 `HERDR_ENV=1`을 검증하고 아니면 중단한다. Herdr 바깥 세션에서는 트리거 조건(사용자가 Herdr를 명시적으로 언급)이 맞아도 동작하지 않는다.
- 다른 skill을 참조하지 않는 단일 파일이라 integrity check는 추가 의존성 없이 clean이다. upstream `.agents/skills/` 아래의 개발자용 skill 세 개(triage, herdr-pre-release-audit, herdr-throwaway-repro)는 사용자 설치 대상이 아니라 채택하지 않았다.
