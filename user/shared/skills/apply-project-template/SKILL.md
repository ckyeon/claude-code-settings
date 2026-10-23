---
name: apply-project-template
description: 프로젝트에 이 기기의 project template(nextjs, nodejs, phaser, python, go, cpp, video)을 적용한다. SessionStart 안내가 새 프로젝트라고 알렸을 때, 사용자가 새 프로젝트를 만들기 시작할 때, 사용자가 template 적용을 요청할 때 쓴다.
---

# Project template 적용

template은 이 skill 디렉터리의 `apply-template`이 복사한다. 이 파일은 설정 repo의 `bin/apply-template`을 가리키는 symlink이고, 복사 규칙과 옵션은 `--help`가 정본이다. 복사한 파일은 그 프로젝트의 것이 되고 template이 바뀌어도 따라 바뀌지 않는다.

## 1. 종류를 고른다

| 단서 | 종류 |
|---|---|
| `package.json`에 `next` | nextjs |
| `package.json`에 `phaser` | phaser |
| `package.json`에 `remotion`, HyperFrames 프로젝트, 영상 편집 요청 | video |
| 그 밖의 `package.json` | nodejs |
| `pyproject.toml`, `requirements.txt`, `uv.lock` | python |
| `go.mod` | go |
| `CMakeLists.txt`, C++ 소스 | cpp |

- 파일이 아직 없으면 사용자의 요청에서 종류를 읽는다.
- 여러 줄이 맞으면 위쪽의 더 구체적인 종류를 고른다.
- 서로 다른 종류가 둘 맞으면, 예를 들어 Go 서버와 Next.js 화면이면 어느 쪽이 주된 종류인지 묻는다. template은 하나만 적용한다.
- 맞는 종류가 없거나 요청이 프로젝트와 무관하면 여기서 멈추고 template을 언급하지 않는다.

종류 하나가 정해지면 이 단계가 끝난다.

## 2. 한 번 묻는다

파일을 만들거나 scaffolder를 돌리기 전에 "`<종류>` template을 적용할까요?"라고 한 번 묻는다. template이 더하는 것을 함께 적는다. permission, project skill, 설치할 plugin이 여기에 들어가며, 종류별 template의 `.claude/settings.json`과 `.claude/skills/`를 읽어 확인한다.

- 승인하면 3단계로 간다.
- 거절하면 요청받은 일만 하고, 이 세션에서는 다시 묻지 않는다.

사용자가 template 적용을 직접 요청했으면 이 단계를 건너뛴다.

## 3. scaffolder를 먼저 돌린다

요청에 scaffolder가 필요하면 template보다 먼저 돌린다. template의 `CLAUDE.md`가 먼저 있으면 create-next-app이 실행을 거부하고, HyperFrames는 그 파일을 덮어쓴다.

- **create-next-app**: `--no-agents-md`를 주지 않는다. `AGENTS.md`는 4단계에서 `CLAUDE.md`가 불러온다.
- **HyperFrames `init`**: 언제나 `HYPERFRAMES_SKIP_SKILLS=1`을 붙인다. 이 변수가 없으면 skill이 `~/.claude/skills`에 복사되는데, 그곳은 설정 repo의 `user/shared/skills`다. HyperFrames는 template이 켜는 plugin으로 project scope에서만 쓴다.
- **Remotion `create-video`**: skill 설치를 건너뛴다(`--yes` 또는 "Skip skill installation"). 설치하면 `.claude/skills`가 `.agents/skills`로 가는 symlink가 된다. 같은 skill은 template이 켜는 `remotion@remotion` plugin이 준다.

HyperFrames는 `AGENTS.md`와 같은 내용의 `CLAUDE.md`를 만든다. `cmp CLAUDE.md AGENTS.md`로 같은지 확인하고, 같으면 `CLAUDE.md`를 지운다. 다르면 멈추고 사용자에게 묻는다.

scaffolder가 프로젝트 디렉터리를 새로 만들었으면, 4단계부터는 그 디렉터리가 대상이다.

## 4. template을 복사한다

```bash
<이 skill 디렉터리>/apply-template <종류> <프로젝트 디렉터리>
```

- 종료 코드가 0이면 출력의 마지막 줄에 설치할 plugin 목록이 있다.
- 종료 코드가 1이면 아무것도 복사되지 않은 것이다. 출력에 나온 경로 목록을 사용자에게 보여 주고, 어떻게 할지 묻는다. 겹치는 파일은 사용자가 정하기 전까지 그대로 둔다.

## 5. plugin을 설치한다

4단계가 출력한 plugin마다, 프로젝트 디렉터리 안에서 실행한다.

```bash
claude plugin install <plugin>@<marketplace> --scope project
```

- **marketplace가 이 기기에 등록되어 있지 않다는 오류가 나면** 그 plugin은 건너뛴다. 사용자에게 이 기기가 아직 재현되지 않았다고 알린다. 그리고 template의 `extraKnownMarketplaces`에 적힌 repo로 `claude plugin marketplace add <owner>/<repo>`를 안내한다. 이 명령은 사용자가 실행한다. `--scope` 없이 실행하면 설정 repo의 `user/shared/settings.json`이 바뀌기 때문이다.
- **`Host key verification failed`가 나면** `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`을 붙여 한 번 더 실행한다.

모든 plugin이 설치되거나 건너뛴 이유가 사용자에게 전달되면 이 단계가 끝난다.

## 6. 마무리를 알린다

사용자에게 다음을 알린다.

- 적용한 template과 복사한 파일 수. 파일은 commit하지 않은 상태로 남아 있다.
- plugin을 설치했으면, `/reload-plugins`를 실행하거나 세션을 새로 열어야 plugin이 켜진다는 것.
- `CLAUDE.md`의 Architecture, Commands, Conventions 절은 template 문구 그대로이니 채워 넣어야 한다는 것.

그다음 요청받은 일을 이어서 한다.
