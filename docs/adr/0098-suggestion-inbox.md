# 0098 — 다른 프로젝트의 세션은 설정 변경을 inbox에 건의로 남긴다

다른 프로젝트 세션에서 사용자 설정에 고칠 점이 보이면 Claude가 건의를 제안한다. 사용자가 승인하면 user scope skill `suggest-setting`이 이 repo의 `inbox/`에 건의를 파일 하나로 남긴다. 이 repo에서 세션을 열면 project scope `SessionStart` hook이 건수를 알리고, 처리는 CLAUDE.md의 "Process suggestions" 절차를 따른다. 용어는 GLOSSARY의 "건의" 절에 정했다.

## 경위

- `~/.claude` 아래의 `skills`, `rules`, `settings.json`은 디렉터리나 파일째 이 repo로 symlink되어 있다. 그래서 다른 프로젝트 세션이 `~/.claude` 아래를 고치면 ADR, provenance, `check-integrity`를 거치지 않고 이 repo의 파일이 바로 바뀐다.
- `retro` skill도 개선 후보를 찾지만, 마지막 단계가 "Present these candidates to the user"여서 결과가 대화창에만 남는다.

## 결정

- 건의는 이 기기의 `inbox/`에 두고 gitignore한다. 이 repo는 public이므로 GitHub Issues나 commit하는 폴더에 쓰면 다른 프로젝트의 경로와 코드가 공개된다. 그 대가로 건의는 다른 기기와 공유되지 않는다. 받아들인 건의는 ADR로 남으므로 재현에는 영향이 없다.
- 건의 하나에 파일 하나를 쓴다. 그러면 두 세션이 동시에 써도 같은 파일을 건드리지 않는다. 파일 이름은 시각과 제목으로 만들고, 같은 이름이 있으면 번호를 붙인다.
- Claude가 건의를 제안하고, 사용자가 승인하면 남긴다. 사용자만 호출할 수 있게 하면 사용자가 skill을 기억해야 한다. 묻지 않고 남기면 쓸모없는 건의가 쌓인다.
- 다른 세션이 설정을 직접 고치는 것은 막지 않는다. `PreToolUse` hook으로 Edit과 Write는 막을 수 있지만 Bash와 외부 설치 프로그램은 막지 못한다. 건의를 먼저 써 보고, 직접 수정이 계속 문제가 되면 다시 정한다. 사용자가 직접 고치라고 한 경우에도 무엇을 왜 고쳤는지 건의로 남겨, 이 repo에서 ADR과 commit으로 마무리한다.
- 구조는 ADR 0097을 따른다. 파일을 쓰는 일은 `bin/suggest-setting`이 맡고, 건의할지 판단하는 일은 skill이 맡는다. skill 폴더의 `suggest-setting`은 script를 가리키는 상대 경로 symlink이고, script는 자기 실제 경로에서 repo 위치를 구한다.
- 건의를 받아들여 쓰는 ADR에는 설정의 문제만 적고, 다른 프로젝트의 이름, 경로, 코드는 적지 않는다. ADR도 공개되기 때문이다.
- 받아들이지 않은 건의는 사용자에게 이유를 말하고 지운다. 따로 기록하지 않는다.

## 남은 일

- 외부 설치 프로그램이 symlink된 디렉터리에 직접 쓴 항목은 건의로 잡히지 않는다. 예를 들어 untracked 상태인 `user/shared/skills/ego-browser`는 ego 설치 프로그램이 만든 symlink다.
- 공식 문서(code.claude.com/docs/en/hooks)는 `systemMessage`에 대해 "Some events discard it or deliver it elsewhere, and each event's section says so."라고 적는다. SessionStart 절에는 그런 언급이 없어서 건수 안내가 사용자에게 보인다고 판단했다. 실제 세션에서 확인해야 한다.
