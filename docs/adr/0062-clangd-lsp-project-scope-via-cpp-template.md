# 0062 — clangd-lsp를 C/C++ 프로젝트 전용으로: user scope에서 빼고 `cpp` template 추가

2026-09-28에 user scope로 설치된 clangd-lsp(C/C++ language server plugin)가 `user/shared/settings.json`의 `enabledPlugins`에 들어가 있었고, commit `92f49b6`(ADR 0061)에 기록 없이 섞여 들어갔다. 사용자는 C/C++ 프로젝트에서만 쓰기를 원한다. 그래서 user scope에서 제거하고(`claude plugin uninstall ... --scope user`), typescript-lsp와 같은 방식으로 새 `project-templates/cpp/`의 settings에서만 켠다. provenance는 `user/shared/plugins/clangd-lsp/`에 기록했다.

## Considered Options

- **template 없이 기록만**: 파일은 덜 늘지만 어떤 settings에서도 켜지지 않아 `install.sh`가 경고로 표시한다. 사용 가능한 설치 명령을 안내하는 기존 구조(ADR 0007)와 맞지 않아 택하지 않았다.

## Consequences

- `cpp` template은 go template처럼 CLAUDE.md와 settings.json 두 파일이다. 권한 allow 목록은 비워 뒀다.
- clangd는 build flag를 `compile_commands.json`에서 읽는다. clangd 문서(clangd.llvm.org/installation)에 따라 CMake 설정 명령에 `-DCMAKE_EXPORT_COMPILE_COMMANDS=1`을 넣고, make 기반이면 `bear -- make`를 쓰라고 template CLAUDE.md에 적었다.
- 이 머신에서는 plugin이 제거된 상태다. C/C++ 프로젝트를 만들면 그 안에서 `--scope project`로 다시 설치한다.
