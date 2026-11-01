# 0111 — Rust project template `rust` 추가

`project-templates/rust/`를 추가했다. go, cpp template처럼 `CLAUDE.md`와 `.claude/settings.json` 두 파일이고, Anthropic 공식 marketplace의 `rust-analyzer-lsp` plugin을 project scope로 켠다. 사용자가 공식 출처를 우선하고 공신력이나 효과가 검증된 것만 넣기를 원해서, 공개 Rust skill은 넣지 않았다.

## Considered Options

- **BeautifulRust plugin**(morganlinton/BeautifulRust, MIT, skill 3개): 조사한 공개 Rust skill 중 가장 나은 후보였고, 확인한 주장이 모두 맞았다. 하지만 아래 이유로 넣지 않았다.
  - 공식 출처가 아니다. 저장소는 2026-10-23에 만들어졌고 작성자는 한 명이다.
  - README가 밝힌 효과 수치(skill이 있으면 30개 중 29개, 없으면 24개 통과)는 확인하지 못했다.
  - 핵심 skill의 SKILL.md만 29.7KB여서 Rust 작업마다 그만큼 context를 쓴다.
  - 그 안의 Effective Rust 요약은 원서 온라인판 license가 CC BY-NC-ND 4.0이다(lurklurk.org/effective-rust).
- **다른 공개 skill**: apollographql/skills의 `rust-best-practices`는 예제 3개가 실행에서 실패했다. leonardomso/rust-skills에는 틀린 주장이 3개 있었고, actionbook/rust-skills에는 LICENSE 파일이 없었다. microsoft/rust-guidelines가 agent용으로 내는 `all.txt`는 3,500줄이라 template에 넣기에는 크다.
- **clippy 경고를 deny하기**: Clippy 문서(doc.rust-lang.org/clippy/usage.html)는 Cargo 1.97부터 `-- -D warnings` 대신 `build.warnings` 설정을 권한다. 그러나 두 방법 모두 문제가 있다.
  - `CARGO_BUILD_WARNINGS=deny`를 명령 앞에 붙이면 `Bash(cargo:*)` 허용 규칙이 맞지 않을 수 있다. permission 문서에 따르면 known-safe 목록에 없는 변수가 명령 앞에 대입되어 있으면 allow 규칙이 그 명령에 맞지 않는다.
  - `.cargo/config.toml`에 두면 개발 중 build도 경고 하나에 실패한다.
  - 그래서 Lint 명령은 deny하지 않고, `CLAUDE.md`에 경고를 모두 고치라고 적었다.
- **편집할 때마다 format하는 hook**: 다른 template에도 hook이 없고, rust-analyzer가 편집마다 진단을 준다. 넣지 않았다.

## 결정과 근거

- `cargo test`에는 `--all-targets`를 붙이지 않는다. 실패하는 doctest가 있는 crate에서 `--all-targets`를 붙이면 종료 코드가 0이었고, 붙이지 않으면 101이었다.
- format은 `cargo fmt`로 한다. `rustfmt <파일>`은 `Cargo.toml`을 읽지 않고 edition 2015로 동작해서, edition 2024 crate의 `async fn`을 거부했다.
- `Bash(cargo publish:*)`를 deny한다. Cargo 문서(doc.rust-lang.org/cargo/reference/publishing.html)에 따르면 publish한 version은 덮어쓸 수 없고 코드도 지울 수 없다. `cargo publish --dry-run`도 막히므로 publish는 사용자가 직접 실행한다.
- `Bash(cargo:*)`는 go template의 `Bash(go:*)`만큼 넓다. `cargo install`도 묻지 않고 실행된다.

## Consequences

- 이 기기에는 `rust-analyzer` component가 설치되어 있지 않다. `~/.cargo/bin/rust-analyzer`는 rustup의 proxy일 뿐이라 실행하면 `Unknown binary` 오류가 난다. `rustup component add rust-analyzer`를 실행해야 plugin이 동작한다.
- 검증은 cargo 1.99.0으로 scratch 디렉터리에서 했다.
  - `cargo new` 다음에 `bin/apply-template rust`를 실행했다. 그리고 `CLAUDE.md`의 명령 6개를 실행해 모두 종료 코드 0을 확인했다.
  - 순서를 바꿔 template을 먼저 적용하고 `cargo init`을 돌려도 `.gitignore`에 `/target`과 `.claude/settings.local.json`이 모두 남았다.
  - permission 규칙과 plugin 동작은 세션을 열어야 확인할 수 있다. 아직 확인하지 않았다.
