# 자르기와 이어붙이기

## 구간 자르기

정확하게 자르려면 재인코딩한다. `-ss`는 `-i` 앞에 두고(빠른 seek), 길이는 `-t`로 준다.

```bash
ffmpeg -ss 90 -i in.mp4 -t 30 -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k edit/clip.mp4
```

- 끝 시각으로 쓰려면 `-to`도 입력 앞에 둔다: `ffmpeg -ss 90 -to 120 -i in.mp4 ...`(실측 30초).
- `-ss 90 -i in.mp4 -to 120`은 30초가 아니다. 입력 앞에서 seek하면 출력 쪽 `-to`는 0초부터 다시 재므로 120초 분량, 입력이 그보다 짧으면 끝까지 담긴다(실측: 150초 입력에서 60초).
- 시각은 `90`, `90.5`, `00:01:30.500` 모두 된다.

### 빠른 자르기 (`-c copy`)

```bash
ffmpeg -ss 95 -i in.mp4 -t 10 -c copy edit/clip_fast.mp4
```

재인코딩이 없어 금방 끝나지만 시작점이 직전 keyframe으로 당겨진다. MP4는 당겨진 부분을 edit list로 숨겨서 10초처럼 보인다. 실측에서는 10초 요청에 3.3초가 숨은 채 담겼고, mkv로 remux하자 14.3초로 드러났다. 그래서 미리보기나 대략 잘라 공유하는 용도에만 쓰고, 이어붙이거나 다시 편집할 구간은 재인코딩으로 자른다.

## 가운데 구간 삭제

0~10초와 20초~끝을 남긴다.

```bash
ffmpeg -i in.mp4 -filter_complex "[0:v]trim=0:10,setpts=PTS-STARTPTS[v0];[0:a]atrim=0:10,asetpts=PTS-STARTPTS[a0];[0:v]trim=start=20,setpts=PTS-STARTPTS[v1];[0:a]atrim=start=20,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac edit/out.mp4
```

지울 구간이 여럿이면 auto-editor가 짧다. `--cut`을 구간마다 반복한다.

```bash
auto-editor in.mp4 --edit none --cut 5sec,10sec --cut 20sec,25sec -o edit/out.mp4
```

한 `--cut` 뒤에 구간을 공백으로 나열하면(`--cut 5sec,10sec 20sec,25sec`) auto-editor 31.6.0은 두 번째 구간을 입력 파일로 읽고 실패한다(실측). auto-editor skill 본문의 `--cut 0,30 -10sec,end` 예시도 같은 형식이라 그대로 쓰면 실패한다.

## 이어붙이기

### 사양이 같은 파일 (무손실)

video codec, 해상도, fps, 오디오 codec, sample rate, 채널이 모두 같을 때만 쓴다. 먼저 `ffprobe`로 비교한다.

```bash
printf "file '%s'\n" "$PWD/a.mp4" "$PWD/b.mp4" > edit/list.txt
ffmpeg -f concat -safe 0 -i edit/list.txt -c copy edit/joined.mp4
```

### 사양이 다른 파일

각 입력을 같은 해상도, fps, 오디오 형식으로 맞춘 뒤 concat filter로 잇는다. 비율이 다르면 `pad`가 검은 여백을 넣는다. filtergraph는 줄을 나눠 써도 된다(실측).

```bash
ffmpeg -i a.mp4 -i b.mp4 -filter_complex "
[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p[v0];
[1:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p[v1];
[0:a]aformat=sample_rates=48000:channel_layouts=stereo[a0];
[1:a]aformat=sample_rates=48000:channel_layouts=stereo[a1];
[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac edit/joined.mp4
```

오디오가 없는 입력은 같은 길이의 무음을 입력으로 추가해서 그 자리에 쓴다.

```bash
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 silent.mp4)
ffmpeg -i a.mp4 -i silent.mp4 -f lavfi -t "$D" -i anullsrc=r=48000:cl=stereo -filter_complex "[0:a]aformat=sample_rates=48000:channel_layouts=stereo[a0];[0:v][a0][1:v][2:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac edit/joined.mp4
```

## Transition (xfade)

두 입력의 해상도, fps, pix_fmt가 같아야 한다. 다르면 출력에 아무것도 쓰이지 않고 실패하므로(실측), 위 "사양이 다른 파일"의 정규화 체인을 먼저 건다.

```bash
D1=$(ffprobe -v error -show_entries format=duration -of csv=p=0 a.mp4)
OFF=$(awk "BEGIN{print $D1-1}")
ffmpeg -i a.mp4 -i b.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=1:offset=${OFF}[v];[0:a][1:a]acrossfade=d=1[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac edit/xfade.mp4
```

- `offset`은 첫 영상 길이에서 transition 길이를 뺀 값이다. 결과 길이는 두 길이의 합에서 transition 길이를 뺀 값이다(실측 11.83 + 11.73 - 1 = 22.57초).
- 셋 이상은 xfade를 사슬로 잇는다. 각 `offset`은 그때까지 이어진 출력의 길이에서 transition 길이를 뺀 값이다. 세 번째 입력의 offset은 `D1 + D2 - 1 - 1`이다(실측 33.37초로 기대값과 일치).
  ```
  [0:v][1:v]xfade=transition=fade:duration=1:offset=${O1}[x1];[x1][2:v]xfade=transition=slideleft:duration=1:offset=${O2}[v];
  [0:a][1:a]acrossfade=d=1[y1];[y1][2:a]acrossfade=d=1[a]
  ```
- `transition` 값은 `ffmpeg -h filter=xfade`가 나열한다. 예: `fade`, `fadeblack`, `fadewhite`, `wipeleft`, `slideleft`, `circlecrop`, `radial`, `smoothleft`.

## 속도

```bash
# 2배속
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=PTS/2[v];[0:a]atempo=2[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac edit/fast.mp4
# 0.5배속
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=PTS*2[v];[0:a]atempo=0.5[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac edit/slow.mp4
```

`atempo`는 음높이를 유지하고, 이 빌드에서 범위는 0.5~100이다(`ffmpeg -h filter=atempo`). 구간마다 속도를 다르게 하려면 auto-editor의 `--set-speed`나 auto-editor-effects skill을 쓴다.

## Fade in, fade out

길이가 D초인 영상의 처음과 끝 1초:

```bash
ffmpeg -i in.mp4 -vf "fade=t=in:st=0:d=1,fade=t=out:st=<D-1>:d=1" -af "afade=t=in:st=0:d=1,afade=t=out:st=<D-1>:d=1" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac edit/fades.mp4
```
