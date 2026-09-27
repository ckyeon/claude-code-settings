# 색, 자막 스타일, 음악, animation

여기 값은 video-use가 실제 영상에서 쓴 예시다. 정답이 아니므로 재료와 사용자의 취향에 맞게 바꾼다.

## 색보정

frame을 뽑아 무엇이 문제인지 보고, 한 가지를 바꾸고, 다시 본다. EDL의 `filter`에 넣으면 모든 구간에 걸린다. 사용자가 색을 말하지 않았으면 넣지 않는다.

| 이름 | filter | 쓰임 |
|---|---|---|
| subtle | `eq=contrast=1.03:saturation=0.98` | 거의 티 나지 않는 정리 |
| neutral_punch | `eq=contrast=1.06:brightness=0.0:saturation=1.0,curves=master='0/0 0.25/0.23 0.75/0.77 1/1'` | 대비를 조금 올리고 완만한 S curve, 색 변화 없음 |
| warm_cinematic | `eq=contrast=1.12:brightness=-0.02:saturation=0.88,colorbalance=rs=0.02:gs=0.0:bs=-0.03:rm=0.04:gm=0.01:bm=-0.02:rh=0.08:gh=0.02:bh=-0.05,curves=master='0/0 0.25/0.22 0.75/0.78 1/1'` | 대비를 올리고 채도를 낮추며 어두운 곳은 따뜻하게, 밝은 곳은 차갑게. 강하므로 요청이 있을 때만 쓴다 |

조정 전후 비교와 개별 filter는 ffmpeg-recipes의 `references/frame.md` "색보정"에 있다. 사람 피부가 나오면 강한 보정 뒤에 피부색이 자연스러운지 frame으로 확인한다.

## 자막 스타일

`render.py --subtitles`의 기본값은 굵은 흰 글씨에 검은 외곽선, 화면 아래 가운데, cue 하나에 최대 4단어 20자다.

- **짧게 끊기** (빠른 SNS 영상): `--sub-max-words 2 --sub-max-chars 12`.
- **문장 단위** (강의, 다큐멘터리): `--sub-max-words 7 --sub-max-chars 32`, 글씨를 조금 작게, 위치를 조금 위로.
  ```
  --sub-style "FontName=Apple SD Gothic Neo,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1.5,Shadow=0,Alignment=2,MarginV=70"
  ```
- `--sub-style`은 ASS 스타일 문자열 전체를 바꾸므로 `FontName`도 넣는다. 필드 설명은 ffmpeg-recipes의 `references/subtitles.md`에 있다.
- 입힌 뒤에는 frame을 뽑아 글자 크기와 줄바꿈을 확인한다. 휴대폰 화면에서 볼 영상이면 작게 줄여서도 본다.

## 음악과 효과음

섞는 명령(말할 때 음악 줄이기 포함)은 ffmpeg-recipes의 `references/audio.md`에 있다. video-use가 실제 편집에서 얻은 규칙:

- 효과음은 화면에 보이는 사건(컷, 등장, 클릭)마다 하나씩만 쓴다. 18초에 20개면 싸구려처럼 들리고 8개쯤이면 의도한 것처럼 들린다.
- 효과음에는 소리가 터지기 전 준비 구간이 있다. 첫 큰 소리가 파일의 몇 초에 있는지 재서, 그만큼 먼저 시작해 화면의 사건과 맞춘다.
- 말하는 동안 음악은 음악만 나올 때보다 12~15dB 낮춘다. 마지막 화면 앞에서는 음악을 줄여서 끝낸다.
- loudness는 전부 섞은 뒤 마지막에 한 번 맞추고(`render.py` 최종본이 한다), 구간별(말, 음악만, 마지막 화면) 수치를 따로 재서 보고한다. 마지막 화면이 말보다 15dB 작다면 버그다.
- 음악 선택은 사용자의 몫이다. 성격이 다른 후보 두 개를 제안하고 사용자가 듣고 고르게 한다.

## Animation (HyperFrames, Remotion)

이 프로젝트에는 코드로 장면을 만드는 도구가 둘 있다. 작성과 렌더링 방법은 각 도구의 skill을 따르고, 여기에는 고르는 기준과 이 편집에 잇는 방법만 둔다.

- **HyperFrames** (plugin, `.claude/settings.json`): HTML, CSS, GSAP로 장면을 쓴다. 제품 UI 움직임, 웹 페이지나 목업을 영상으로, 글자 animation, 투명 배경 overlay에 맞는다.
- **Remotion** (plugin, `remotion-best-practices` skill부터): React component로 장면을 쓴다. 사용자가 React나 Remotion을 원하거나, 상태가 있는 component를 재사용하거나, 이미 Remotion으로 만든 brand 자산이 있을 때 쓴다. slot 디렉터리 안에 Remotion 프로젝트를 따로 만들고, 렌더링 결과의 길이와 해상도를 `ffprobe`로 확인한다.

두 도구 모두 결과는 영상 파일 하나이고, EDL에 잇는 방법은 같다.

- animation 하나마다 `edit/animations/slot_<id>/` 디렉터리를 쓴다. 배경이 투명해야 하면 webm(alpha)으로, 아니면 mp4로 렌더링한다.
- 결과 파일을 EDL `overlays`에 넣는다: `{"file": "edit/animations/slot_1/render.webm", "start_in_output": 12.4, "duration": 5.0}`.
- 여러 개면 slot마다 sub-agent를 동시에 띄운다. brief에 넣을 것: 만들 것 한 문장, 출력 절대 경로, 해상도와 fps와 길이, 색과 글꼴의 구체적인 값, 시간대별 장면 순서, 넣지 말 것, 렌더링 후 `ffprobe`로 길이를 확인하라는 지시, "모호하면 가장 자연스러운 해석으로 진행하고 묻지 마라".
- 팔레트와 글꼴은 사용자에게서 받는다. 받지 못했으면 계획 단계에서 제안하고 승인을 받는다.
- 길이 기준: 내용을 읽어야 하는 카드는 최소 3초, 보통 5~7초. 마지막 frame은 1초 이상 멈춘다. 설명과 맞추는 animation은 핵심 단어가 들리는 순간에 장면이 완성되도록, 그 단어의 시각에서 등장 시간만큼 먼저 시작한다.
- 움직임에는 ease-out이나 ease-in-out을 쓴다. 등속(linear)은 기계적으로 보인다.
- 글꼴은 로드에 실패해도 오류 없이 다른 글꼴로 그려진다. 렌더링 전에 로드됐는지 확인한다: `if (!document.fonts.check('700 76px "Pretendard"')) throw new Error("font not loaded")`.
