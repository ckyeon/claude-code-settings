# 0130 — password를 묻는 명령은 Claude Code 밖 terminal에서 실행하도록 안내한다

`user/shared/CLAUDE.md` 3절에 한 항목을 더했다. `sudo`처럼 password를 묻는 명령은 `! <command>`로 실행하라고 하지 않고, 사용자가 자기 terminal에서 실행할 명령으로 적어 준다. `!` 명령에는 TTY가 없어서 password를 입력받지 못한다.

## 경위

- 다른 프로젝트의 세션이 inbox에 남긴 건의(ADR 0098)에서 왔다. 그 세션은 원격 서버의 `sudo` 명령을 `! ssh -t <host> 'sudo ...'`로 실행하라고 안내했고, 사용자가 그대로 실행하자 실패했다.
- 실패 출력은 `Pseudo-terminal will not be allocated because stdin is not a terminal.`와 `sudo: a terminal is required to read the password`였다. `!` 명령의 stdin이 terminal이 아니라는 직접 증거다.
- Claude Code system prompt는 `!`를 "an interactive login like `gcloud auth login`"에 쓰라고 예를 들어서, 대화형 입력이 되는 것처럼 읽힌다. 이 항목은 그 안내가 password 입력에는 맞지 않는다는 점을 적는다.

## 결정

- **전역 `CLAUDE.md`에 둔다.** 같은 사실을 이미 두 프로젝트가 각자 따로 적고 있었다. 한 곳에 두면 다음 프로젝트에서 같은 실패를 막는다.
