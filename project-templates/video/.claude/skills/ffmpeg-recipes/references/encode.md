# 변환과 압축

## 컨테이너만 바꾸기 (재인코딩 없음)

```bash
ffmpeg -i in.mkv -c copy -movflags +faststart edit/out.mp4
ffmpeg -i in.mp4 -c copy edit/out.mkv
```

stream의 codec이 대상 컨테이너에 들어갈 수 있을 때만 된다. 실패하면 문제가 된 stream만 재인코딩한다. 예: `-c:v copy -c:a aac`.

## 화질 기준 압축 (CRF)

| codec | 옵션 | 기본 CRF | 비고 |
|---|---|---|---|
| H.264 | `-c:v libx264 -crf 23 -preset medium` | 23 | 가장 널리 재생된다 |
| HEVC | `-c:v libx265 -crf 28 -preset medium -tag:v hvc1` | 28 | ffmpeg 기본 tag는 `hev1`이다(실측). Apple 기기에서 재생할 파일은 `hvc1`로 바꾼다. Apple HLS 명세가 "use 'avc1', 'hvc1', or 'dvh1' rather than 'avc3', 'hev1', or 'dvhe'"라고 요구한다 |
| AV1 | `-c:v libsvtav1 -crf 35 -preset 8` | | CRF 범위 0~63, preset 범위 -2~13이고 숫자가 클수록 빠르다 |

- 기본 CRF 23과 28은 인코더가 출력 파일에 기록한 설정 문자열(`crf=23.0`, `crf=28.0`)로 확인했다. x264와 x265의 CRF 범위는 0~51이다(x265 CLI 문서).
- `-preset`은 느릴수록 같은 화질에서 파일이 작다. `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`(기본), `slow`, `slower`, `veryslow` 순이다.
- 같은 CRF라도 영상 내용에 따라 용량이 크게 달라진다. 긴 영상은 10초 구간(`-ss 60 -t 10`)으로 CRF 두세 개를 시험 인코딩해 용량과 화질을 비교한 뒤 전체를 돌린다.

## 목표 용량에 맞추기 (2-pass)

"10MB 이하로" 같은 요청에 쓴다. 용량을 비트레이트로 바꿔 두 번 인코딩한다.

```bash
T=10    # 목표 크기, MiB
A=128   # 오디오 kbps
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 in.mp4)
VB=$(awk "BEGIN{printf \"%d\", $T*8192/$D - $A}")
ffmpeg -y -i in.mp4 -c:v libx264 -b:v ${VB}k -preset medium -pass 1 -passlogfile edit/ffpass -an -f null /dev/null
ffmpeg -i in.mp4 -c:v libx264 -b:v ${VB}k -preset medium -pass 2 -passlogfile edit/ffpass -pix_fmt yuv420p -c:a aac -b:a ${A}k -movflags +faststart edit/out.mp4
rm -f edit/ffpass*
```

- 실측: 30초 영상에 2MiB 목표로 1.98MiB.
- `VB`가 작게 나오면 화질이 무너지므로 해상도를 함께 낮춘다(아래). 사용자에게 계산된 비트레이트와 해상도를 알려준다.

## 해상도 낮추기

```bash
ffmpeg -i in.mp4 -vf scale=-2:720 -c:v libx264 -crf 23 -pix_fmt yuv420p -c:a copy edit/out_720p.mp4
```

`-2`는 비율을 유지하면서 폭을 짝수로 맞춘다(실측: 1280x720에 `scale=-2:480`을 걸면 854x480).

## GIF

```bash
ffmpeg -ss 1 -t 3 -i in.mp4 -filter_complex "fps=12,scale=480:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" -loop 0 edit/clip.gif
```

`palettegen`이 이 구간에 맞춘 256색 팔레트를 만들고 `paletteuse`가 그 팔레트로 변환한다. GIF는 용량이 빨리 커진다(실측: 3초, 480px, 12fps에 약 560KB). 길이, 폭, fps를 줄여 크기를 맞춘다.
