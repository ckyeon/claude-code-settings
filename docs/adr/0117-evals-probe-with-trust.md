# 0117 — 한 디렉터리에서 세션을 한 번 띄우는 `evals/run.py probe`

`evals/run.py`에 `probe` 명령을 더했다. case 없이 기존 디렉터리에서 `claude -p`를 한 번 실행하고, 부른 tool, 거부된 명령, 최종 답을 출력한다. `--trust`를 주면 그 폴더를 trust한 상태로 실행하므로 project의 allow 규칙까지 시험할 수 있다.

## 경위

- `claude -p`는 trust를 받지 않은 폴더에서 project의 `permissions.allow`를 적용하지 않는다. 그래서 ADR 0112의 세션 시험은 rust template의 deny 규칙만 확인했고, allow 규칙은 확인하지 못했다.
- template을 세션에서 시험할 때마다(ADR 0097, 0112) 방법을 즉석에서 만들었다. ADR 0112에서는 `evals/run.py`의 환경 변수 정리를 scratch script로 다시 썼다.

## 결정

- trust는 mirror config 디렉터리의 `.claude.json`에만 기록한다. permission 문서는 `~/.claude.json`의 `projects["<path>"].hasTrustDialogAccepted`를 직접 고치는 방법을 안내한다. 그러나 그 파일은 Claude Code가 쓰는 상태라 이 repo의 범위 밖이다.
- trust의 key는 문서가 정한 대로 git repository 안이면 그 root, 밖이면 그 폴더다.
- mirror는 evals의 `on-mirror` arm과 같은 방법으로 만들고, 실행이 끝나면 지운다.
- `--trust`에서는 `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`을 켠다. mirror는 세션에 token을 환경 변수로 넘기고, trust를 받은 allow 규칙은 `cargo run`처럼 프로그램을 실행할 수 있다. evals README의 "한계"는 Bash를 막아서 모델이 token을 읽지 못한다고 전제하는데, 이 경우에는 그 전제가 깨진다. env-vars 문서에 따르면 이 설정은 Bash 명령, hook, stdio MCP server의 환경에서 인증 정보를 지운다.
- `--trust` 없이 실행하면 평소 config 디렉터리에서 돈다.

## 확인

rust template을 적용한 scratch crate에서 시험했다. `main.rs`는 token 환경 변수가 있는지만 출력하도록 직접 썼다.

- `--trust` 없이 실행했다. `cargo run`은 승인을 기다리며 멈췄고, stderr에 "Ignoring 1 permissions.allow entry from .claude/settings.json: this workspace has not been trusted"가 나왔다. `cargo +stable publish --dry-run`은 deny 규칙에 막혔다.
- `--trust`로 실행했다. `cargo run`이 묻지 않고 실행됐고, rust template의 allow 규칙은 이것으로 처음 확인됐다. 출력은 `CLAUDE_CODE_OAUTH_TOKEN present: false`와 `CLAUDE_CONFIG_DIR present: false`였다.
- 같은 세션에서 Claude는 `cargo +stable publish --dry-run`을 실행하지 않았다. 근거로 template `CLAUDE.md`의 "The user runs every `cargo publish`"를 들었다.
