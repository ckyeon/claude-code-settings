# 자막

## 자막 파일 만들기

auto-editor의 whisper로 SRT를 만든다(auto-editor-transcribe skill). `--language`는 항상 준다.

```bash
auto-editor whisper in.mp4 "$WHISPER_MODEL" --language ko --format srt -o edit/in.srt
auto-editor whisper in.mp4 apple --language ko_KR --format srt -o edit/in.srt   # WHISPER_MODEL이 없을 때
```

- `apple` backend는 언어를 지정하지 않으면 영어로 처리해서 한국어가 엉터리 영어 문장이 된다(실측).
- 오인식이 흔하다(실측: 두 backend 모두 "무음"을 "모음"으로 적었다). 입히기 전에 SRT를 읽고, 고유명사와 문맥에 안 맞는 단어를 사용자에게 확인한다.
- 컷 편집을 한 영상은 원본으로 만든 SRT와 시간이 어긋난다. 편집 결과물의 자막은 edit-by-transcript skill의 `render.py --subtitles`가 출력 기준 시간으로 만든다. 편집이 끝난 영상을 다시 전사해도 된다.

## 영상에 입히기 (burn-in)

```bash
ffmpeg -i in.mp4 -vf "subtitles=edit/in.srt:force_style='FontName=Apple SD Gothic Neo,FontSize=22,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=40'" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a copy edit/subbed.mp4
```

- libass가 있는 ffmpeg가 필요하다(ffmpeg-full).
- `force_style`은 ASS 스타일 필드다. 색은 `&HAABBGGRR`(alpha, blue, green, red 순). `Alignment=2`는 가운데 아래, `8`은 가운데 위. `BorderStyle=3`은 외곽선 대신 반투명 상자를 깐다.
- `FontName`을 빼도 fontconfig가 한국어 글꼴로 대신 그린다(실측). 다만 굵기와 크기를 통제하려면 명시한다. 쓸 수 있는 글꼴은 `fc-list :lang=ko family`로 확인한다.
- `FontSize`는 픽셀 값보다 크게 그려진다(실측: 1280x720에서 `FontSize=22`인 21자 한국어 자막 한 줄이 화면 폭의 절반을 넘었다). 크기와 위치는 frame을 뽑아 확인한다.
- 자막 파일 경로에 `:`나 `'`가 있으면 filtergraph 해석이 깨질 수 있다. `edit/` 아래 단순한 이름으로 두고 쓴다.
- crop, overlay, 텍스트와 함께 쓰면 `subtitles`를 filter 체인의 마지막에 둔다.

### 세밀한 스타일 (ASS)

```bash
ffmpeg -i edit/in.srt edit/in.ass
# edit/in.ass의 [V4+ Styles] 아래 Style: 줄을 고친다
ffmpeg -i in.mp4 -vf "ass=edit/in.ass" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a copy edit/subbed.mp4
```

변환 직후 기본 스타일은 `Style: Default,Arial,16,...`이다(실측). Arial을 한국어 글꼴 이름으로 바꾼다.

## 자막 트랙으로 넣기 (soft subtitle)

재인코딩 없이 넣고, 보는 사람이 켜고 끌 수 있다.

```bash
# MP4
ffmpeg -i in.mp4 -i edit/in.srt -map 0 -map 1 -c copy -c:s mov_text -metadata:s:s:0 language=kor edit/soft.mp4
# MKV, 두 언어, 한국어를 기본으로
ffmpeg -i in.mp4 -i ko.srt -i en.srt -map 0 -map 1 -map 2 -c copy -c:s srt -metadata:s:s:0 language=kor -metadata:s:s:1 language=eng -disposition:s:0 default edit/soft.mkv
```

언어 코드는 세 글자(`kor`, `eng`)다. 올릴 곳이 자막 파일 업로드를 지원하면 SRT를 따로 올리고, 지원하지 않으면 burn-in한다.

## 자막 추출

```bash
ffmpeg -i in.mkv -map 0:s:0 edit/extracted.srt
```

`0:s:0`은 첫 번째 자막 트랙이다. 텍스트 자막만 SRT로 뽑힌다.

## 싱크 조정

```bash
python3 .claude/skills/ffmpeg-recipes/scripts/srt_shift.py edit/in.srt edit/shifted.srt -0.5   # 0.5초 앞당기기
python3 .claude/skills/ffmpeg-recipes/scripts/srt_shift.py edit/in.srt edit/shifted.srt 1.2    # 1.2초 늦추기
```

ffmpeg의 `-itsoffset`은 늦추기만 된다. 음수를 주거나 `-ss`를 써도 SRT 시간은 그대로다(실측). 0초 앞으로 밀려난 cue는 script가 지운다.
