# 0087 — 새 모델마다 user 설정의 효과를 재는 `evals/`를 둔다

user-scope 설정(`CLAUDE.md`, rules, skill)이 실제로 행동을 바꾸는지 잰 적이 없었다. `check-integrity`는 설정이 동작하는지, 곧 참조가 풀리는지만 보고 효과는 보지 않는다. 모델이 좋아지면 일부 지침은 할 일이 없어지고 context만 차지하므로, 새 모델이 나올 때마다 다시 재야 한다.

## 결정

- **구성요소마다 켠 조건과 끈 조건을 비교해 유지, 중복, 무효로 판정한다.** 유지는 켠 쪽이 의도한 지표에서 확실히 낫다는 뜻이다. 중복은 끈 쪽도 이미 잘해서 차이가 없다는 뜻이고, 무효는 둘 다 못하거나 켠 쪽이 더 나쁘다는 뜻이다. "확실히"의 숫자 기준은 아직 정하지 않았다.
- **같은 환경에서 한 부분만 끈다.** `off-memory`는 `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`, `off-skills`는 `--disable-slash-commands`, `off-all`은 `--safe-mode`를 쓴다. 모든 조건에서 모델과 effort를 고정하고, session 기록과 MCP server와 auto memory를 끈다. `--bare`는 system prompt까지 바꾸므로 쓰지 않는다.
- **skill도 직접 만든 runner로 잰다.** `claude plugin eval`은 켬과 끔의 점수 차를 내 주지만, manifest가 있는 plugin만 대상으로 하고 개인 설정을 불러오지 않는다. 알고 싶은 것은 다른 skill과 plugin이 함께 켜진 실제 환경에서 trigger가 되는지라서 맞지 않는다.
- **runner는 `evals/run.py` 하나이고 Python stdlib만 쓴다.** 채점은 실행 기록만으로 하는 `checks`와 judge 모델이 하는 `rubric` 두 종류다. judge는 `claude-haiku-5-5`로 고정하고 `--safe-mode`로 돌린다. 내 설정이 채점에 섞이지 않게 하기 위해서다. judge에게는 어느 조건의 출력인지 알리지 않는다.
- **구독 사용 한도를 쓰므로 hook이나 `tests/run.sh`에서 돌리지 않는다.** 새 모델이 나왔을 때 손으로 돌린다. 결과 원본은 `evals/results/`에 남기고 commit하지 않는다.

## pilot

2026-10-15에 `claude-opus-5-5[1m]`, effort xhigh로 조건마다 3회씩 돌렸다. off 열은 CLAUDE.md case에서 `off-memory`이고 `skill-pr`에서 `off-skills`다.

| case | 지표 | on | off |
|---|---|---|---|
| claude-md-ambiguous | 고치기 전에 묻거나 선택지를 낸다 | 3/3 | 0/3 |
| claude-md-scope | 옆 파일을 건드리지 않는다 | 3/3 | 3/3 |
| claude-md-scope | 옆의 버그를 follow-up으로 알린다 | 3/3 | 0/3 |
| claude-md-trivial | 묻지 않고 바로 고친다 | 3/3 | 3/3 |
| skill-pr | `pr` skill이 불린다 | 3/3 | 0/3 |
| skill-pr | template의 세 절을 따른다 | 3/3 | 0/3 |

- 과제가 case당 하나뿐이라 이 결과는 판정이 아니라 runner 검증이다. 차이는 모두 3회 전부 아니면 0회로 갈렸다.
- trivial에서 CLAUDE.md를 켠 쪽은 고친 뒤 검증을 시도해서 turn이 평균 6 대 4였고, 실행당 비용이 $0.195 대 $0.141이었다. `pr` skill을 켠 쪽은 $0.276 대 $0.147이었다. 비용은 Claude Code가 낸 추정값이고, 24회 합계는 약 $4.9였다.

pilot에서 확인한 것:

- `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`은 `~/.claude/rules`도 함께 끈다. 문서에는 rules 언급이 없어서, 모델에게 context에 어떤 파일이 있는지 물어 확인했다. 그래서 한국어 rule만 끄는 조건은 아직 없다.
- `CLAUDE_CONFIG_DIR`을 새 디렉터리로 바꾸면 Keychain 항목이 달라져 로그인을 다시 해야 한다(authentication 문서).
- `--safe-mode`에서도 `settings.json`의 모델과 `language`는 유지된다.
- judge가 이번 실행의 수정분 diff를 branch 변경으로 잘못 읽은 판정이 1회 있었다. diff가 무엇인지 prompt에 밝혔다. 다시 채점해도 그 1회는 실패였는데, 이번에는 PR 본문이 테스트 추가를 명시하지 않았다는 정당한 이유였다.

## Consequences

- repo의 목적이 재현에서 효과 확인까지 넓어졌다. eval은 owned도 declared도 아닌 repo 도구라서 README § Scope의 분류는 그대로다.
- 남은 결정은 세 가지다. "확실히"의 숫자 기준, 과제 세트 확장(기존 transcript에서 후보 추출), 그리고 한국어 rule만 끄는 조건을 만들지 여부다. 마지막 것은 `claude setup-token`이 필요하다.
