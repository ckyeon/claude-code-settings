# 0057 — `transcribe` skill이 파일 전사 API 옵션 5개를 모두 노출

`transcribe` skill은 `gemini-3.5-transcribe`의 옵션 다섯 개 중 verbatim mode와 word timestamp만 쓰고 있었다. 화자 구분(`--speakers`), smart mode(`--smart`), `language_codes`(`--lang`), `custom_vocabulary`(`--vocab`, `--vocab-file`)를 CLI 옵션으로 더해 파일 전사 API의 옵션을 전부 쓸 수 있게 했다. API 사실의 출처는 https://ai.google.dev/gemini-api/docs/transcribe 이다.

## 결정 (2026-09-21)

- **범위는 파일 전사 옵션 5개다.** 실시간 model(`gemini-3.5-transcribe-live`)은 넣지 않는다. WebSocket이 필요한데 Python stdlib에 client가 없어 "Python 3 stdlib + bash 3.2" guardrail과 충돌하고, ADR 0044가 입력을 로컬 파일로 한정했다.
- **API가 함께 받지 않는 조합은 요청 전에 오류로 끝낸다.** `--smart`와 `--vocab`은 각각 `--anchors`, `--speakers`와 함께 쓸 수 없다. 한쪽을 조용히 끄면 사용자가 결과가 요청과 다른 이유를 알 수 없다.
- **화자 출력은 발언 차례별 문단이다.** `**spk_0:** 본문` 형태이고 `--anchors`와 함께 쓰면 앞에 `[H:MM:SS]`가 붙는다. parser는 `chunk_segs`를 확장했고, 본문은 `content[].text`에서 취하고 annotation은 위치 지도로만 쓰는 ADR 0044의 원칙을 그대로 따른다.
- **`CHUNK_SEC`은 1500초 그대로 둔다.** smart나 vocabulary만 쓸 때는 API 상한이 1시간이지만 mode별 분기는 이번 범위가 아니다.

## 실측 (2026-09-21, macOS `say` 두 목소리 27초 클립)

- `diarization_mode`만 켜면 `word_info` annotation이 아예 오지 않는다. 그래서 `--speakers`는 word timestamp를 함께 켠다.
- label의 실제 형식은 `spk:0`이다. 문서의 `spk_1`과 다르고 0부터 시작한다. 출력에서는 쌍점만 밑줄로 바꾼다.
- label은 요청마다 등장 순서로 매겨진다. 같은 두 목소리의 순서를 뒤집은 클립에서 먼저 말한 쪽이 `spk:0`이 됐다. 25분 초과 파일은 청크마다 따로 요청하므로 label에 `c1-`, `c2-` 접두어를 붙여 번호 체계가 서로 다름을 드러낸다.
- word timestamp를 켜자 같은 클립의 "Kubernetes"가 "Cuba needs"로, "BigQuery"가 "Big Query"로 바뀌었다. 문서의 정확도 경고가 실제로 나타난 사례이고, SKILL.md의 옵션 선택 기준에 적었다.
- 회귀 확인: 응답에서 `speaker`를 지운 사본으로 수정 전후 `chunk_segs`와 `paras_from` 출력을 비교해 같음을 확인했다.

## Consequences

- 화자 구분과 용어 보정은 함께 쓸 수 없다. 고유명사가 많은 회의에서는 화자 구분을 켜면 고유명사 오청취가 늘고, 보정할 방법이 없다.
- 합성 음성은 실제 회의보다 구분하기 쉽다. 겹쳐 말하기, 비슷한 목소리, 3명 이상(API가 실험적 기능으로 분류)에서의 품질은 검증하지 않았다.
- 나중에: 청크 경계에서 잘린 발언이 새 청크의 `spk_0`으로 시작하는 문제(ADR 0044의 청크 경계 재검토와 같은 뿌리), interactions API의 `previous_interaction_id`로 청크 사이 label을 이을 수 있는지 확인.
