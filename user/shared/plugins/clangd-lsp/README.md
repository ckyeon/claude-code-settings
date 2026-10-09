# clangd-lsp (declared)

This directory is a declaration. The clangd-lsp plugin is **not** vendored here.

## What it does

C/C++ language server integration for Claude Code: runs `clangd --background-index` for `.c`, `.h`, `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hxx`, `.C`, `.H` files, providing go-to-definition, find references, and diagnostics.

## Prerequisites

`clangd` on `PATH`. macOS has `/usr/bin/clangd` from the Xcode Command Line Tools; the plugin's README suggests `brew install llvm` (then `/opt/homebrew/opt/llvm/bin` on `PATH`) for a current one. clangd also needs the project's build flags in `compile_commands.json` (see `project-templates/cpp/CLAUDE.md`).

## How it's actually installed

Project scope only, from inside a C/C++ project:

```
claude plugin install clangd-lsp@claude-plugins-official --scope project
```

Run that in your shell, or run `/plugin install clangd-lsp@claude-plugins-official` in a session and choose project scope. The shell command defaults to user scope, which turns it on in every project.

## Where it's enabled

Project-scope only (not user-scope). Enabled in:
- `project-templates/cpp/.claude/settings.json`
