# 오디오

## Loudness 정규화

```bash
python3 .claude/skills/ffmpeg-recipes/scripts/loudnorm.py in.mp4 edit/out.mp4           # -14 LUFS, true peak -1.5 dBTP
python3 .claude/skills/ffmpeg-recipes/scripts/loudnorm.py in.mp4 edit/out.mp4 --i -23   # EBU R128 방송 기준
python3 .claude/skills/ffmpeg-recipes/scripts/loudnorm.py in.mp4 --measure               # 측정만
```

- 1차로 측정하고 그 값을 2차에 넘겨 선형 gain으로 맞춘다. 영상은 복사하고 오디오만 재인코딩한다. script가 처리 전후 수치를 출력하므로 그 수치를 사용자에게 보고한다.
- 목표는 사용자가 올릴 곳의 기준을 따른다. 말이 없으면 -14 LUFS를 쓴다. -14는 video-use가 공개용 영상에 쓰는 값이고, -23은 EBU R128 방송 기준이다.
- 기본 true peak을 -1.5로 둔 이유: -1을 목표로 했을 때 AAC 출력이 -0.84 dBTP로 상한을 넘었다(실측). -1.5를 목표로 하면 -1.49였다.
- 측정만 할 때는 ffmpeg로도 된다. 출력 끝의 Summary에서 `I:`가 통합 loudness, `Peak:`가 true peak이다.
  ```bash
  ffmpeg -hide_banner -nostats -i in.mp4 -af ebur128=peak=true -f null -
  ```
- auto-editor로 편집하면서 함께 맞추려면 `-anorm ebu`를 붙인다.
- 소리를 직접 들을 수 없으므로 "잘 들린다"가 아니라 측정한 수치로 보고한다.

## 오디오 추출

| 형식 | 명령 |
|---|---|
| 원본 codec 그대로 | `ffmpeg -i in.mp4 -vn -c:a copy edit/audio.m4a` (AAC일 때. 다른 codec이면 확장자를 맞춘다) |
| WAV | `ffmpeg -i in.mp4 -vn -c:a pcm_s16le edit/audio.wav` |
| MP3 | `ffmpeg -i in.mp4 -vn -c:a libmp3lame -q:a 2 edit/audio.mp3` |

## 오디오 교체와 음소거

```bash
ffmpeg -i video.mp4 -i narration.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest edit/out.mp4
ffmpeg -i in.mp4 -c:v copy -an edit/muted.mp4
```

`-shortest`는 영상과 오디오 중 짧은 쪽에 맞춰 끝낸다.

## 배경음악 깔기 (말할 때 자동으로 줄이기)

```bash
ffmpeg -i in.mp4 -stream_loop -1 -i music.mp3 -filter_complex "[0:a]asplit=2[voice][sc];[1:a]volume=0.3[bgm];[bgm][sc]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[ducked];[voice][ducked]amix=inputs=2:duration=first:normalize=0[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k edit/with_music.mp4
```

- `sidechaincompress`가 두 번째 입력(목소리)을 감지해 첫 번째 입력(음악)을 누른다. 실측: 말하는 동안 음악이 -40dB 안팎, 쉬는 동안 -31.5dB로 8~12dB 내려갔다.
- `-stream_loop -1`은 음악이 짧으면 반복하고, `duration=first`는 영상 길이에서 끝낸다.
- `amix`의 `normalize=0`을 빼면 기본값(`normalize=1`)이 입력들의 볼륨을 나눠 줄인다.
- 음악의 기본 크기는 `volume`, 반응 감도는 `threshold`로 조정한다. `threshold`가 낮을수록 작은 목소리에도 음악을 누른다.
- 끝에서 음악을 줄이려면 `[1:a]volume=0.3,afade=t=out:st=<D-3>:d=3[bgm]`처럼 fade를 넣는다.
- 섞은 뒤 마지막에 loudness 정규화를 한 번 한다.

## 목소리 정리

```bash
ffmpeg -i in.mp4 -c:v copy -af "highpass=f=80,afftdn=nf=-40" -c:a aac edit/clean.mp4
```

- `highpass=f=80`은 80Hz 아래의 웅웅거리는 저음을 자른다.
- `afftdn`의 `nf`는 잡음 바닥(noise floor)이다. 범위 -80~-20, 기본 -50이고(`ffmpeg -h filter=afftdn`), 값을 올릴수록 더 큰 소리까지 잡음으로 보고 지운다. 강하게 걸수록 목소리도 상하므로 조금씩 올리고, 결과는 들을 수 있는 사용자에게 확인받는다.
- 볼륨만 올리거나 내리려면 `-af volume=6dB`.
