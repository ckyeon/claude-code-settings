# 0089 — 한국어 rule만 끄는 eval 조건을 mirror config 디렉터리와 장기 token으로 만든다

ADR 0087의 pilot에서 `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`이 `~/.claude/rules`까지 함께 끈다는 것을 확인했다. 그래서 `korean-technical-writing` rule의 효과만 따로 잴 조건이 없었다.

## 결정

- **mirror 디렉터리를 config 디렉터리로 쓴다.** `~/.claude`에서 `list_owned_links`가 연결하는 항목과 `plugins/`만 symlink하고, `.claude.json`에는 `{"hasCompletedOnboarding": true}`만 둔다. 이 디렉터리를 `CLAUDE_CONFIG_DIR`로 넘긴다. `off-rules`는 여기서 `rules`를 뺀다.
- **장기 token으로 로그인한다.** config 디렉터리가 다르면 Keychain 항목도 달라 로그인이 풀린다(authentication 문서). 그래서 `claude setup-token`으로 만든 token을 `CLAUDE_CODE_OAUTH_TOKEN`으로 넘긴다. token은 Keychain 항목 `claude-code-evals-oauth-token`에 두고, runner는 mirror 조건을 돌릴 때만 읽는다. `docs/SECRETS.md`에 행을 더했다.
- **mirror 조건끼리 비교한다.** `on-mirror`와 `off-rules`는 인증 경로와 config 디렉터리가 같아서 rules 말고는 차이가 없다. `on`과는 비교하지 않는다.
- **본문 기호 검사 `result_absent`를 둔다.** 최종 답변에서 code, 표, 제목을 뺀 본문에 패턴이 없으면 통과한다. 굵은 label 뒤의 대시는 rule이 허용하므로 잡지 않는다. 이중피동은 "되어진다", "보여집니다"처럼 활용한 꼴까지 잡도록 받침이 붙은 음절을 함께 적었다.
- **`korean-prose` case를 더한다.** 단계와 실패 처리를 설명하게 해서 화살표와 대시를 부르기 쉬운 과제다.
- **하위 `claude`의 stdin을 닫는다.** 닫지 않으면 실행마다 stdin을 3초 기다린다는 경고가 나왔다.

## 확인한 것

- 두 mirror 조건 모두 로그인된다. 모델에게 context에 있는 파일을 물으면 `on-mirror`는 CLAUDE.md와 rule을 모두 보고, `off-rules`는 CLAUDE.md만 본다고 답했다.
- haiku로 `korean-prose`를 조건마다 한 번 돌려 runner가 끝까지 돌았다. 결과 기록에 token은 없고, mirror 디렉터리는 실행 뒤 지워졌다.

## Consequences

- token은 하위 process의 환경 변수로 들어간다. eval은 정해 둔 git 명령 말고는 Bash를 거부하므로 모델이 이 값을 읽을 길은 막혀 있다. `allowed_tools`에 Bash를 넓게 열면 이 전제가 깨진다.
- mirror 조건도 claude.ai의 remote settings를 받는다. 두 mirror 조건에 똑같이 적용되므로 비교에는 영향이 없다.
- `MIRROR_ENTRIES`는 `list_owned_links`의 목록을 따로 적은 것이다. 소유 항목의 종류가 늘면 두 곳을 함께 고친다.
