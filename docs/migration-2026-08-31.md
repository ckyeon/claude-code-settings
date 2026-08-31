# 2026-08-31 회사 맥북 반납 — 개인 데이터 반출 기록과 복원 runbook

퇴사로 회사 맥북을 초기화·반납한다. 목표는 두 방향 모두다: **이어갈 개인 작업은 빠짐없이 가져가고, 회사(gigr) 데이터는 가져가지 않는다.** 그중 최우선은 진행 중인 개인 프로젝트(llm-wiki·toego·agent·claude-code-settings)의 **작업 연속성**이고, 연속성의 주 수단은 각 repo 안의 문서다(§5 재개 지점) — 세션 아카이브는 보조 기록이다. 이 repo가 새 머신에서 가장 먼저 clone하는 부트스트랩 지점이므로 runbook을 여기에 둔다. 결정 기록은 [ADR 0024](adr/0024-notebook-migration-runbook.md), [ADR 0025](adr/0025-offboarding-revision.md), [ADR 0026](adr/0026-continuity-first.md).

분리 기준: 회사 **작업물**(gigr 프로젝트의 세션·파일 편집 이력·프롬프트·plan)은 제외한다. 개인 세션 안에 gigr라는 이름이 지나가듯 등장하는 것(예: 이 마이그레이션 세션의 디렉터리 목록)까지는 걷어내지 않는다 — 작업물과 언급을 구분한다.

## 1. 반납 전에 끝낸 정리

| repo | remote | 정리 내용 |
|---|---|---|
| claude-code-settings | github.com/ckyeon/claude-code-settings | ADR 0023 + `user/shared/mcp/linear/` 커밋. **settings.json 미커밋 수정분은 폐기** (§6) |
| llm-wiki | github.com/ckyeon/llm-wiki | `raw/humanities/` 장자강좌 5~10강 원문 10개를 `wiki/batch-zhuangzi-2-4-2026-08-26` 브랜치에 커밋·푸시 (`31420b9`). 아직 ingest 전 소스 |
| toego | github.com/ckyeon/toego | main(`330002e`) 푸시 + 로컬 전용 브랜치 2개 푸시: `prototype/p4-p5-measure`, `prototype/recalibrate-2026-08-24` |
| mattpocock-skills | github.com/ckyeon/mattpocock-skills | 미커밋 없음. 설치 산출물 `.agents/`·`skills-lock.json`은 삭제 — 필요하면 `setup-matt-pocock-skills` 스킬로 재생성 |
| agent | github.com/ckyeon/agent | clean, 전 브랜치 푸시됨. 정리 불필요 |

## 2. 백업 아카이브 — 반납 **직전에** 실행

repo에 안 담기는 Claude Code 로컬 상태 중 **개인 것만** 골라 묶는다. 한 줄 tar로는 안 되고(gigr가 `history.jsonl` 줄 단위, `plans/` 파일 단위로 섞여 있다) staging을 거친다:

```bash
STAGE=$(mktemp -d) && mkdir -p "$STAGE/.claude"

# 세션 기록 — gigr 프로젝트 디렉터리 제외
rsync -a --exclude='-Users-ckyeon-workspace-gigr*' ~/.claude/projects "$STAGE/.claude/"

# 프롬프트 히스토리 — gigr 세션 줄 제거 (2026-08-31 기준 4,394줄 중 3,542줄이 gigr)
grep -v 'workspace/gigr' ~/.claude/history.jsonl > "$STAGE/.claude/history.jsonl"

# plan — gigr/GiverGround 언급 파일 제거
cp -R ~/.claude/plans "$STAGE/.claude/plans"
grep -El 'gigr|GiverGround' "$STAGE/.claude/plans"/* 2>/dev/null | tr '\n' '\0' | xargs -0 rm -f

tar czf ~/claude-backup-$(date +%F).tgz -C "$STAGE" .claude && rm -rf "$STAGE"

# 검증: 아카이브 안에 gigr 경로가 없어야 한다
tar tzf ~/claude-backup-$(date +%F).tgz | grep -i gigr && echo "FAIL: gigr leaked" || echo "OK"
```

이 절차는 2026-08-31에 리허설로 검증했고, 같은 날 본 실행으로 `~/claude-backup-2026-08-31.tgz`(64M)를 만들었다. 아카이브는 **개인 클라우드에 평문으로** 올린다 — 암호화는 생략하기로 결정 (2026-08-31, ADR 0028). 근거: 흔한 토큰 형식(Anthropic·GitHub·AWS 키, private key, Slack 토큰) 스캔에서 본인 자격증명 0건 — 유일한 매치는 subagent가 읽어온 외부 README에 제3자가 흘린 GitHub PAT였다. 외장 디스크 사본까지 두면 더 좋다.

## 3. git repo 없는 디렉터리 — 반출하지 않기로 결정 (2026-08-31)

`cs231n_2017`(3.9G, 강의 영상)·`hackers`(840M)·`learn`(151M)·`datagrip-projects`(3.4M)는 **가져가지 않는다** — 진행 중인 작업이 아니라 자료 보관이고, 필요해지면 재다운로드·재구성이 가능한 수준이라 판단했다. 이 결정으로 `datagrip-projects` 내부의 개인/회사 분류 문제(`playad`는 회사 DB)도 함께 소멸한다. Desktop·Documents·사진·브라우저 데이터 등 workspace 밖 개인 파일은 이 runbook 범위 밖이다 — 따로 챙길 것.

