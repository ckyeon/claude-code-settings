# {{PROJECT_NAME}}

C/C++ project. Replace `{{PROJECT_NAME}}` and fill in the sections below.

## Architecture

(Brief overview.)

## Commands

- Configure: `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=1`
- Build: `cmake --build build`
- Test: `ctest --test-dir build`
- Format: `clang-format -i <files>`

## Conventions

- Standard: C++ version pinned in `CMakeLists.txt` (`CMAKE_CXX_STANDARD`).
- The clangd-lsp plugin needs build flags. clangd reads `compile_commands.json` from the edited file's parent directories and from `build/`; the configure command above writes it there. For make-based builds, generate it with `bear -- make`.
- Install the plugin once per machine: `claude plugin install clangd-lsp@claude-plugins-official --scope project`. `clangd` must be on `PATH` (macOS ships one with the Xcode Command Line Tools; `brew install llvm` gives a newer one).
