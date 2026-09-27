# {{PROJECT_NAME}}

Video editing project. Replace `{{PROJECT_NAME}}` and fill in the sections below.

## About this video

(What it is, who it is for, target platform, aspect ratio, target length, style references.)

## Layout

- `footage/`: source media, read-only. Nothing writes here.
- `edit/`: everything generated: transcripts, `edl.json`, previews, final renders, and `project.md` (session memory, appended each session).

## Environment (once per machine)

- `brew install ffmpeg-full auto-editor`
- ffmpeg-full is keg-only. Put it first on `PATH` so `ffmpeg` has libass, freetype and zimg, which burned-in subtitles and `drawtext` need (the plain `ffmpeg` formula lacks them). The brew line below also puts ffmpeg's developer tools on `PATH`.
  ```bash
  echo 'export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH' >> ~/.zshrc
  ```
- A whisper model for word-level transcripts. `ggml-small` kept fillers in both Korean and English when tested on synthesized speech; without a model, transcription falls back to macOS's `apple` backend, which drops English "um" and "uh".
  ```bash
  mkdir -p ~/.local/share/whisper.cpp
  curl -L -o ~/.local/share/whisper.cpp/ggml-small.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin
  echo 'export WHISPER_MODEL=$HOME/.local/share/whisper.cpp/ggml-small.bin' >> ~/.zshrc
  ```
- HyperFrames, for HTML-rendered animation overlays. `.claude/settings.json` enables it but does not download it: run `claude plugin install hyperframes@claude-plugins-official --scope project` once per machine. Needs Node 22+.
- Remotion, for React-rendered animation overlays. Its plugin comes from a third-party marketplace, so add the marketplace first; keep `--scope project`, since Remotion's own docs omit it and that installs at user scope.
  ```bash
  claude plugin marketplace add remotion-dev/claude-code-plugin
  claude plugin install remotion@remotion --scope project
  ```
  The skills are MIT. Rendering uses the `remotion` npm packages under the Remotion License: free for individuals, for-profit organizations with up to 3 employees, and non-profits; other companies need a company license (remotion.pro/license).
- Verify: `bash .claude/skills/ffmpeg-recipes/scripts/check_env.sh`

## Conventions

- Transcripts for cutting come from `edit-by-transcript`'s `transcribe.py` (word timings, cached in `edit/transcripts/`). The user-scope `transcribe` skill (Gemini) produces readable markdown without usable cut timings; use it only when the user wants text to read or quote.
- auto-editor 31.6.0 takes one range per `--cut`: write `--cut 5sec,10sec --cut 20sec,25sec`. The `auto-editor` skill's example `--cut 0,30 -10sec,end` fails on this version.
- Claude cannot watch or listen. Report measured values (durations from `ffprobe`, LUFS and true peak, frames extracted and viewed) instead of impressions.
- Default delivery: H.264 and AAC in MP4, -14 LUFS, unless the user names a platform with its own spec.