## 4. 새 맥 복원 절차

1. 새 맥의 username은 `ckyeon`으로 만든다 (4단계 세션 resume의 전제). Claude Code 설치 후 **개인 계정으로** 로그인 — 회사 계정(kyle@gigr.ai)은 퇴사로 소멸하며, 거기 묶인 claude.ai 대화 이력·커넥터·구독은 반출 불가로 간주한다.
2. 이 repo를 clone:
   ```bash
   mkdir -p ~/workspace && git clone https://github.com/ckyeon/claude-code-settings ~/workspace/claude-code-settings
   ```
3. `./install.sh` 실행 — `~/.claude/`의 CLAUDE.md·settings.json·agents·commands·skills·rules·output-styles·hooks·statusline 2종을 이 repo로 향하는 symlink로 구성한다. 실행 전 기존 `~/.claude/` 내용을 백업하니 안내를 읽고 진행.
4. 백업 아카이브 복원 — 아카이브에는 `.claude/projects`·`history.jsonl`·`plans`만 들어 있으므로 그대로 풀면 된다:
   ```bash
   cd ~ && tar xzf claude-backup-<날짜>.tgz
   ```
   세션 resume은 **username(`ckyeon`)과 프로젝트 경로(`/Users/ckyeon/workspace/...`)가 이전과 같아야** 작동한다 — `~/.claude/projects/`의 디렉터리 이름이 절대 경로에서 나오기 때문.
5. `install.sh`가 출력하는 리마인더대로 plugin과 MCP를 재등록:
   - `/plugin marketplace add ...` → `/plugin install ...`
   - `claude mcp add ...` — 정확한 명령은 `user/shared/mcp/*/README.md`에 있다.
6. 나머지 repo clone: `agent`, `llm-wiki`, `toego`, `mattpocock-skills` (§1의 remote).

git identity, `gh auth login`, SSH 키, MCP OAuth(linear 등) 같은 인증·키 재설정은 필요해질 때 그때그때 직접 한다 — runbook이 관리하지 않는다.

## 5. 프로젝트별 재개 지점 (2026-08-31 기준)

연속성의 원본. 세션을 열어보지 않아도 여기서 바로 이어갈 수 있다.

- **llm-wiki** — ① 열린 auto PR #51(자동 유지보수 2026-08-30) 리뷰·머지 대기. ② 다음 작업: 배치 2차(5·6·7강) 인제스트 — `wiki/humanities/humanities-index.md`의 "미인제스트 raw 백로그"가 원본. ③ 승격 대기 3건도 같은 index에. **매일 09:00 KST 자동 유지보수 routine은 개인 claude.ai 계정에 있어 퇴사와 무관하게 계속 돈다.** 재생성이 필요해지면: 절차 원본은 repo의 `auto-maintain` 스킬이므로, 스킬을 가리키는 얇은 프롬프트로 routine만 다시 만들면 된다.
- **toego** — P5 낱말 심사 대기 132건(고유 82형). `PROJECT.md` 5.5절("심사 전")이 원본, 심사 시트는 `.toego/sheets/p5-words-2026-08-26.html`. 두 prototype 브랜치는 근거 보존용이라 머지 대상이 아니다.
- **agent** — 커리큘럼 리뷰 2차까지 머지 완료(PR #6, 2026-08-18). 코드는 M1 미착수 — `CURRICULUM.md`의 마일스톤 완료 기준에서 재개.
- **claude-code-settings** — 진행형. 이 runbook과 ADR들이 마지막 작업.

## 6. 가져가지 않는 것

**회사 데이터라서 (의도적으로 두고 간다):**

- `~/.claude/projects/-Users-ckyeon-workspace-gigr*` — gigr 세션 전부.
- `~/.claude/file-history/` — 세션 UUID 단위라 gigr 파일 편집 내용이 분리 불가로 섞여 있다. 개인 세션 rewind를 포기하고 통째로 제외.
- `~/.claude.json` — gigr 프로젝트 항목과 머신 로컬 상태 혼재. MCP는 §4-5로 재등록하고, 프로젝트 신뢰는 새 맥에서 처음 열 때 다시 수락하면 된다.
- `~/.claude/history.jsonl`의 gigr 줄(81%), `~/.claude/plans/`의 gigr 관련 plan 1개 — §2 스크립트가 걸러낸다.
- `~/.ssh`의 GCE 키, JetBrains 설정의 회사 DB 데이터소스.
- gigr 저장소 인수인계는 **완료** (2026-08-31 확인).

**개인 설정이지만 폐기하기로 한 것:**

- **`user/shared/settings.json` 미커밋 수정분** (2026-08-31 사용자 결정). 개인 선호와 회사(GiverGround) autoMode 설정이 섞여 있었다. 새 맥에서 필요하면 `/config`로 재설정할 항목: `model: claude-fable-5[1m]`, `language: Korean`, `effortLevel: xhigh`, `voice: {enabled, mode: hold}`, `agentPushNotifEnabled: true`.
- `~/.claude/plugins/` (477M), `cache/`, `jobs/`, `shell-snapshots/`, `paste-cache/`, `daemon*`, `telemetry/` — 재설치·재생성되는 상태.
- Keychain의 로그인 토큰 — 재로그인으로 대체.
