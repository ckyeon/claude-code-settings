# 0044 — 자작 스킬 `transcribe` 추가 (로컬 파일 Gemini 전사)

로컬 오디오·영상 파일을 Gemini API(`gemini-3.5-transcribe`, verbatim)로 전사하는 자작 스킬을 `user/shared/skills/transcribe/`에 추가했다. 원본은 llm-wiki의 `intake/scripts/yt2raw.py` Gemini 경로(2026-09-02 실측 검증본)인데, 위키 계약(raw/ 저장·파일명 유일성·Whisper 폴백·60초 앵커 강제)이 섞여 있어 다른 프로젝트(강의 녹음 등)에서 재사용할 수 없었다. 자작이므로 `.provenance.json`은 두지 않는다(CLAUDE.md "Add a self-authored item").

## 결정 (2026-09-03)

- **입력은 로컬 파일만.** YouTube 등 URL 다운로드는 나중에 별도 스킬로 뺀다.
- **Gemini 단일 경로.** Whisper 폴백을 넣지 않는다 — Mac 전용 mlx 의존을 범용 스킬에 넣지 않기 위해서다. 키는 `GEMINI_TRANSCRIBE_API_KEY` 하나만 읽는다(범용 `GEMINI_API_KEY`는 다른 과금 프로젝트일 수 있어 읽지 않는다).
- **앵커는 옵션(`--anchors [초]`), 기본 off.** word timestamp는 공식 문서가 정확도 저하 가능성을 경고하는 옵션이라 앵커를 켤 때만 요청한다.
- **yt2raw와는 독립 복제.** yt2raw는 손대지 않는다. 파서를 고칠 일이 생기면 합치기를 재심한다.

## Consequences

- `~/.claude/skills`가 이 폴더의 symlink이므로 폴더를 만드는 즉시 모든 프로젝트에서 보인다. `install.sh` 재실행 불필요.
- 앵커 off일 때 요청 본문의 `mode`가 `{"type": "verbatim"}`만 담기는 지점은 초안에서 실측 없이 바뀐 유일한 부분이었다. 2026-09-03 macOS `say`로 만든 20초 클립으로 스모크한 결과 API가 timestamp 없는 verbatim을 그대로 받아 본문을 돌려줬다(m4a `--plain`, 그리고 mp4 → ffmpeg 오디오 추출 경로 `--out` 모두 통과). 앵커 on 경로는 원본 yt2raw에서 검증된 코드 그대로라 재실측하지 않았다.
- 나중에: URL 입력 스킬, 앵커 off 모드의 25분 청크 경계(문장 중간 절단) 재검토, llm-wiki yt2raw가 이 스킬을 import하도록 합치기.
