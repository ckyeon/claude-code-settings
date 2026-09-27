# 화면 가공

## 세로(9:16) 변환

### 가운데 잘라내기

```bash
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920,setsar=1" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a copy edit/vertical.mp4
```

화면 양옆이 잘린다. 인물이 가운데에 있지 않으면 frame을 뽑아 위치를 확인하고 crop의 x를 준다: `crop=ih*9/16:ih:<x>:0`(x는 왼쪽 끝에서 잘라내기 시작할 픽셀). 말하는 사람을 따라 움직이는 reframe은 이 recipe에 없다.

### 전체를 살리고 위아래를 흐린 배경으로 채우기

```bash
ffmpeg -i in.mp4 -filter_complex "[0:v]split[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30[bg];[fg]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]" -map "[v]" -map 0:a -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a copy edit/vertical_blur.mp4
```

정사각형(1:1)은 1920 대신 1080을 쓴다.

## 회전과 뒤집기

`-vf transpose=1`은 시계 방향 90도, `transpose=2`는 반시계 방향 90도다(`ffmpeg -h filter=transpose`). 좌우는 `hflip`, 상하는 `vflip`.

휴대폰 영상이 누워 보이면 먼저 회전 metadata를 확인한다.

```bash
ffprobe -v error -select_streams v -show_entries stream_side_data=rotation -of csv=p=0 in.mp4
```

값이 있으면 ffmpeg가 재인코딩하면서 자동으로 돌린다. 여기에 `transpose`를 또 걸면 두 번 돈다(실측: 90도 metadata가 있는 1280x720 영상은 그냥 재인코딩하면 720x1280이 되고, `transpose=1`을 더하면 다시 1280x720이 된다). metadata를 무시하려면 입력 앞에 `-noautorotate`를 둔다.

## 워터마크 (이미지)

```bash
ffmpeg -i in.mp4 -i logo.png -filter_complex "[1:v]scale=200:-1,format=rgba,colorchannelmixer=aa=0.6[wm];[0:v][wm]overlay=W-w-40:H-h-40[v]" -map "[v]" -map 0:a -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a copy edit/wm.mp4
```

- `aa=0.6`이 불투명도 60%다. 위치는 왼쪽 위 `40:40`, 오른쪽 위 `W-w-40:40`, 가운데 `(W-w)/2:(H-h)/2`.
- 일정 시간에만 보이려면 overlay에 `:enable='between(t,5,10)'`를 붙인다.

## 텍스트

```bash
printf '%s' '편집 테스트' > edit/title.txt
ffmpeg -i in.mp4 -vf "drawtext=textfile=edit/title.txt:font='Apple SD Gothic Neo':fontsize=56:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=16:x=(w-text_w)/2:y=h-text_h-60:enable='between(t,1,6)'" -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a copy edit/text.mp4
```

- `font=`에 한국어 글꼴을 준다. 빠뜨리면 한글이 네모로 나온다(실측). 쓸 수 있는 글꼴은 `fc-list :lang=ko family`로 확인한다.
- 문구는 `textfile=`로 넘긴다. `text=`에 직접 쓰면 `:`, `'`, `%`, `\`를 filtergraph 규칙에 맞게 escape해야 한다.
- `fontsize`는 픽셀 단위다.

## PiP (화면 속 화면)

```bash
ffmpeg -i main.mp4 -i sub.mp4 -filter_complex "[1:v]scale=iw/2:-2[pip];[0:v][pip]overlay=W-w-40:40:eof_action=pass[v]" -map "[v]" -map 0:a -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a copy edit/pip.mp4
```

`eof_action=pass`는 작은 영상이 먼저 끝나면 사라지게 하고 본 영상은 계속 보여준다(실측: 5초 PiP에 11.8초 출력). PiP의 소리도 섞으려면 [audio.md](audio.md)의 `amix`를 쓴다.

## 썸네일과 frame 추출

| 목적 | 명령 |
|---|---|
| 특정 시각 한 장 | `ffmpeg -ss 5 -i in.mp4 -frames:v 1 -q:v 2 edit/thumb.jpg` |
| 대표 장면 자동 선택 | `ffmpeg -i in.mp4 -vf thumbnail=300 -frames:v 1 edit/thumb.jpg` |
| 한 장에 훑어보기 | `ffmpeg -i in.mp4 -vf "fps=1/10,scale=320:-2,tile=4x3" -frames:v 1 edit/contact.jpg` |
| 일정 간격으로 전부 | `mkdir -p edit/frames && ffmpeg -i in.mp4 -vf fps=1/10 edit/frames/f_%03d.jpg` |

- `-q:v`는 JPEG 품질이고 낮을수록 좋다.
- `thumbnail=300`은 300 frame 묶음마다 가장 대표적인 frame을 고른다(기본 100). `-frames:v 1`이면 첫 묶음, 즉 영상 앞부분에서만 고른다.
- `tile=4x3`은 10초마다 한 장씩 12장을 격자 하나로 합친다(실측: 320x180 12장이 1280x540 한 장).

## 색보정

frame을 뽑아 보고 한 가지씩 조정한다. 조정 전후를 나란히 보려면:

```bash
ffmpeg -ss 3 -i in.mp4 -filter_complex "[0:v]split[a][b];[b]<조정 filter>[g];[a][g]hstack" -frames:v 1 edit/verify/compare.png
```

| 조정 | filter |
|---|---|
| 대비, 채도, 밝기 | `eq=contrast=1.08:saturation=1.1:brightness=0.02` (기본값 1, 1, 0) |
| 대비 곡선 | `curves=preset=medium_contrast` (preset 목록은 `ffmpeg -h filter=curves`) |
| 색온도 | `colortemperature=temperature=5500` (기본 6500K, 낮을수록 따뜻한 색. 실측: 3000에서 붉은 성분이 늘고 10000에서 줄었다) |
| LUT | `lut3d=file=look.cube` |

## 노이즈 제거와 흔들림 보정

- 노이즈: `-vf hqdn3d=4:3:6:4`. 값이 클수록 강하고 화면이 뭉개진다.
- 흔들림 보정은 두 번 돌린다(libvidstab).
  ```bash
  ffmpeg -i in.mp4 -vf vidstabdetect=shakiness=5:result=edit/transforms.trf -f null -
  ffmpeg -i in.mp4 -vf vidstabtransform=input=edit/transforms.trf:smoothing=30,unsharp=5:5:0.8:3:3:0.4 -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a copy edit/stable.mp4
  ```
  `vidstabtransform`은 기본으로 흔들림 때문에 생기는 빈 가장자리를 숨기도록 고정 배율로 확대한다(`optzoom=1`). 그래서 화면 가장자리가 조금 잘린다. `smoothing`이 클수록 카메라 움직임을 더 부드럽게 편다(기본 15).
