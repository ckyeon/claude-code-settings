# 0058 — 영상 편집용 project template `video` 추가

영상 편집 프로젝트를 시작할 때 복사할 `project-templates/video/`를 추가했다. 공개된 영상 편집 skill을 먼저 조사하고, 쓸 만한 것은 가져오고, 빈 곳은 직접 썼다. template에 넣은 명령과 수치는 모두 ffmpeg-full 9.0.2, auto-editor 31.6.0, macOS 27에서 시험 영상으로 실행해 확인했다(2026-09-27). 한국어와 영어 영상을 모두 다룬다.

## 구성

| 항목 | 출처 | 방식 |
|---|---|---|
| `auto-editor`, `auto-editor-effects`, `auto-editor-export`, `auto-editor-transcribe` | WyattBlue/auto-editor@7796222, Unlicense | copied |
| `ffmpeg-recipes` (SKILL.md, reference 5개, `check_env.sh`, `loudnorm.py`, `srt_shift.py`) | 직접 작성 | sidecar 없음 |
| `edit-by-transcript` (SKILL.md, reference 2개, script 4개) | browser-use/video-use@b877063, MIT | inspired-by |
| HyperFrames plugin | heygen-com/hyperframes@8d2b6e7 (claude-plugins-official이 고정한 sha), Apache-2.0 | template의 `enabledPlugins`, provenance는 `user/shared/plugins/hyperframes/` |
| Remotion plugin (skill 12개) | remotion-dev/claude-code-plugin@a39a501, MIT (plugin manifest 선언) | template의 `enabledPlugins`와 `extraKnownMarketplaces`, provenance는 `user/shared/plugins/remotion/` |

## Considered Options

- **video-use를 그대로 복사**: 전사가 ElevenLabs Scribe 유료 API로 고정되어 있다. 사용자가 유료 key 대신 inspired-by 재작성을 골랐다.
- **ffmpeg MCP server들**: Bash로 ffmpeg를 직접 부르는 것보다 기능이 적다. 제외했다.
- 그 밖에 조사한 후보(media-os, JosiahSiegel ffmpeg skill, ECC video-editing, jianshuo, cut-video, Rendi cheatsheet 등)는 license 부재, 틀린 recipe, 유료 서비스 의존, 영어 전용 튜닝 중 하나 이상에 걸려 제외했다. 예를 들어 media-os의 trim 예시는 30초를 만든다고 적었지만 실행하면 그렇지 않았다.

## 결정과 근거

