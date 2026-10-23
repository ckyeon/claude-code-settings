# 0097 — 새 프로젝트에서 Claude가 project template 적용을 제안한다

새 프로젝트에서 세션이 시작되면 user scope의 SessionStart hook이 Claude에게 안내를 남긴다. Claude는 프로젝트 종류가 드러나는 첫 요청에서 template 적용을 한 번 제안하고, 사용자가 승인하면 `apply-project-template` skill의 절차대로 적용한다. 복사는 새 script `bin/apply-template`이 맡는다. 이전에는 README의 `cp -r` 절차를 사람이 직접 실행해야 했고, `~/workspace`에서 template으로 만든 프로젝트는 하나도 없었다. 용어는 GLOSSARY의 "프로젝트 template" 절에 정했다.

## 결정

**적용 방식**
- template 적용은 복사 한 번으로 끝난다. 복사한 파일은 그 프로젝트의 것이 되고, template이 나중에 바뀌어도 따라가지 않는다.
- template은 프로젝트 종류로 고른다. 종류는 기술 스택일 수도 있고 영상 편집 같은 작업 종류일 수도 있다.
  - 여러 종류가 맞으면 가장 구체적인 것을 고른다. 서로 다른 종류가 둘 맞으면 어느 쪽이 주된 종류인지 묻는다.
  - 맞는 종류가 없으면 제안하지 않는다. `_base`는 종류별 template과 함께만 들어간다.
- 사용자가 직접 요청하면 이미 써 오던 프로젝트에도 적용한다.

**판정과 제안**
- hook은 `startup`일 때만 돈다. 아래 조건을 모두 만족하면 새 프로젝트로 본다.
  - `cwd`가 home 디렉터리가 아니고, `$TMPDIR`나 `/tmp` 아래도 아니다.
  - `CLAUDE.md`도 `.claude/settings.json`도 없다.
  - commit이 1개 이하다.
  - `.git`, `node_modules`, `.venv` 밖의 파일이 모두 ctime 기준 24시간 이내에 생겼다.
- 시각을 mtime이 아니라 ctime으로 재는 이유: zip을 풀어 template을 받는 scaffolder는 mtime을 옛 값으로 남길 수 있다.
- 파일이 2000개를 넘으면 새 프로젝트로 보지 않는다. 세션 시작이 늦어지지 않게 하려는 상한이다.
- 제안은 작업을 시작하기 전에 한 번 한다. 거절하면 그 세션에서는 다시 묻지 않는다. 다음 세션에서는 판정이 유지되는 동안 다시 묻는다. 거절 기록은 남기지 않는다.

**절차**
- scaffolder를 먼저 돌리고 template을 나중에 적용한다. 순서가 반대면 두 가지 문제가 생긴다.
  - create-next-app 16.4.2의 `isFolderEmpty`는 `.claude`는 허용하지만 `CLAUDE.md`가 있으면 실행을 거부한다.
  - HyperFrames 0.8.181은 `CLAUDE.md`를 조건 없이 덮어쓴다.
