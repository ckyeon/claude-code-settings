# 0112 — rust template을 세션에서 시험하고 두 곳을 고침

ADR 0111의 rust template을 실제 Claude Code 세션에서 시험했다. 그 결과 `.gitignore`에 `/target`이 빠지는 경우와 `CLAUDE.md`의 edition 문구가 실제와 다른 것을 찾아 고쳤다.

## 시험

Claude Code 2.1.314와 Opus 5.5로 `claude -p`를 세 번 실행했다. 환경 변수는 `evals/run.py`와 같은 방식으로 정리했고, 실행한 곳은 `~/workspace` 아래 빈 디렉터리다.

1. "Rust로 텍스트 파일의 단어 수를 세는 CLI 만들어줘."라고 요청했다. SessionStart hook의 안내를 받은 Claude가 `apply-project-template` skill을 불러 rust template을 골랐고, 적용할지 물었다.
2. 같은 세션을 이어 승인했다. Claude는 `cargo init`, `apply-template rust`, `claude plugin install ... --scope project` 순서로 실행했다. scaffolder를 template보다 먼저 돌린다는 skill의 순서를 지켰다.
3. 새 세션에서 일부러 타입 오류를 만들었다. 그러자 rust-analyzer의 진단(E0308 등)이 들어왔다. `cargo publish --dry-run`은 deny 규칙에 막혔다.

## 고친 것

- **`.gitignore.snippet` 추가.** 2번에서 Claude는 `cargo init --vcs none`을 썼다. cargo는 VCS를 만들지 않으면 `.gitignore`도 만들지 않는다. 그래서 template이 넣은 `.claude/settings.local.json` 한 줄만 남았다. 종류별 template의 snippet은 `_base`의 snippet을 대신하므로, 두 줄을 모두 rust template의 snippet에 넣었다. `cargo new`(git)로 만든 경우와 `cargo init --vcs none`으로 만든 경우 모두 두 줄이 남는 것을 확인했다.
- **edition 문구.** `CLAUDE.md`는 `rust-version`이 `Cargo.toml`에 고정되어 있다고 적었다. 그러나 `cargo new`와 `cargo init`은 이 키를 쓰지 않는다. 시험 세션의 Claude가 이 불일치를 짚었다. edition만 적도록 고쳤다.

## Consequences

- 3번에서 Claude Code는 `Bash(cargo:*)` 허용 규칙이 있는데도 `cargo build` 실행 승인을 물었다. permission 문서(code.claude.com/docs/en/permissions)에 따르면 project의 `permissions.allow`는 workspace trust를 받은 뒤에만 적용되고, `claude -p`에서는 적용되지 않는다. deny 규칙은 trust와 상관없이 적용된다. 그래서 허용 규칙은 대화형 세션에서 trust를 승인해야 확인할 수 있고, 아직 확인하지 않았다.
- 1번에서 Claude는 template 내용을 읽지 못한 채 적용할지 물었다. `-p`에서는 작업 디렉터리 밖의 파일을 읽을 때 필요한 승인 요청에 아무도 답할 수 없기 때문이다. 대화형 세션에서는 사용자에게 권한을 묻는다.
- 시험 디렉터리, 그 안에 project scope로 설치한 plugin, 시험 세션 기록은 시험 뒤에 지웠다.
