---
name: edit-by-transcript
description: 말한 내용을 기준으로 영상을 편집한다. 전사를 읽고 군더더기, 말실수, NG take를 잘라내고, 여러 take 중 좋은 것을 골라 잇고, 자막과 overlay를 얹어 렌더링한다. "음, 어 같은 말버릇 빼줘", "NG 난 부분 잘라줘", "제일 잘 된 take로 이어줘", "10분짜리를 3분으로 줄여줘", "말하는 내용 기준으로 편집해줘"라는 요청에 쓴다.
---

# Edit by transcript

무엇을 자를지는 전사로 정하고, 어디서 자를지는 오디오에서 잰 무음으로 정한다. 무음만 기계적으로 지우는 일은 auto-editor가 빠르고, 파일 하나를 변환하거나 가공하는 일은 ffmpeg-recipes가 맡는다.

browser-use/video-use의 방법을 이 프로젝트의 도구(auto-editor whisper, ffmpeg)에 맞게 다시 쓴 것이다. "실측"이 붙은 내용은 이 template을 만들며 시험 영상으로 확인한 결과다(2026-09-27).

## 도구

프로젝트 루트에서 실행한다. 아래에서 `$S`는 `.claude/skills/edit-by-transcript/scripts`다. 옵션은 각 script의 `--help`에 있다.

| script | 하는 일 |
|---|---|
| `transcribe.py <소스...> --lang ko` | 단어 단위 전사를 `edit/transcripts/<이름>.json`에 캐시한다 |
| `pack.py` | 전사와 실측 무음을 합쳐 구절 단위 읽기용 `edit/takes_packed.md`를 만든다 |
| `timeline_view.py <영상> <시작> <끝> [--mark T]` | filmstrip과 waveform PNG를 만들고, 그 구간의 짧은 무음 목록을 출력한다 |
| `render.py edit/edl.json -o <출력> [--preview] [--subtitles]` | EDL을 렌더링한다 |

## 규칙

`render.py`가 지키는 규칙이다. ffmpeg로 직접 합칠 때도 똑같이 지킨다.

- 구간마다 따로 추출해 같은 사양으로 인코딩하고, concat demuxer의 `-c copy`로 잇는다.
- 구간 양 끝에 30ms audio fade를 건다. 없으면 컷마다 튀는 소리가 난다.
- 구간 길이를 frame 단위로 맞추고, 추출 단계의 오디오는 PCM으로 둔다. frame 반올림과 AAC padding이 이음매마다 1 frame 빈틈을 만들기 때문이다(실측).
- overlay는 `setpts=PTS-STARTPTS+T/TB`로 첫 frame을 시작 시각에 맞춘다. 투명 webm은 libvpx decoder로 읽는다. 기본 decoder는 alpha를 버리고 검은 배경으로 덮는다(실측).
- 자막은 filter 체인의 마지막에 입힌다(실측: 화면 전체를 덮는 overlay 위에서도 자막이 보였다). 자막 시간은 출력 기준이다.

직접 지켜야 하는 규칙이다.

1. **계획 승인이 먼저다.** 편집 방향을 평이한 말로 제안하고, 사용자가 승인한 뒤에 EDL을 쓴다.
2. **경계는 실측 무음 안에 둔다.** ASR 단어 시각은 흔들린다(실측: whisper-small에서 최대 약 0.3초, apple backend에서 최대 약 0.5초).
   - 구절 사이 경계는 `takes_packed.md`의 `~ silence` 줄 범위 안에 둔다.
   - 구절 안 경계(군더더기와 말실수의 앞뒤)는 전사 시각 앞뒤 1초를 `timeline_view.py`로 보고, 출력된 짧은 무음 안에 둔다. 무음이 없으면 단어 경계에 두고 렌더링 결과의 waveform으로 확인한다.
   - 경계는 말소리에서 30~200ms 떨어뜨린다. 남길 말의 시작 앞 50ms, 끝 뒤 80ms가 출발점이다(video-use 예시값).
   - 실측 사례: whisper는 "어,"가 4.57초에 끝난다고 했지만 무음 목록은 4.661~4.854초였다. 4.57초에서 자르면 "어"의 꼬리 0.09초가 남고, 무음 안인 4.80초에서 자르면 깨끗하다.
3. **quote는 전사의 단어를 그대로 옮긴다.** `render.py --subtitles`는 quote와 전사 단어를 맞춰 그 구간의 자막 단어를 고른다. 경계 근처 단어는 시각이 흔들려서 시각만으로 고르면 빠지거나 끼어든다(실측: 구간 시작 직후의 "how"가 빠졌다). quote가 전사와 다르면 경고를 출력하고 시각 기준으로 고른다.
4. **전사는 소스마다 한 번 한다.** `transcribe.py`가 캐시하고, 소스 파일이나 model, 언어가 바뀔 때만 다시 전사한다.
5. **산출물은 모두 `edit/` 아래에 둔다.** 원본 소스는 읽기만 한다.

## 과정