- **ffmpeg-full을 전제로 한다.** Homebrew 기본 `ffmpeg`에는 libass와 freetype이 없어 `subtitles`, `ass`, `drawtext`, `zscale` filter가 없다. ffmpeg-full은 keg-only라 PATH를 직접 잡아야 하고, template의 CLAUDE.md와 `check_env.sh`가 이를 안내한다.
- **편집용 전사는 로컬 whisper model(ggml-small)이 기본이다.** 합성 음성 시험에서 macOS `apple` backend는 영어 "um"을 지우고 "uh"를 "Ah"로 바꿨고, 단어 끝 시각이 실제 무음보다 최대 약 0.5초 늦었다. whisper-small은 군더더기를 비는 prompt와 함께 쓸 때 한국어와 영어 군더더기를 모두 남겼고, 오차는 최대 약 0.3초였다. model이 없으면 `apple`로 동작하되 경고한다. 두 backend 모두 언어를 지정해야 한다. `apple`은 언어를 빼면 한국어를 엉터리 영어로 적었다.
- **컷 경계는 실측 무음에 둔다.** ASR 시각을 그대로 쓰면 군더더기의 꼬리가 남았다(실측: whisper가 "어,"의 끝을 4.57초로 적었는데 실제 무음은 4.661~4.854초였다). 가장 가까운 무음으로 자동으로 옮기는 방식은 검토 후 버렸다. 이 사례에 규칙을 대입하면 군더더기를 다시 포함하는 쪽을 고르는 경우가 있었기 때문이다. 대신 `pack.py`와 `timeline_view.py`가 실측 무음을 보여주고, 경계는 agent가 정한다.
- **자막 단어는 EDL의 `quote`로 고른다.** 시각만으로 고르면 구간 시작 직후의 "how"가 빠졌다.
- **`render.py`는 이음매의 1 frame 빈틈을 없앤다.** 구간 길이를 frame 단위로 자르고, 추출 단계의 오디오를 PCM으로 둔다. AAC는 마지막에 한 번만 인코딩한다. 소스 fps가 다를 때 첫 frame이 밀리는 문제는 `setpts=PTS-STARTPTS`로 막았다. 투명 webm overlay는 libvpx decoder로 읽는다. 기본 decoder는 alpha를 버리고 검은 배경을 깔았다.
- **loudnorm 기본 true peak은 -1.5 dBTP다.** -1을 목표로 하면 AAC 출력이 -0.84 dBTP로 상한을 넘었다.
- **코드로 만드는 영상은 HyperFrames와 Remotion을 둘 다 둔다.** 둘 다 headless Chrome과 FFmpeg로 렌더링한다. HyperFrames는 HTML로, Remotion은 React component로 장면을 쓴다. 첫 초안은 license를 이유로 Remotion을 뺐지만 근거가 부정확했다. Remotion 프레임워크의 Remotion License(`remotion-dev/remotion/LICENSE.md`)는 개인, 직원 3명 이하 영리 조직, 비영리 조직에 무료이고 상업적 사용도 허용하며, 그 밖의 조직에만 회사 license를 요구한다. skill 자체는 Remotion의 공식 Claude Code plugin(`remotion@remotion`)이 manifest에서 MIT로 선언한다. 처음에는 `remotion-dev/skills`의 skill 12개를 copied로 가져왔다가, 사용자가 plugin의 존재를 짚은 뒤 plugin으로 바꿨다. 같은 skill이고(버전 4.0.529, 지도 예제 `.tsx` 몇 개만 다르다), HyperFrames와 같은 방식이며, 약 2.3MB와 280여 개 파일을 repo에 넣지 않아도 되기 때문이다.
- **HyperFrames는 project scope로만 켠다.** 공식 문서에 따르면 shell의 `claude plugin install`은 기본이 user scope이고, 프로젝트 settings의 `enabledPlugins`만으로는 plugin이 내려받아지지 않는다. 그래서 README에 `--scope project` 설치 명령을 적었다.

## Consequences

- adopt한 upstream `auto-editor` skill의 `--cut 0,30 -10sec,end` 예시는 auto-editor 31.6.0에서 실패한다. 두 번째 구간을 입력 파일로 읽기 때문이다. copied 항목이라 본문은 고치지 않았고, template CLAUDE.md와 `ffmpeg-recipes`에 `--cut`을 구간마다 반복하라고 적었다. upstream에 알릴지는 따로 정한다.
- `bin/check-integrity`는 `user/shared/skills/`만 검사하므로 template 안의 skill은 검사하지 않는다. 이번 결과는 clean이다(`--strict` 포함).
- 검증은 scratch 디렉터리에 README 절차대로 template을 복사한 뒤, 문서의 명령 50개를 zsh로 실행해서 했다. 50개 모두 통과했다. 음성은 macOS `say`로 합성한 것이라 실제 말버릇에서의 군더더기 보존율과 timestamp 오차는 아직 재지 않았다.
- zsh에서는 filtergraph 안의 `$OFF[v]`가 배열 첨자로 해석된다. `ffmpeg-recipes`에 `${OFF}`로 쓰라고 적었다.
- template에서만 켜는 third-party marketplace는 remotion이 처음이다. `lib/common.sh`의 `list_tracked_plugins`가 marketplace 저장소 주소를 user settings에서만 읽어서, `install.sh`가 remotion을 built-in marketplace로 분류하고 `marketplace add` 안내를 빠뜨렸을 것이다. template settings의 `extraKnownMarketplaces`도 읽도록 고쳤다(user settings가 우선). 고친 뒤 `install.sh`의 plugin 안내 부분만 떼어 실행해 `/plugin marketplace add remotion-dev/claude-code-plugin`이 출력되는 것을 확인했다.
- Remotion 공식 문서의 설치 명령에는 `--scope`가 없어서 그대로 따르면 user scope로 설치된다. template CLAUDE.md와 plugin README에 `--scope project`를 붙인 명령을 적었다. third-party marketplace는 자동 업데이트가 기본으로 꺼져 있다.
- Remotion의 license 조건은 template CLAUDE.md에 적었다. 직원 4명 이상인 회사 업무에 Remotion으로 렌더링하면 회사 license가 필요하다.
- template의 `.claude/settings.json` 권한 목록은 다른 template처럼 비워 뒀다. ffmpeg와 script 실행을 미리 허용할지는 따로 정한다.
