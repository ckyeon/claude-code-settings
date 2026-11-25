# 0145 — 2026-11-25 check-updates의 55건을 re-pin하고 skill 3개를 들이며 auto-editor-transcribe는 31.10.0까지 보류

check-updates에서 outdated로 나온 10개 source의 항목 56건 가운데 55건을 옮겼다. ADR 0124가 31.8.1을 기다리며 보류한 auto-editor 세 항목은 upstream이 31.8.1 없이 31.9.0을 내서 head로 옮겼고, 그 세 항목이 가리키는 `auto-editor-transitions`를 함께 들였다. agent-browser의 새 skill `vercel`과 `modern-web-guidance`도 Next.js template에 들였다. `auto-editor-transcribe`는 head가 31.10.0 기능을 안내하고 이 기기에 설치된 버전은 31.9.0이라 옛 pin에 남겼다.

## 바뀐 내용 (`copied` 10건)

- **auto-editor 3건** (`980a2e6c`, 31.9.0과 같은 내용)
  - `auto-editor-effects`: audio action `highpass`, `lowpass`, `dehum`과 이를 쓰는 recipe가 들어갔다.
  - `auto-editor-export`: `--export edl`(CMX 3600)이 생겼고 import가 FCPXML과 EDL까지 늘었다. FCP7 import의 experimental 표기가 빠졌다.
  - `auto-editor`: `auto-editor-transitions`로 보내는 줄만 더했다.
  - 세 항목 모두 `**auto-editor-transitions** skill`처럼 굵은 글씨로 새 skill을 가리킨다. effects sidecar의 "waits for 31.8.1" 메모는 옛 entry에 기록으로 남고, 새 entry notes가 31.9.0 기준으로 다시 적는다.
- **agent-browser `core`** (v0.44.0)
  - v0.44.0 CLI가 옛 이름 `protected-vercel-deployments` alias를 지웠다. 옛 `core`는 `agent-browser skills get protected-vercel-deployments`를 안내했으므로, 최신 CLI를 쓰는 기기에서는 이 명령이 "Skill not found"를 냈다. 새 `core`의 skill 표는 그 이름을 `vercel`로 바꾸고 `modern-web-guidance` 행을 더했다.
  - 새 명령과 flag는 `tab keep`, `click`과 `dblclick`의 `--button`과 `--modifiers`, `-p ladybird`다. `webmcp invoke`는 JSON을 positional 인자로 받는다.
  - 동작도 바뀌었다. unknown flag를 거부하고, 빈 `--allowed-domains`는 filter를 푸는 대신 error를 내고, 다른 document로 navigation한 뒤의 ref는 error를 낸다. login wall과 deployment protection은 header나 cookie로만 넘으라는 지시가 생겼다.
- **`web-design-guidelines`** (1.1.0): 전에는 실행할 때마다 `web-interface-guidelines`의 `command.md`를 WebFetch로 받았다. 이제는 같은 파일을 `references/command.md`로 담고 network에서 받지 말라고 적는다. 담긴 파일은 지금 upstream HEAD와 같다. 새 "Updating the Guidelines" 절은 upstream의 zip 재생성 절차라서 이 repo에서는 쓸 곳이 없다.
- **next.js template skill 5건** (`bd020231`)
  - `next-cache-components-adoption`: browser 확인 단계가 바뀌었다. 전에는 route마다 shell과 fallback을 capture해 streaming demo를 만들었다. 이제는 cookie `next-instant-navigation-testing=1`로 dev server의 navigation을 멈춰 확인한다.
  - `next-cache-components-optimizer`: "`next dev`에서 측정하지 말라"는 문구가 RED와 GREEN 판정은 production build에서 하고 편집 중 빠른 확인은 dev에서 하라는 문구로 바뀌었다. production 측정 요구는 그대로다.
  - `next-dev-loop`: link가 prefetch한 내용을 dev에서 보려면 navigation을 멈추라는 안내가 붙었고, 멈춘 navigation은 `networkidle`로 기다리지 않는다는 구분이 생겼다.
  - 두 prefetching skill은 문서 링크 대상만 바뀌었다.

`/name` 참조와 Skill tool 호출 문구는 새로 생기거나 사라진 것이 없다.

## pin만 옮긴 항목 (45건)

