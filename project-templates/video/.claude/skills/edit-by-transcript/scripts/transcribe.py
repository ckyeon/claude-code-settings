#!/usr/bin/env python3
"""Word-level transcripts for editing, cached per source.

Runs `auto-editor whisper --split-words --format json` and writes
<edit-dir>/transcripts/<stem>.json (JSON Lines: {"start": ms, "end": ms, "text": word})
plus <stem>.meta.json recording the source, model, and language. A source is
re-transcribed only when its size or mtime, the model, or the language changes.

    python3 transcribe.py footage/*.mp4 --lang ko
    python3 transcribe.py talk.mp4 --lang en --model ~/models/ggml-small.bin
    python3 transcribe.py talk.mp4 --lang ko --model apple      # macOS 26+, no download
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Whisper tends to drop disfluencies unless the prompt already contains them.
# Measured with ggml-small: these kept "um"/"uh" (en) and "음"/"어" (ko).
FILLER_PROMPTS = {
    "ko": "음, 어, 그러니까, 뭐랄까, 이제... 네, 음.",
    "en": "Umm, let me think, uh, like, hmm... So, um, yeah.",
}
APPLE_LOCALES = {"ko": "ko_KR", "en": "en_US", "ja": "ja_JP", "zh": "zh_CN"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--lang", required=True, help="spoken language: ko, en, ... (auto-detect is unreliable)")
    ap.add_argument("--model", default=os.environ.get("WHISPER_MODEL") or "apple",
                    help="ggml model path, or 'apple' (default: $WHISPER_MODEL, else apple)")
    ap.add_argument("--prompt", help="override the filler-preserving prompt (whisper models only)")
    ap.add_argument("--edit-dir", default="edit")
    ap.add_argument("--force", action="store_true", help="ignore the cache")
    args = ap.parse_args()

    apple = args.model == "apple"
    if apple:
        lang = APPLE_LOCALES.get(args.lang, args.lang)
        if args.lang == "en":
            print("warn: the apple backend drops English fillers (um, uh); set WHISPER_MODEL for filler editing",
                  file=sys.stderr)
    else:
        lang = args.lang
        if not Path(args.model).expanduser().is_file():
            sys.exit(f"model not found: {args.model}")
    prompt = None if apple else (args.prompt or FILLER_PROMPTS.get(args.lang))

    out_dir = Path(args.edit_dir) / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)
    seen = {}
    for src in args.sources:
        src_path = Path(src).resolve()
        stem = src_path.stem
        if stem in seen and seen[stem] != src_path:
            sys.exit(f"two sources share the stem '{stem}': {seen[stem]} and {src_path}; rename one")
        seen[stem] = src_path
        st = src_path.stat()
        meta = {"source": str(src_path), "size": st.st_size, "mtime": int(st.st_mtime),
                "model": args.model, "lang": lang, "prompt": prompt}
        out, meta_path = out_dir / f"{stem}.json", out_dir / f"{stem}.meta.json"
        if not args.force and out.exists() and meta_path.exists() and json.loads(meta_path.read_text()) == meta:
            print(f"cached  {out}")
            continue
        cmd = ["auto-editor", "whisper", str(src_path), str(Path(args.model).expanduser()) if not apple else "apple",
               "--language", lang, "--split-words", "--format", "json", "-o", str(out)]
        if prompt:
            cmd += ["--prompt", prompt]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0 or not out.exists():
            sys.exit(f"auto-editor whisper failed for {src}:\n{proc.stderr[-2000:]}")
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1))
        n = sum(1 for line in out.read_text().splitlines() if line.strip())
        print(f"wrote   {out}  ({n} words)")


if __name__ == "__main__":
    main()
