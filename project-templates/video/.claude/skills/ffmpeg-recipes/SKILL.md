---
name: ffmpeg-recipes
description: ffmpeg로 영상과 오디오 파일을 가공하는 검증된 recipe. 포맷 변환, 용량 압축, 구간 자르기와 이어붙이기, transition, 속도, 세로 영상 변환, 워터마크와 텍스트, 썸네일, 색보정, 흔들림 보정, loudness 정규화, 배경음악, 자막 입히기와 자막 트랙을 다룬다. "mp4로 바꿔줘", "용량 줄여줘", "1분 30초부터 2분까지 잘라줘", "세로로 만들어줘", "자막 입혀줘", "소리 크기 맞춰줘"처럼 파일을 직접 가공하라는 요청에 쓴다.
---

# ffmpeg recipes

여기 적힌 명령과 수치는 ffmpeg-full 9.0.2에서 시험 영상으로 실행해 확인한 것이다(2026-09-27). "실측"이라고 적힌 값이 그 결과다.

## 모든 작업의 공통 단계

1. **환경 점검.** 세션에서 ffmpeg를 처음 쓰기 전에 실행한다. `FAIL` 줄이 없어야 진행하고, 있으면 출력된 해결 방법을 사용자에게 전한다.
   ```bash
   bash .claude/skills/ffmpeg-recipes/scripts/check_env.sh
   ```
2. **입력 파악.** 길이, 해상도, fps, codec, 오디오 유무를 확인하고 recipe의 숫자를 거기에 맞춘다.
   ```bash
   ffprobe -v error -show_entries format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels -of compact <입력>
   ```
3. **출력 위치.** 원본은 읽기만 하고, 결과와 중간 파일(pass log, transform 파일, 목록 파일)은 `edit/` 아래에 새 이름으로 쓴다.
4. **검증.** 출력의 길이와 해상도를 `ffprobe`로 재서 기대값과 비교한다. 재인코딩한 결과는 길이 차이가 1 frame 이내여야 한다. 화면에 보이는 결과(자막, 텍스트, overlay, crop, 색)는 frame을 뽑아 이미지로 열어 본다.
   ```bash
   mkdir -p edit/verify && ffmpeg -v error -ss <초> -i edit/out.mp4 -frames:v 1 edit/verify/frame.png
   ```

## 기본 인코딩 값

재인코딩할 때 다른 값을 쓸 이유가 없으면 이 값을 쓴다.

```
-c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart
```

- `-crf`는 낮을수록 화질이 좋고 파일이 커진다. codec별 값은 [references/encode.md](references/encode.md)에 있다.
- `-pix_fmt yuv420p`는 10bit나 4:4:4 원본을 대부분의 플레이어와 브라우저가 재생하는 형식으로 맞춘다.
- `-movflags +faststart`는 MP4 index를 파일 앞으로 옮겨 웹에서 받는 도중에 재생되게 한다.

여러 가공을 한 번에 할 때(자르고, 세로로 만들고, 자막 입히기)는 filter를 한 명령에 이어서 재인코딩을 한 번으로 줄인다. 자막 filter는 체인의 마지막에 둔다. 앞에 두면 뒤의 overlay가 자막을 덮는다.

## 셸 변수와 filtergraph

filtergraph 안의 셸 변수는 `${OFF}`처럼 중괄호로 감싼다. zsh는 `$OFF[v]`를 배열 첨자로 읽어 빈 값을 넘긴다(실측: xfade가 `Unable to parse "offset" option value ""`로 실패).

## 작업별 recipe

| 작업 | 파일 |
|---|---|
| 자르기, 가운데 구간 삭제, 이어붙이기, transition, 속도, fade | [references/cut-and-join.md](references/cut-and-join.md) |
| 컨테이너 변환, 화질 기준 압축, 목표 용량, 해상도, GIF | [references/encode.md](references/encode.md) |
| 세로 변환, 회전, 워터마크, 텍스트, PiP, 썸네일, 색보정, 노이즈와 흔들림 | [references/frame.md](references/frame.md) |
| loudness 정규화, 오디오 추출과 교체, 배경음악 ducking, 목소리 정리 | [references/audio.md](references/audio.md) |
| 자막 만들기, burn-in, 자막 트랙, 추출, 싱크 조정 | [references/subtitles.md](references/subtitles.md) |