- `inspired-by` 5건. 등록 명령과 설치 명령은 모두 그대로다.
  - `remotion` 4.0.547: skill이 14개가 됐다. 새 `remotion-elements`는 외부 Element library의 component 소스를 프로젝트에 설치한다. `remotion-best-practices`에서 "명시적으로 요청할 때만 render한다"는 문장이 빠졌고, `remotion-render`는 회사 사용자에게 `--license-key`를 넘기라고 한다. README의 skill 개수와 docs URL(`docs/ai/`가 `docs/agents/`로 옮겨짐), video template `CLAUDE.md`의 license 링크를 upstream에 맞춰 고쳤다.
  - `fetch` 2026.11.18: GHSA-3rxj-6jhw-qfv7과 GHSA-f9hh-cmx9-2f23을 고쳤고 DNS rebinding을 막는다. 5 MiB를 넘는 응답과 `br` 또는 `zstd` 응답은 이제 error다. 이 기기의 uv cache는 이미 이 버전이다. 그보다 먼저 시작한 session의 fetch process는 재시작해야 수정이 적용된다.
  - `context7` 4.8.0: `query-docs`가 optional `version` 입력을 받는다. libraryId 뒤에 버전을 붙이는 옛 형식도 계속 받는다.
  - `github`: 새 tool은 모두 기본으로 꺼진 toolset이나 feature flag 뒤에 있다. 새 `skills` feature는 Insiders Mode에서 자동으로 켜지고, 켜지면 server instructions가 MCP skills 형태로 바뀐다. README는 Insiders가 아닌 URL을 쓰므로 지금은 영향이 없다.
  - `sequential-thinking` 2.2.0: HTTP transport option이 생겼고 기본은 stdio 그대로다.
- 내용 변경이 없는 40건: mattpocock/skills 27건, claude-plugins-official plugin 7건, vercel-labs/agent-skills 5건, agent-browser `dogfood`이다.

## `to-tickets`

ADR 0100의 local 수정(step 4b) 때문에 `bin/re-pin`이 이 항목에서 멈췄다. upstream 내용은 이번 구간에서 바뀌지 않았다. `docs/PROVENANCE.md` Edge cases의 절차대로 `--overwrite-local`과 `--notes`로 옮긴 다음 덮어쓰기 전 파일을 되돌렸다. SKILL.md는 이 commit 전과 같다.

## 새 항목

- **`auto-editor-transitions`** (들임): `--transition KIND:DURATION[:MIN-CUT]`으로 컷마다 전환 효과를 넣는다. 31.9.0에 들어 있다. 위 auto-editor 세 항목이 가리키므로 함께 들였다. `bin/check-integrity`는 굵은 글씨 참조를 검사하지 않아서, 빠뜨렸다면 경고 없이 참조가 끊겼을 것이다.
- **agent-browser `vercel`과 `modern-web-guidance`** (들임): `vercel`은 OIDC header로 Vercel Deployment Protection을 통과하고 cookie로 feature flag variant를 바꿔 본다. 지워진 `protected-vercel-deployments`의 새 이름이다. `modern-web-guidance`는 Chrome의 Modern Web Guidance로 UI를 고친 뒤 브라우저에서 CLS, reduced motion, dialog focus를 확인한다. `core`가 `agent-browser skills get <name>`으로 불러오도록 안내하므로 로컬 사본 없이도 동작하지만, 로컬에 두면 description을 보고 자동으로 trigger된다. `core`, `dogfood`와 같이 `track: release`를 sidecar에 직접 넣었다. `modern-web-guidance`의 `allowed-tools`는 버전을 고정하지 않은 `npx modern-web-guidance@latest`를 허용한다.
- 들이지 않은 것
  - `claude-for-manufacturing` (claude-plugins-official): 제조업 전용 plugin이고 README가 "Not actively maintained"라고 적는다.
  - `theme-examples` (claude-plugins-official): desktop app에 backdrop을 그리는 예제 mod다. 작업 흐름에 더하는 기능이 없다.
  - next.js `.agents/skills/`의 `rebase-pr`, `run-tests`, `rust-turbopack`: frontmatter에 `internal: true`가 있는 Next.js contributor용 skill이다.
- agent-browser의 `protected-vercel-deployments`는 `vercel`로 rename됐다. 로컬에 들인 적이 없다.

## 보류

`auto-editor-transcribe`의 head는 `-l`이 `en-US`나 `english` 같은 형태를 받는다고 안내한다. 31.10.0 기능이라 설치된 31.9.0에서는 실패할 수 있다. auto-editor를 31.10.0 이상으로 올릴 때 옮긴다. 그때까지 `check-updates`는 이 항목을 changed로 보고한다.

## 후속

- `project-templates/video/CLAUDE.md`의 `--cut` 제약 설명은 31.6.0 기준이다. 31.10.0 changelog에 "Let range options take several ranges"가 있으므로, `auto-editor-transcribe`를 옮길 때 함께 확인한다.
- `project-templates/nextjs/CLAUDE.md`는 skill이 9개라고 적지만 이번 변경 전에도 13개였고 이제 15개다.
- `bin/check-integrity`가 굵은 글씨로 쓴 skill 참조를 검사하지 않는 문제는 ADR 0124 후속 그대로 남아 있다. ADR 0147에서 해결했다.
