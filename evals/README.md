# evals

새 모델이 나올 때마다 user-scope 설정이 그 모델에서도 효과가 있는지 확인하는 eval이다. 같은 과제를 설정을 켠 조건과 일부를 끈 조건에서 반복 실행하고, 구성요소마다 아래 셋 중 하나로 판정한다(ADR 0087).

| 판정 | 조건 | 할 일 |
|---|---|---|
| **유지** | 켠 조건이 의도한 지표에서 끈 조건보다 확실히 낫다 | 그대로 둔다 |
| **중복** | 끈 조건도 이미 점수가 높아 차이가 없다 | 삭제 후보. context 비용만 남는다 |
| **무효** | 두 조건 모두 낮아 차이가 없거나, 켠 쪽이 더 나쁘다 | 문구를 고치거나 삭제한다 |

## 실행

```sh
evals/run.py run --model '<정확한 모델 ID>' --effort <level> --runs 3 --jobs 4
evals/run.py summarize evals/results/<dir>
```

- 모델은 alias가 아닌 정확한 ID로 준다. judge 모델도 `--judge-model`로 고정되어 있다.
- 실행은 구독 로그인으로 돌고, 평소 작업과 같은 사용 한도를 나눠 쓴다.
- 결과는 `evals/results/`에 쌓이고 git은 이 디렉터리를 무시한다.
- 과제는 실행마다 임시 디렉터리에 새로 만든 git repo에서 돈다. `--work-root`로 위치를 바꾼다.

## 조건(arm)

| arm | 끄는 것 | 방법 |
|---|---|---|
| `on` | 없음 | |
| `off-memory` | `CLAUDE.md`와 `rules/` | `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` |
| `off-skills` | 모든 skill | `--disable-slash-commands` |
| `off-all` | 모든 customization | `--safe-mode` |

모든 arm에 공통으로 적용하는 것:
- `--model`과 `--effort` 고정
- `--no-session-persistence`: 실험 session이 transcript와 `/insights` 통계에 섞이지 않는다
- `--strict-mcp-config`: MCP server를 띄우지 않는다
- `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`
- Edit, Write, Skill과 case의 `allowed_tools`만 미리 허용한다. 읽기 도구는 원래 허락이 필요 없고, 그 밖의 Bash 명령은 거부된다

## case

`cases/<이름>/`에 다음을 둔다.

- `prompt.md`: 사용자 요청
- `fixture/`: 시작 상태. `main` branch의 첫 commit이 된다
- `branch/`: 있으면 새 branch를 만들고 이 파일들을 덮어쓴 commit을 하나 더 만든다
- `case.json`: arm 목록과 채점 기준

`case.json`의 채점 기준은 두 종류다.

- **`checks`**: 실행 기록만으로 채점한다. `no_changes`, `changed_only`, `untouched`, `skill_called`, `result_regex`가 있다.
- **`rubric`**: judge 모델이 예 또는 아니오로 채점한다. judge는 어느 arm의 출력인지 모른다.

과제나 채점 기준을 고친 뒤의 결과는 이전 모델의 결과와 직접 비교하지 않는다.

## 한계

- `-p`는 한 turn으로 끝난다. "질문하고 멈췄는가"까지만 볼 수 있고, 그 질문이 최종 결과를 낫게 했는지는 보지 못한다.
- 한국어 rule만 따로 끄는 arm은 없다. 별도 `CLAUDE_CONFIG_DIR`이 필요한데, 그 디렉터리는 Keychain 항목이 달라 로그인을 새로 해야 한다.
- skill은 다른 skill과 plugin이 모두 켜진 실제 환경에서 잰다. `claude plugin eval`은 manifest가 있는 plugin만 대상으로 하고 개인 설정을 불러오지 않아서 이 목적에 맞지 않는다.
- judge도 모델이라 틀릴 수 있다. 판정 전에 기록 일부를 직접 읽는다.
