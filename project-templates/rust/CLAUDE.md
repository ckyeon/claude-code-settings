# {{PROJECT_NAME}}

Rust project. Replace `{{PROJECT_NAME}}` and fill in the sections below.

## Architecture

(Brief overview.)

## Commands

- Build: `cargo build`
- Test: `cargo test`. Leave out `--all-targets`, which skips doctests.
- Lint: `cargo clippy --all-targets --all-features`
- Format: `cargo fmt`. To check without rewriting: `cargo fmt --check`. A bare `rustfmt <file>` doesn't read `Cargo.toml` and formats as edition 2015, so it rejects `async fn`.
- Docs: `cargo doc --no-deps`

## Conventions

- Edition: pinned in `Cargo.toml`.
- Fix every Clippy and rustc warning before calling a change done. The Lint command doesn't deny warnings, so read its output, not its exit code.
- The user runs every `cargo publish`, because a publish to crates.io can't be undone. `.claude/settings.json` denies the common forms of the command, but a rule can't catch every form.
- The rust-analyzer-lsp plugin needs the `rust-analyzer` binary. With rustup, `~/.cargo/bin/rust-analyzer` is only a proxy until the component is installed: `rustup component add rust-analyzer`.
- Install the plugin once per machine: `claude plugin install rust-analyzer-lsp@claude-plugins-official --scope project`.
