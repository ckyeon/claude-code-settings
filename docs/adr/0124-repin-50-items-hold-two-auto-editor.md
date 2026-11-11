# 0124 — 2026-11-11 check-updates의 50건을 re-pin하고 auto-editor 두 항목은 31.8.1까지 보류

check-updates에서 outdated로 나온 12개 source의 항목 52건 가운데 50건을 옮겼다. `auto-editor`와 `auto-editor-export`는 upstream 최신 내용이 아직 release되지 않은 기능을 안내하므로 옛 pin에 남겼다. `auto-editor-effects`는 ADR 0108의 보류 이유가 31.8.0 release로 사라져서, 이 path를 바꾼 commit 가운데 release에 들어간 마지막 commit `692cbbe`로 옮겼다.

## 바뀐 내용 (`copied` 6건)

- **next.js template skill 4건** (`9464bf78`)
  - `next-cache-components-optimizer`, `next-partial-prefetching-adoption`, `next-partial-prefetching-optimizer`: test rig가 `EXPOSE_TESTING_API=1`을 build 때뿐 아니라 server를 띄울 때와 test 명령에도 설정한다. build 때만 설정하면 `instant()` test에서 첫 page load가 request-time 내용을 렌더링해서 결과가 틀린다.
  - 두 prefetching skill은 redirect되는 link도 test에서 production `href`를 그대로 쓰고 최종 pathname과 query를 확인하라고 안내한다. `next-partial-prefetching-optimizer`에서는 redirect link를 rig 문제로 보던 이전 안내가 빠졌다.
  - `next-dev-loop`에 팁 3개가 더해졌다. `agent-browser react tree --json`을 쓰고, production test port를 dev와 나누고, locator timeout 뒤에는 URL과 새 snapshot을 확인한 다음 재시도한다.
- **agent-browser `core`** (v0.42.0): SKILL.md가 짧아지고 MCP, React, Web Vitals, 접근성 감사 같은 세부 내용은 `references/commands.md`로 옮겨졌다. 환경 변수 `AGENT_BROWSER_SESSION`을 export하는 대신 명령마다 `--session`을 붙이라고 안내하고, screenshot보다 snapshot을 쓰라고 한다. `skills get core --ref <name>`과 실험 기능 `flow`가 들어갔다. template은 agent-browser 버전을 고정하지 않으므로 새로 설치하면 이 명령들이 있다. 오래된 전역 설치가 남은 기기에서는 `flow`와 `--ref`가 실패한다.
- **`auto-editor-effects`** (`692cbbe`, 31.8.0): keyframe에 시점을 붙이는 `value@time` 문법이 들어갔다. auto-editor 31.8.0 이상이 필요하다. 이 path를 바꾼 다음 commit `5883594`는 아직 들이지 않은 `auto-editor-transitions`를 가리키는 줄만 더하므로 옮기지 않았다.

`/name` 참조와 Skill tool 호출 문구는 새로 생기거나 사라진 것이 없다.

## pin만 옮긴 항목 (44건)

- `inspired-by` 9건: plugin `understand-anything`, `clangd-lsp`, `rust-analyzer-lsp`, `typescript-lsp`, `remotion`과 MCP server `github`, `fetch`, `sequential-thinking`, `context7`이다. 실제 동작은 marketplace와 `claude mcp add`가 정하므로 pin만 기록으로 옮겼다. 그중 기록해 둘 변경은 다음과 같다.
  - `remotion` 4.0.542에 13번째 skill `remotion-license`가 생겼고, `remotion-render`가 Remotion에 번들된 browser를 그대로 쓰라고 안내한다. README의 skill 개수를 13으로 고쳤다. video template은 browser를 따로 지정하지 않으므로 새 안내와 충돌하지 않는다.
  - `fetch`의 Readability.js 추출에 timeout이 생겼다. 전에는 tool 호출이 멈추거나, `npm install` 출력이 stdio JSON-RPC 통로인 stdout에 섞일 수 있었다. 등록 명령은 그대로다.
  - `sequential-thinking` README가 tool 이름을 `sequential_thinking`으로 적고 있었다. 실제 이름은 `sequentialthinking`이므로 고쳤다.
  - 세 LSP plugin은 upstream이 marketplace entry와 같은 `lspServers` 값을 담은 `plugin.json`을 더했을 뿐이다.
  - `understand-anything`은 Devin 지원을 더했고 SessionStart hook을 Node script로 옮겼다. 새 MCP package는 `.mcp.json`에 등록되지 않아서 Claude Code에서 켜지지 않는다.
  - `github`과 `context7`에는 기본으로 꺼진 실험 tool만 더해졌다. `context7`의 `resolve-library-id`와 `query-docs`는 이름과 인자가 그대로다.
- 내용 변경이 없는 35건: mattpocock/skills 27건, claude-plugins-official plugin 5건, `auto-editor-transcribe`, agent-browser `dogfood`, `next-cache-components-adoption`이다.

## `to-tickets`

ADR 0100이 넣은 local 수정(step 4b) 때문에 `bin/re-pin`이 이 항목에서 멈췄다. upstream 내용은 이번 구간에서 바뀌지 않았다. `docs/PROVENANCE.md` Edge cases의 절차대로 `--overwrite-local`과 `--notes`로 옮긴 다음, 덮어쓰기 전 파일에서 step 4b를 다시 넣었다. SKILL.md는 이 commit 전과 같다.

## 보류

- `auto-editor-export`의 head는 EDL export와 import, FCPXML import를 안내한다. 31.8.0에는 없는 기능이다.
- `auto-editor`의 head는 `auto-editor-transitions`로 보내는 줄만 더했다.
- 31.8.1이 tag되면 두 항목을 head로 옮기면서 `auto-editor-transitions`를 함께 들인다. auto-editor의 tag에는 `v` 접두사가 없어서 `track: release`를 쓸 수 없다(ADR 0108). 그래서 그때까지 `check-updates`는 이 두 항목과 `auto-editor-effects`를 계속 changed로 보고한다.

## 새 항목

- `auto-editor-transitions` (auto-editor): 컷마다 전환 효과를 넣는 `--transition KIND:DUR[:MIN-CUT]`을 다룬다. 31.8.0의 `--transition`은 `dissolve`만 받으므로 31.8.1 release 때 들인다.
- `champion-kit` (claude-plugins-official): 팀에서 Claude Code 도입을 맡은 사람을 위한 plugin이다. skill 7개가 hackathon, office hours, 성숙도 평가 같은 팀 단위 활동을 다룬다. 개인 설정 repo에는 쓸 곳이 없어서 들이지 않는다.
- `software-factory` (mattpocock/skills): ticket과 PR을 merge된 code로 바꾸는 agent pipeline을 설계할 때 쓰는 용어집이다. 들어 있는 `skills/in-progress/`를 upstream README가 Beta라고 부르므로 들이지 않는다. 안정된 디렉터리로 옮겨지면 다시 본다.

`champion-kit`과 `software-factory`는 이번 re-pin으로 pin보다 먼저 생긴 항목이 되어서 `check-updates`가 다시 알리지 않는다.

## 후속

- `project-templates/video/CLAUDE.md`가 auto-editor 31.6.0의 `--cut` 제약을 설명한다. 설치된 버전은 31.8.0이므로 그 제약이 아직 있는지 확인해야 한다.
- `bin/check-integrity`는 `**name** skill`처럼 굵은 글씨로 쓴 skill 참조를 검사하지 않는다. auto-editor 두 항목을 head로 옮기면서 `auto-editor-transitions`를 들이지 않으면 경고 없이 참조가 끊긴다.
