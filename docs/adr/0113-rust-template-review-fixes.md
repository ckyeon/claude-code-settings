# 0113 — rust template 리뷰 반영

ADR 0111과 0112의 변경(`d69d76a` 이후 commit 둘)을 `code-review` skill로 리뷰했다. 리뷰는 Standards와 Spec 두 축으로 나눠 했다. 지적 가운데 template의 동작과 기록에 관한 것을 고쳤고, 이전부터 있던 구조 문제는 후속 과제로 남겼다.

## 고친 것

- **`cargo publish` deny 규칙을 넓혔다.** cargo의 사용법은 `cargo [+toolchain] [OPTIONS] [COMMAND]`이다. 그래서 `cargo +stable publish`나 `cargo -v publish`는 `Bash(cargo publish:*)`에 걸리지 않고 `Bash(cargo:*)`로 허용됐다. permission 문서도 같은 경우를 든다. 원문은 "A push written another way, such as `git -C . push`, isn't matched"이다.
  - `Bash(cargo * publish)`와 `Bash(cargo * publish *)`를 더했다. 문서에 따르면 끝의 `*`가 인자 없는 명령까지 맞추는 것은 그 `*`가 규칙의 유일한 wildcard일 때뿐이다. 그래서 두 규칙을 따로 둔다.
  - `claude -p`로 확인했다. deny 규칙은 workspace trust 없이도 적용된다. `cargo publish --dry-run`, `cargo +stable publish --dry-run`, `cargo -v publish --dry-run`, `cargo +stable publish`는 모두 "has been denied"였다. 대조로 넣은 `cargo build`는 막히지 않았다.
  - 대신 `cargo run -- publish`도 막힌다. 만드는 프로그램에 `publish`라는 인자가 있으면 사용자가 직접 실행해야 한다.
  - `sh -c` 안의 명령이나 cargo alias는 규칙이 잡지 못한다. 그래서 `CLAUDE.md`에는 deny가 막는다고 쓰지 않고, publish는 사용자가 실행한다고 썼다.
- **`Bash(rustfmt:*)`를 뺐다.** `CLAUDE.md`는 `rustfmt`를 단독으로 실행하지 말라고 한다. `cargo fmt`는 `Bash(cargo:*)`로 이미 허용된다.
- **template `CLAUDE.md`를 줄였다.**
  - 단독 `rustfmt`를 피하라는 경고를 Format 명령 줄로 옮겼다. 같은 뜻이 Conventions에 한 번 더 있었기 때문이다.
  - edition 줄은 go template처럼 "`Cargo.toml`에 고정되어 있다"만 남겼다. cargo의 지금 기본값은 `Cargo.toml`에서 읽을 수 있고, 기본값이 바뀌면 문장이 낡는다.
- **ADR 기록을 바로잡았다.**
  - ADR 0111의 마지막 줄은 permission 규칙을 확인했다고 적었다. 그러나 ADR 0112는 allow 규칙을 확인하지 못했다고 적는다. 0111을 0112에 맞췄다.
  - ADR 0111에 rust-analyzer를 설치한 사실과 이후 바뀐 것을 더했다.
  - ADR 0112의 "kind"를 GLOSSARY의 용어 "종류"로 바꿨고, 번역투 한 문장을 고쳤다.

## 후속 과제

- 종류를 하나 더할 때마다 손으로 관리하는 목록 네 곳을 고쳐야 한다. README의 tree와 `apply-template` 주석, `apply-project-template` skill의 description과 표다. `bin/apply-template`은 이미 디렉터리에서 목록을 만든다.
- 종류별 `.gitignore.snippet`은 `_base`의 snippet에 더해지지 않고 그것을 대신한다. 그래서 nextjs, phaser, video, rust가 `.claude/settings.local.json` 줄을 반복한다.
- commit `f2394c7`은 plugin 하나를 adopt했지만 `Source-Repo` 같은 trailer를 붙이지 않았다. clangd-lsp를 넣은 commit `002049e`와 같다. 출처는 sidecar에 기록되어 있다. template 추가와 adopt가 한 commit에 섞일 때 trailer를 붙일지는 CLAUDE.md가 정하지 않는다.
