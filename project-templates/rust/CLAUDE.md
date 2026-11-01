# {{PROJECT_NAME}}

Rust project. Replace `{{PROJECT_NAME}}` and fill in the sections below.

## Architecture

(Brief overview.)

## Commands

- Build: `cargo build`
- Test: `cargo test`. Leave out `--all-targets`, which skips doctests.
- Lint: `cargo clippy --all-targets --all-features`
- Format: `cargo fmt`. To check without rewriting: `cargo fmt --check`.
- Docs: `cargo doc --no-deps`

## Conventions

- Edition: `edition` in `Cargo.toml`. `cargo new` writes 2024, which needs Rust 1.85 or later.
- Fix every Clippy and rustc warning before calling a change done. The Lint command doesn't deny warnings, so read its output, not its exit code.
- Format through `cargo fmt`. A bare `rustfmt <file>` doesn't read `Cargo.toml` and formats as edition 2015, so it rejects `async fn`.
- `cargo publish` is denied in `.claude/settings.json`. A publish to crates.io can't be undone, so the user runs it.
- The rust-analyzer-lsp plugin needs the `rust-analyzer` binary. With rustup, `~/.cargo/bin/rust-analyzer` is only a proxy until the component is installed: `rustup component add rust-analyzer`.
- Install the plugin once per machine: `claude plugin install rust-analyzer-lsp@claude-plugins-official --scope project`.
