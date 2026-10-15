# evals

새 모델이 나올 때마다 user-scope 설정이 그 모델에서도 효과가 있는지 확인하는 eval이다. 같은 과제를 설정을 켠 조건과 일부를 끈 조건에서 반복 실행하고, 구성요소마다 아래 셋 중 하나로 판정한다(ADR 0087).

| 판정 | 조건 | 할 일 |
|---|---|---|
| **유지** | 켠 조건이 의도한 지표에서 끈 조건보다 확실히 낫다 | 그대로 둔다 |
| **중복** | 끈 조건도 이미 점수가 높아 차이가 없다 | 삭제 후보. context 비용만 남는다 |
| **무효** | 두 조건 모두 낮아 차이가 없거나, 켠 쪽이 더 나쁘다 | 문구를 고치거나 삭제한다 |

`summarize`가 지표마다 켠 조건과 끈 조건의 통과율로 판정을 계산한다(ADR 0088). 숫자는 조건마다 5회 실행을 기준으로 정했다.

- 유지: 켠 쪽 통과율이 끈 쪽보다 0.6 이상 높다
- 중복: 두 쪽 모두 0.8 이상이다
- 무효: 두 쪽 모두 0.2 이하이거나, 끈 쪽이 0.6 이상 높다
- 어디에도 해당하지 않으면 보류다. 반복 횟수를 늘려 다시 잰다

`case.json`의 `guard`에 적은 지표는 설정이 해를 끼치지 않는지 보는 지표다. 켠 쪽이 0.8 이상이면 해 없음, 끈 쪽이 0.6 이상 높으면 해로움, 그 밖은 보류다.

조건이 하나뿐인 case는 비교할 대상이 없어서 통과율 자체로 판정한다(ADR 0090). 0.8 이상이면 통과, 0.2 이하면 실패, 그 사이는 보류다. skill trigger case가 여기에 해당한다. skill을 끈 조건에서는 skill이 아예 불릴 수 없으므로 비교해도 얻는 것이 없다.

## 실행

```sh
evals/run.py run --model '<정확한 모델 ID>' --effort <level> --jobs 4
evals/run.py summarize evals/results/<dir>
```

- 모델은 alias가 아닌 정확한 ID로 준다. judge 모델도 `--judge-model`로 고정되어 있다.
- 실행은 구독 로그인으로 돌고, 평소 작업과 같은 사용 한도를 나눠 쓴다.
- 결과는 `evals/results/`에 쌓이고 git은 이 디렉터리를 무시한다.
- 과제는 실행마다 임시 디렉터리에 새로 만든 git repo에서 돈다. `--work-root`로 위치를 바꾼다.
- 판정을 확인한 요약은 `history/<날짜>-<모델>-<effort>.md`에 남기고 commit한다. `results/`의 기록 전체는 commit하지 않는다.

## 조건(arm)

| arm | 끄는 것 | 방법 |
|---|---|---|
| `on` | 없음 | |
| `off-memory` | `CLAUDE.md`와 `rules/` | `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` |
| `off-skills` | 모든 skill | `--disable-slash-commands` |
| `off-all` | 모든 customization | `--safe-mode` |
| `on-mirror` | 없음. `off-rules`와 비교하는 기준 | mirror 디렉터리와 token |
| `off-rules` | `rules/` | `rules`를 뺀 mirror 디렉터리와 token |

mirror 디렉터리는 `~/.claude`에서 이 repo가 소유한 항목과 `plugins/`만 symlink해 만든 config 디렉터리이고, `CLAUDE_CONFIG_DIR`로 넘긴다. config 디렉터리가 다르면 Keychain 항목도 달라 로그인이 풀리므로, 이 두 arm은 `claude setup-token`으로 만든 token으로 로그인한다(`docs/SECRETS.md`). 인증 방식이 `on`과 다르므로 mirror arm끼리만 비교한다.

모든 arm에 공통으로 적용하는 것:
- `--model`과 `--effort` 고정
- `--no-session-persistence`: 실험 session이 transcript와 `/insights` 통계에 섞이지 않는다
- `--strict-mcp-config`: MCP server를 띄우지 않는다
- `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`
- Claude Code가 자기 session에 붙이는 환경 변수(`CLAUDECODE`, `CLAUDE_`로 시작하는 것 등)를 뺀다. Claude Code session 안에서 eval을 띄워도 terminal에서 띄운 것과 같은 환경에서 돈다
- Edit, Write, Skill과 case의 `allowed_tools`만 미리 허용한다. 읽기 도구는 원래 허락이 필요 없고, 그 밖의 Bash 명령은 거부된다

## case

`cases/<이름>/`에 다음을 둔다.

- `prompt.md`: 사용자 요청
- `fixture/`: 시작 상태. `main` branch의 첫 commit이 된다
- `branch/`: 있으면 새 branch를 만들고 이 파일들을 덮어쓴 commit을 하나 더 만든다
- `case.json`: arm 목록과 채점 기준

`case.json`의 채점 기준은 두 종류다.

- **`checks`**: 실행 기록만으로 채점한다. `no_changes`, `changed_only`, `untouched`, `skill_called`, `no_skill`, `result_regex`, `result_absent`가 있다.
  - `skill_called`는 skill 이름이 정확히 같아야 통과다. user skill `code-review`와 plugin skill `engineering:code-review`처럼 콜론 뒤가 같은 이름이 있기 때문이다.
  - `result_absent`는 최종 답변에서 code, 표, 제목, 라벨 구분자(`**용어** — 설명`)를 뺀 본문에 패턴이 없으면 통과다.
- **`rubric`**: judge 모델이 예 또는 아니오로 채점한다. judge는 어느 arm의 출력인지 모른다.

`guard`는 위 두 종류의 지표 이름 가운데 해를 끼치지 않는지 보는 것을 나열한다.

과제나 채점 기준을 고친 뒤의 결과는 이전 모델의 결과와 직접 비교하지 않는다.

## 한계

- `-p`는 한 turn으로 끝난다. "질문하고 멈췄는가"까지만 볼 수 있고, 그 질문이 최종 결과를 낫게 했는지는 보지 못한다.
- 같은 이유로 앞선 대화 맥락을 따르는지도 잴 수 없다. 사고 이야기를 하던 session에서 "리뷰해."를 branch 리뷰로 읽은 중단 기록은 case로 만들지 못했다(ADR 0092).
- mirror arm의 하위 process는 token을 환경 변수로 물려받는다. eval은 정해 둔 git 명령 말고는 Bash를 거부하므로 모델이 이 값을 읽을 길은 막혀 있다. `allowed_tools`에 Bash를 넓게 열면 이 전제가 깨진다.
- skill은 다른 skill과 plugin이 모두 켜진 실제 환경에서 잰다. `claude plugin eval`은 manifest가 있는 plugin만 대상으로 하고 개인 설정을 불러오지 않아서 이 목적에 맞지 않는다.
- judge도 모델이라 틀릴 수 있다. 판정 전에 기록 일부를 직접 읽는다.
- skill trigger case와 `no-skill-*` case는 `max_turns` 5에서 끊으므로 `is_error`로 끝나는 일이 많다. `summary.json`의 `errors`가 그만큼 나오는 것은 정상이다.
- Edit와 Write는 경로 제한 없이 허용한다. 모델이 repo 밖에 검증용 script를 쓰는 일이 있는데, 변경 집계는 repo 안만 보므로 지표에 잡히지 않는다.