1. **환경.** `bash .claude/skills/ffmpeg-recipes/scripts/check_env.sh`를 실행하고 `FAIL`이 없을 때 진행한다. `WHISPER_MODEL` 경고가 떴는데 영어 군더더기를 다뤄야 하면 사용자에게 알린다. apple backend는 영어의 "um"을 지우고 "uh"를 "Ah"로 바꾼다(실측).
2. **이전 세션.** `edit/project.md`가 있으면 읽고, 지난 세션을 한 문장으로 요약한 뒤 이어서 할지 묻는다.
3. **재료 파악.** 모든 소스를 `ffprobe`로 본다. 말하는 언어를 사용자에게 확인하고 `python3 $S/transcribe.py footage/*.mp4 --lang <언어>`, 이어서 `python3 $S/pack.py`를 실행한다. `edit/takes_packed.md`를 끝까지 읽고, 화면의 첫인상을 보려고 `timeline_view.py`를 한두 번 돌린다. 완료 기준: 모든 소스가 `takes_packed.md`에 있고, 소스마다 길이와 내용을 요약할 수 있다.
4. **사전 점검.** `takes_packed.md`를 한 번 더 훑어 말실수, 반복, NG, 군더더기가 몰린 곳을 목록으로 적는다.
5. **대화.** 본 것을 평이하게 설명하고 재료에서 나온 질문을 한다. 모아야 할 것: 영상 종류, 목표 길이와 화면 비율, 꼭 살릴 부분과 뺄 부분, 자막 여부와 스타일, 음악, 색.
6. **계획 제안.** 4~8문장으로 구성, take 선택, 자를 것, 자막, overlay, 색, 예상 길이를 제안하고 승인을 기다린다.
7. **EDL 작성.** `edit/edl.json`에 쓴다(형식은 아래). take가 여럿이면 [references/multi-take.md](references/multi-take.md)의 brief로 sub-agent에게 고르게 한다. 구절 안 경계마다 규칙 2의 확인을 거친다.
8. **미리보기.** `python3 $S/render.py edit/edl.json -o edit/preview.mp4 --preview`(자막이 필요하면 `--subtitles`). 마지막 줄이 `ok`여야 한다. `CHECK`는 출력 길이가 EDL 합계와 1 frame 넘게 다르다는 뜻이다.
9. **자기 검증.** 사용자에게 보이기 전에 한다.
   - 출력에서 컷 시각은 앞 구간 길이의 누적합이다(`render.py`가 구간마다 길이를 출력한다). 컷마다 `python3 $S/timeline_view.py edit/preview.mp4 <컷-1.5> <컷+1.5> --mark <컷>`을 실행하고 이미지를 연다. 컷 직후의 짧은 소리 조각(자르려던 단어의 꼬리), 컷 위치의 waveform 튐, 화면 튐을 찾는다.
   - 처음 2초, 끝 2초, 중간 두세 곳의 frame을 뽑아 자막 가독성, overlay 위치, 색의 일관성을 본다.
   - 문제가 있으면 EDL을 고쳐 다시 렌더링한다. 세 번 돌아도 남으면 남은 문제를 사용자에게 보고한다.
   - 완료 기준: 모든 컷을 확인했고, 찾은 문제는 고쳤거나 보고 목록에 올렸다.
10. **반복과 최종본.** 사용자의 피드백으로 EDL을 고친다. 전사는 다시 돌리지 않는다. 승인되면 `python3 $S/render.py edit/edl.json -o edit/final.mp4`(필요하면 `--subtitles`)로 최종본을 만든다. 최종본에는 loudness 정규화가 들어가므로 출력된 LUFS와 true peak 수치를 보고한다. 소리를 직접 들을 수 없으니 "잘 들린다"가 아니라 수치로 보고한다.
11. **기록.** `edit/project.md`에 이번 세션을 덧붙인다.
    ```markdown
    ## Session N — YYYY-MM-DD
    **Strategy:** 한 문단
    **Decisions:** take 선택, 컷, 색, overlay와 그 이유
    **Outstanding:** 남은 일
    ```

## EDL

```json
{
  "sources": {"take1": "footage/take1.mp4", "take2": "footage/take2.mp4"},
  "ranges": [
    {"source": "take1", "start": 2.42, "end": 6.85, "beat": "HOOK",
     "quote": "오늘은 영상 편집을 자동으로 하는 방법을 알려드릴게요.", "reason": "가장 또렷한 take"},
    {"source": "take2", "start": 14.30, "end": 28.90, "beat": "STEP1",
     "quote": "...", "reason": "말을 더듬지 않은 유일한 take"}
  ],
  "output": {"width": 1080, "height": 1920, "fps": 30},
  "filter": "crop=ih*9/16:ih",
  "overlays": [{"file": "edit/animations/slot_1/render.webm", "start_in_output": 0.0, "duration": 5.0}],
  "subtitles": "edit/custom.srt"
}
```

- 경로는 프로젝트 루트 기준이다.
- `output`을 빼면 첫 구간 소스의 해상도와 fps를 쓴다. 비율이 다른 소스는 `pad`로 여백이 생긴다.
- `filter`는 모든 구간에 크기 조정보다 먼저 거는 filter다. 색보정(예시는 [references/look.md](references/look.md))이나 세로 영상용 crop을 넣는다.
- `subtitles`는 이미 있는 SRT를 입힐 때 쓴다. `--subtitles`를 주면 전사로 `edit/master.srt`를 만들어 입히고 이 값은 무시한다.
- `beat`와 `reason`은 렌더링에 쓰이지 않지만 나중에 편집을 고칠 때 근거가 된다. `quote`는 자막 단어를 고르는 데 쓰인다(규칙 3).

## 군더더기 후보

| 언어 | 후보 |
|---|---|
| 한국어 | 음, 어, 아, 그, 저, 뭐, 이제, 그러니까, 약간 |
| 영어 | um, uh, ah, like, you know, so, I mean, basically |

"그러니까", "이제", "like", "so"는 내용을 잇는 말로 쓰일 때가 많다. 문맥으로 판단하고, 확신이 없으면 남긴다. 구절 안 군더더기의 단어 시각은 `edit/transcripts/<이름>.json`에서 해당 줄을 찾아 읽는다(한 줄에 한 단어, 단위 ms).

## 색, 자막 스타일, 음악, animation

요청이 있을 때 [references/look.md](references/look.md)를 읽는다.