- scaffolder가 만든 agent용 파일은 이렇게 다룬다.
  - `AGENTS.md`는 남기고, `CLAUDE.md` 첫 줄에 `@AGENTS.md`를 넣는다. 공식 문서(code.claude.com/docs/en/memory#agents-md)에 따르면 Claude Code는 `CLAUDE.md`가 없을 때만 `AGENTS.md`를 읽는다.
  - HyperFrames가 만든 `CLAUDE.md`는 `AGENTS.md`와 내용이 같을 때만 지운다.
  - `hyperframes init`에는 언제나 `HYPERFRAMES_SKIP_SKILLS=1`을 붙인다. 이 변수가 없으면 skill이 `~/.claude/skills`, 곧 이 repo의 `user/shared/skills`에 복사되어 ADR 0058의 "project scope로만 켠다"와 어긋난다.
  - Remotion `create-video`의 skill 설치는 건너뛴다. 설치하면 `.claude/skills`가 symlink가 되고, 같은 skill은 `remotion@remotion` plugin이 이미 준다.
- plugin은 `--scope project`로 설치한다. marketplace가 이 기기에 등록되어 있지 않으면 등록 명령만 안내한다. skill이 `marketplace add`를 직접 실행하면 `--scope`를 빠뜨렸을 때 이 repo의 settings가 바뀌기 때문이다(ADR 0095).

**구조**
- 정해진 대로 하면 되는 단계는 `bin/apply-template`에, 판단이 필요한 단계는 skill에 둔다.
- skill 폴더의 `apply-template`은 `bin/apply-template`을 가리키는 상대 경로 symlink다. script는 `$0`이 아니라 자기 실제 경로에서 repo 위치를 구한다. 그래서 repo를 어디에 clone했든 같은 경로로 실행된다.
- script의 규칙:
  - `.provenance.json`과 `.gitignore.snippet`은 복사하지 않는다.
  - snippet은 이미 있는 줄을 빼고 `.gitignore`에 덧붙인다.
  - 복사할 파일이 이미 있거나 경로 중간에 symlink가 있으면 아무것도 복사하지 않는다.
  - `{{PROJECT_NAME}}`은 디렉터리 이름으로 바꾼다.

## Considered Options

- **skill만 둔다.** 사용자가 "새 프로젝트 만들자"라고 말할 때만 불린다. scaffolder를 직접 돌린 뒤 Claude Code를 처음 열고 다른 요청을 하는 경우는 놓친다.
- **user scope CLAUDE.md에 규칙을 적는다.** 모든 세션이 그 문장을 늘 읽어야 한다. 실제로 제안할지는 모델이 기억해 내는지에 달려 있다.
- **template을 계속 동기화한다.** 프로젝트가 고친 파일과 template의 변경이 부딪친다. 복사한 파일은 그 프로젝트의 것이라는 README의 Scope 원칙과도 어긋난다.
- **거절을 기록한다.** 상태 파일을 repo 밖에 하나 더 두고 지울 시점까지 정해야 한다. 다시 묻는 기간이 길어야 하루라서 그만한 이득이 없다.

## Consequences

- `user/shared/settings.json`에 SessionStart hook을 더했다. 이 기기에서는 이 파일이 symlink이므로 새 세션부터 바로 동작한다. 다른 기기는 `install.sh`를 다시 돌릴 필요가 없다. `hooks/shared`와 `skills`가 이미 symlink되어 있기 때문이다.
- CLAUDE.md의 guardrail에 `user/shared/hooks/`를 더했다. 새 hook의 판정 규칙은 `tests/test_suggest_project_template.py`가 조건마다 시험한다. 판정이 틀려도 오류가 나지 않고 안내만 조용히 빠지거나 더해지므로, 시험 말고는 알 방법이 없다. guard hook의 시험은 ADR 0094대로 그 hook의 logic을 바꿀 때 더한다.
- `bin/check-integrity`의 built-in 목록에 `reload-plugins`를 더했다. skill 본문이 이 명령을 안내하기 때문이다.
- 판정 규칙이 놓치는 경우가 둘 있다.
  - 사용자가 HyperFrames를 직접 돌린 디렉터리. HyperFrames가 `CLAUDE.md`를 쓰기 때문이다. 이 경우는 직접 요청해야 한다.
  - `evals/run.py`를 `--work-root`로 임시 디렉터리 밖에서 돌린 경우. 이때는 eval 작업 디렉터리가 새 프로젝트로 보일 수 있다.
- ctime은 `chmod` 같은 메타데이터 변경에도 바뀐다. 그래서 오래된 디렉터리가 새 프로젝트로 보일 수 있다. 다만 그런 디렉터리 대부분은 `CLAUDE.md`나 commit 수 조건에서 걸러진다.
- 안내를 받은 Claude가 실제로 제안하는지는 모델에 달려 있어 자동 시험으로 확인할 수 없다. `~/workspace` 아래 빈 디렉터리에서 세션을 열어 직접 확인한다.
