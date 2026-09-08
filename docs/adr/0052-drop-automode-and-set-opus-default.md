# 0052 — user settings에서 autoMode를 제거하고 기본 model을 opus[1m]으로

기본 model을 `opus[1m]`으로 두고, effortLevel은 fable이 high, opus가 xhigh다. `autoMode.environment` 블록 25개 항목은 제거했다.

`autoMode` 블록은 2026-09-07에 playable-phaser-template에서 실행한 `/auto-mode-setup`이 만든 것이다. `~/.claude/settings.json`이 이 repo의 파일을 가리키는 symlink라서 tracked 파일에 그대로 기록됐다. 제거한 이유는 둘이다. 첫째, 이 repo는 public인데 블록이 private repo인 GiverGround/playable-phaser-template의 이름과 보안 구성을 담고 있었다. 둘째, classifier는 `autoMode`를 user scope에서만 읽어 모든 프로젝트에 적용하는데, Trusted repo와 Repository visibility가 특정 repo로 고정돼 있어 public인 이 repo를 private으로 알려 주고 있었다. 문서상 visibility는 confidential material을 commit해도 되는지를 가르는 기준이라, 판단이 느슨해지는 방향으로 틀린 상태였다.

## Consequences

- 제거 후 `claude auto-mode config`의 environment는 built-in 21개로 돌아갔고 playable-phaser 참조는 없다. Trusted repo는 다시 "작업 중인 repository와 그 remote"라는 동적 표현이다.
- built-in 기본값도 repository를 일단 private으로 가정한다. 대화 안의 증거로만 바뀌고 `gh repo view` 출력은 classifier에 닿지 않으므로, public임을 알리려면 사용자가 직접 문장으로 말해야 한다.
- auto mode가 다시 일상 작업을 막으면 `/auto-mode-setup`을 쓰되 특정 repo 이름을 넣지 않은 중립적 항목으로 쓴다. 이 파일은 public repo에 들어간다.
- 이 사고의 일반형은 machine의 어떤 session이든 symlink를 통해 user scope 설정을 이 repo의 tracked 파일에 쓸 수 있다는 것이다. `install.sh`가 만드는 구조상 피할 수 없으므로 commit 전에 diff를 본다.
