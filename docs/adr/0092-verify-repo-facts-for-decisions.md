# 0092 — 결정 근거로 드는 repo 사실도 원본을 읽고 확인한다

`user/shared/CLAUDE.md`의 "Verify, don't recall" 규칙이 다루는 범위를 넓혔다. 이전에는 library, API, tool의 사실만 다뤘다. 이제 사용자에게 결정을 넘길 때 근거로 드는 repo의 사실도 다룬다. 그런 사실은 요약이나 한 가지 형태만 찾는 검색으로 확인하지 않고, 파일이나 기록 자체를 읽어 확인한다.

## Context

2026-10-15에 infra/data 세션(data-35)이 retro에서 이 후보를 찾아 이 세션으로 넘겼다. personal-db의 설계 가이드 skill을 grilling으로 정하던 중, Claude가 결정의 근거로 든 repo 사실을 원본을 읽지 않고 전한 일이 두 번 있었다.

- view가 `band`를 어떻게 쓰는지 판단할 때 `band = '...'`만 찾는 grep을 근거로 삼았다. 그래서 `band IN (...)`으로 목록 전체를 나누는 column을 놓쳤다.
- 이전 리뷰에서 사용자가 `rename_skill`을 어떻게 고쳤는지를, operation을 읽지 않고 proposal의 `reason` 요약을 보고 전했다. 그 결과 고치기 전의 동작을 전했다.

사용자는 두 근거를 믿고 동의했고, 잘못된 문구가 skill과 결정 문서에 들어갔다. 이 문제는 blind back-test가 두 번 실패한 뒤에야 드러났다. back-test 한 번에 subagent token이 약 14만 개 들었다.

## 결정

"Verify, don't recall" 항목에 다음 문장을 추가한다.

> The same holds for repo facts you cite as evidence for a decision you hand the user: read the file or record itself, not a summary of it or a search that matches only one form of it.

넘겨받은 원래 문구에서 두 곳을 고쳤다.

- 원래 문구의 `artifact`는 Claude Code의 Artifact tool과 이름이 겹친다. 그래서 "the file or record"로 바꿨다.
- "a narrow grep"은 무엇이 좁다는 건지 흐렸다. 실제로 놓친 원인은 검색 pattern이 쓰임새 한 가지만 잡았다는 데 있었다. 그래서 그 원인을 그대로 적었다.

이 문장을 "Say which source you used" 앞에 두었다. 그러면 출처를 밝히라는 요구가 repo의 사실에도 적용된다.

## Consequences

- 적용 범위를 "사용자에게 넘기는 결정의 근거"로 한정했다. 모든 사실 확인에 원본 읽기를 요구하지 않으므로 탐색 비용은 그대로다.
- `evals/cases`에 이 규칙을 재는 case가 없다. 따라서 이 문장이 행동을 바꾸는지는 아직 측정하지 않았다. case를 추가하는 일은 후속 작업으로 남긴다.
- infra/data는 자체 대책도 따로 둔다. back-test의 정답 목록에 확인한 근거(파일과 statement)를 적어 두는 문서다.
