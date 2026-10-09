# 0074 — repo의 목적을 재현으로 정하고, 관리 수준을 소유, 선언, 범위 밖으로 나눈다

2026-10-09 점검 뒤 이 repo가 Claude 설정 가운데 무엇을 책임지는지 조사했다. "관리"라는 말이 symlink로 적용하는 것, 목록만 적어 두는 것, 손대지 않는 것을 모두 가리키고 있었고, 범위 설명은 README의 두 절과 `CLAUDE.md`에 나뉘어 서로 어긋나 있었다. `/grill-with-docs`로 경계를 다시 정했다.

## 결정

- **목적은 재현이다.** 새 기기에서 이 repo와 그 안의 문서만으로 같은 Claude Code 환경을 만든다. 어떤 항목을 제대로 관리하는지는 이 기준으로 가른다.
- **관리 수준은 셋이다.** 소유는 repo의 파일이 곧 적용되는 설정인 상태다. 선언은 repo가 항목의 목록과 만드는 command를 적고 실제 적용은 기기에서 사람이 하는 상태다. 범위 밖은 repo가 저장하지도 점검하지도 않는 상태다. 용어는 `GLOSSARY.md`에 둔다.
- **출처는 별개의 축이다.** "추적"은 upstream 비교의 뜻으로만 쓰고, 목록에 올린다는 뜻으로는 "선언"을 쓴다.
- **분류 원칙**: 사람이 쓰고 secret이 없는 설정 파일은 소유한다. 기기에서 명령으로 만드는 것은 선언한다. Claude Code나 계정이 쓰는 상태와 secret의 값은 범위 밖이다.
- **대상은 Claude Code뿐이다.** Codex 설정은 범위 밖이다.
- **Linux 쪽은 검증되지 않았다고 표시한다.** 사용자가 Linux 기기에서 직접 검증할 예정이다.

## 항목별 분류에서 갈린 것

- **plugin**: "어떤 plugin을 어느 marketplace에서 받는가"까지 선언한다. 설치된 version은 plugin CLI가 제 일정대로 올리므로 범위 밖이다. sidecar의 pin은 마지막으로 내용을 검토한 upstream 시점을 뜻한다.
- **secret**: 값은 범위 밖이다. 이름과 넣는 위치는 선언한다(ADR 0077).
- **memory**: 범위 밖이다. 기기의 절대 경로로 저장되는 작업 상태이고, 소유하면 다른 프로젝트의 상태가 이 repo에 쌓인다. 기기를 바꿔도 남아야 하는 교훈은 소유 파일로 옮긴다.
- **Discord의 `access.json`**: 범위 밖이다. discord plugin의 skill이 쓰는 상태이고, 원격으로 기기를 조작하는 통로이므로 기기마다 접근을 다시 허용하는 편이 안전하다.
- **template을 복사해 간 프로젝트**: 범위 밖이다. 각 프로젝트는 자기 repo에 `.claude/`를 담고 있어 그 repo만으로 재현된다.
- **claude.ai에서 동기화되는 skill, plugin, connector**: 범위 밖이다. 계정을 따라오므로 로그인하면 생긴다.

## 문서

- README의 "Scope" 절이 항목별 수준의 원본이다. "Scope model"과 "What this repo deliberately does NOT manage" 두 절을 이 절로 합쳤다.
- `CLAUDE.md`에는 분류 원칙과 README를 가리키는 문장만 둔다. template 이름처럼 폴더를 보면 아는 목록은 뺐다. `CLAUDE.md`가 template을 6개로 적고 실제는 8개였던 것이 이런 목록에서 나온 어긋남이다.
- `CLAUDE.md`, README, `docs/PROVENANCE.md`의 "Track a plugin", "provenance-only" 표현과 `install.sh`, `uninstall.sh`의 출력 문구를 "declare"로 바꿨다. ADR은 기록이므로 고치지 않았다.
- README의 요구 사항을 "Bash 4.0+"에서 "Bash 3.2+"로 고쳤다. script에 bash 4 전용 문법이 없고 macOS 기본 bash 3.2.57로 문법 검사를 통과한다.

## Considered Options

- **목적을 "설정의 version 관리"로 두기**: 어떤 항목이 빠져도 문제를 알 수 없다. 재현은 항목마다 예, 아니오로 답할 수 있어 기준으로 쓸 수 있다.
- **memory를 소유하기**: 재현에는 유리하지만 다른 프로젝트의 작업 상태까지 이 repo에 들어온다.
- **template과 복사본을 동기화하는 도구**: 복사본이 `video-edit-test` 하나뿐이라 과하다.

## Consequences

- 지금 있는 feedback과 user 유형 memory 38개는 소유 파일로 옮기지 않는 한 새 기기에서 없어진다. 옮길 것을 고르는 일은 별도 작업이다.
- 설치된 plugin이 pin보다 뒤처지거나 앞설 수 있다. 2026-10-09 기준으로 `remotion`과 `understand-anything`의 설치본이 pin보다 오래됐다.
- `lib/common.sh`의 `list_tracked_plugins`, `list_tracked_mcp_servers`와 각 plugin README의 문구는 예전 용어 그대로다.
- 선언한 것과 기기의 실제 상태가 같은지는 `bin/check-machine`이 확인한다(ADR 0078).
