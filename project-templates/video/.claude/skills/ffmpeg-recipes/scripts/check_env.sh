#!/usr/bin/env bash
# Check the tools this project's video skills rely on. Prints one line per
# check; exits 1 when a required tool is missing.
#
#   bash .claude/skills/ffmpeg-recipes/scripts/check_env.sh

fail=0
ok()   { printf 'ok    %s\n' "$1"; }
warn() { printf 'warn  %s\n      %s\n' "$1" "$2"; }
bad()  { printf 'FAIL  %s\n      %s\n' "$1" "$2"; fail=1; }

if command -v ffmpeg >/dev/null 2>&1; then
  filters="$(ffmpeg -hide_banner -filters 2>/dev/null)"
  missing=""
  for f in subtitles ass drawtext zscale loudnorm xfade; do
    printf '%s\n' "$filters" | grep -q " $f " || missing="$missing $f"
  done
  if [ -z "$missing" ]; then
    ok "ffmpeg $(command -v ffmpeg) has subtitles, ass, drawtext, zscale, loudnorm, xfade"
  else
    bad "ffmpeg $(command -v ffmpeg) lacks:$missing" \
      "macOS: brew install ffmpeg-full, then put /opt/homebrew/opt/ffmpeg-full/bin first on PATH (keg-only)."
  fi
else
  bad "ffmpeg not found" "macOS: brew install ffmpeg-full (see CLAUDE.md > Environment)."
fi

command -v ffprobe >/dev/null 2>&1 && ok "ffprobe" || bad "ffprobe not found" "It ships with ffmpeg."

if command -v auto-editor >/dev/null 2>&1; then
  ok "auto-editor $(auto-editor --version 2>/dev/null)"
else
  bad "auto-editor not found" "brew install auto-editor"
fi

if [ -n "$WHISPER_MODEL" ] && [ -f "$WHISPER_MODEL" ]; then
  ok "WHISPER_MODEL=$WHISPER_MODEL"
elif [ -n "$WHISPER_MODEL" ]; then
  bad "WHISPER_MODEL points to a missing file: $WHISPER_MODEL" "Download a ggml model (see CLAUDE.md > Environment)."
else
  warn "WHISPER_MODEL is unset" \
    "Transcription falls back to the macOS 'apple' backend, which drops English fillers (um, uh). See CLAUDE.md > Environment."
fi

if command -v fc-list >/dev/null 2>&1; then
  ko_fonts="$(fc-list :lang=ko family 2>/dev/null | grep -v '^\.' | head -3 | tr '\n' ';')"
  if [ -n "$ko_fonts" ]; then
    ok "Korean fonts for subtitles: $ko_fonts"
  else
    warn "no Korean font visible to fontconfig" "Burned-in Korean subtitles will render as boxes. Install e.g. Noto Sans CJK KR."
  fi
fi

exit "$fail"
