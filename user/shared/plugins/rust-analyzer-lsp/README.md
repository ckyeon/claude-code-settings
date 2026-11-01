# rust-analyzer-lsp (declared)

This directory is a declaration. The rust-analyzer-lsp plugin is **not** vendored here.

## What it does

Rust language server integration for Claude Code: runs `rust-analyzer` for `.rs` files, providing go-to-definition, find references, and diagnostics.

## Prerequisites

`rust-analyzer` on `PATH`. With rustup, `~/.cargo/bin/rust-analyzer` exists as a proxy but fails with `Unknown binary 'rust-analyzer'` until the component is installed:

```bash
rustup component add rust-analyzer
```

## How it's actually installed

Project scope only, from inside a Rust project:

```
claude plugin install rust-analyzer-lsp@claude-plugins-official --scope project
```

Run that in your shell, or run `/plugin install rust-analyzer-lsp@claude-plugins-official` in a session and choose project scope. The shell command defaults to user scope, which turns it on in every project.

## Where it's enabled

Project-scope only (not user-scope). Enabled in:
- `project-templates/rust/.claude/settings.json`
