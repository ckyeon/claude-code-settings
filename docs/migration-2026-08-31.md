# 2026-08-31 노트북 초기화 — 마이그레이션 기록과 복원 runbook

이전 맥북을 초기화하기 전에 개인 프로젝트(gigr 제외)의 상태를 정리한 기록과, 새 맥북에서 복원하는 절차. 이 repo가 새 머신에서 가장 먼저 clone하는 부트스트랩 지점이므로 여기에 둔다. 결정 기록은 [ADR 0024](adr/0024-notebook-migration-runbook.md).

## 1. 초기화 전에 끝낸 정리

| repo | remote | 정리 내용 |
|---|---|---|
| claude-code-settings | github.com/ckyeon/claude-code-settings | ADR 0023 + `user/shared/mcp/linear/` 커밋. **settings.json 미커밋 수정분은 폐기** (§5) |
| llm-wiki | github.com/ckyeon/llm-wiki | `raw/humanities/` 장자강좌 5~10강 원문 10개를 `wiki/batch-zhuangzi-2-4-2026-08-26` 브랜치에 커밋·푸시 (`31420b9`). 아직 ingest 전 소스 |
| toego | github.com/ckyeon/toego | main(`330002e`) 푸시 + 로컬 전용 브랜치 2개 푸시: `prototype/p4-p5-measure`, `prototype/recalibrate-2026-08-24` |
| mattpocock-skills | github.com/ckyeon/mattpocock-skills | 미커밋 없음. 설치 산출물 `.agents/`·`skills-lock.json`은 삭제 — 필요하면 `setup-matt-pocock-skills` 스킬로 재생성 |
| agent | github.com/ckyeon/agent | clean, 전 브랜치 푸시됨. 정리 불필요 |

## 2. 백업 아카이브 — 초기화 **직전에** 실행

repo에 안 담기는 Claude Code 로컬 상태를 묶는다. gigr 세션은 제외.

```bash
cd /Users/ckyeon && tar czf ~/claude-backup-$(date +%F).tgz \
  --exclude='.claude/projects/-Users-ckyeon-workspace-gigr*' \
  .claude/projects .claude/history.jsonl .claude/plans .claude/file-history .claude.json
```

담기는 것과 이유:

- `.claude/projects/` — 프로젝트별 세션 대화 기록(`claude --resume` 대상). 메모리 디렉터리도 이 안에 있다(2026-08-31 시점 비어 있음).
- `.claude/history.jsonl` — 프롬프트 입력 히스토리.
- `.claude/plans/` — plan mode 저장분.
- `.claude/file-history/` — 세션 rewind용 파일 편집 히스토리 (선택 — 빼도 세션 열람에는 지장 없음).
- `.claude.json` — MCP 등록, 프로젝트별 신뢰/허용 상태. **gigr 항목과 machine-local secret이 섞여 있을 수 있으니 새 맥이 개인용이면 통째로 복원하지 말고 참고용으로만 보관** — MCP는 §4-5로 재등록하면 된다.

만든 아카이브는 외장 디스크나 클라우드에 복사한다. gigr 관련 백업은 이 runbook의 범위 밖.

## 3. 파일로만 옮기는 디렉터리 (git repo 없음, 총 ~4.9G)

| 디렉터리 | 용량 | 내용 | 처리 |
|---|---|---|---|
| `workspace/cs231n_2017` | 3.9G | `kor/`, `videos/` 강의 영상 | 재다운로드 가능하면 생략 가능 |
| `workspace/hackers` | 840M | `listening-player/`, `mp3/` | 복사 |
| `workspace/learn` | 151M | `claude-agent-lab` (git repo 아님) | 복사 |
| `workspace/datagrip-projects` | 3.4M | `labbylab`, `playad`, `yajasu` SQL | `playad`는 회사 관련 여부 확인 후 분리 |

중첩된 git repo가 없는 것은 확인함 (2026-08-31).

## 4. 새 맥 복원 절차

1. Claude Code 설치 후 로그인. 인증 토큰은 macOS Keychain에 있었으므로 이전되지 않는다 — 재로그인이 정상이다.
2. 이 repo를 clone:
   ```bash
   mkdir -p ~/workspace && git clone https://github.com/ckyeon/claude-code-settings ~/workspace/claude-code-settings
   ```
3. `./install.sh` 실행 — `~/.claude/`의 CLAUDE.md·settings.json·agents·commands·skills·rules·output-styles·hooks·statusline 2종을 이 repo로 향하는 symlink로 구성한다. 실행 전 기존 `~/.claude/` 내용을 백업하니 안내를 읽고 진행.
4. 백업 아카이브 복원:
   ```bash
   cd ~ && tar xzf claude-backup-<날짜>.tgz
   ```
   세션 resume은 **username(`ckyeon`)과 프로젝트 경로(`/Users/ckyeon/workspace/...`)가 이전과 같아야** 작동한다 — `~/.claude/projects/`의 디렉터리 이름이 절대 경로에서 나오기 때문.
5. `install.sh`가 출력하는 리마인더대로 plugin과 MCP를 재등록:
   - `/plugin marketplace add ...` → `/plugin install ...`
   - `claude mcp add ...` — 정확한 명령은 `user/shared/mcp/*/README.md`에 있다.
   - linear는 등록 후 세션에서 `/mcp` → `linear` → Authenticate로 OAuth 인증 한 번 필요.
6. 나머지 repo clone: `agent`, `llm-wiki`, `toego`, `mattpocock-skills` (§1의 remote).
7. §3 디렉터리를 외장/클라우드에서 복사.

## 5. 옮기지 않기로 한 것

- **`user/shared/settings.json` 미커밋 수정분 — 의도적으로 폐기** (2026-08-31 사용자 결정). 개인 선호와 회사(GiverGround) 관련 autoMode 설정이 섞여 있었다. 새 맥에서 필요하면 `/config`로 재설정할 항목: `model: claude-fable-5[1m]`, `language: Korean`, `effortLevel: xhigh`, `voice: {enabled, mode: hold}`, `agentPushNotifEnabled: true`. autoMode environment 블록(GiverGround/phaser-template 전용)은 개인 맥에는 불필요.
- `~/.claude/plugins/` (477M), `cache/`, `jobs/`, `shell-snapshots/`, `paste-cache/`, `daemon*`, `telemetry/` — 재설치·재생성되는 상태라 백업하지 않는다.
- Keychain의 로그인 토큰 — 재로그인으로 대체.
- `~/.claude/projects/-Users-ckyeon-workspace-toy-project-*` — 디스크에 더 이상 없는 옛 프로젝트의 세션. 아카이브에는 포함되지만 resume 대상 코드가 없으므로 열람용이다.
