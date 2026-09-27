#!/usr/bin/env python3
"""Pack word-level transcripts into one phrase-level reading view.

Reads <edit-dir>/transcripts/*.json (from transcribe.py), measures each
source's silences with ffmpeg silencedetect (cached in <edit-dir>/silences/),
and writes <edit-dir>/takes_packed.md:

    ## talk  (43.00s, 8 phrases)  source: /abs/talk.mp4
      [002.52-005.36] Ninety percent of what a web agent does is wasted.
      ~ silence 005.41-006.02 (0.61s)
      [006.08-006.74] We fixed this.

Phrase times come from the ASR and drift (measured up to ~0.5 s with the apple
backend, ~0.2 s with whisper-small). Silence lines come from the audio itself;
put cut edges inside them.

    python3 pack.py
    python3 pack.py --noise -30dB --min-silence 0.3
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def load_words(path):
    words = []
    for line in path.read_text().splitlines():
        if line.strip():
            w = json.loads(line)
            words.append({"start": w["start"] / 1000, "end": w["end"] / 1000, "text": w["text"]})
    return words


def silences(src, cache, noise, min_len):
    key = {"source": src, "noise": noise, "min": min_len, "mtime": int(Path(src).stat().st_mtime)}
    if cache.exists():
        data = json.loads(cache.read_text())
        if data.get("key") == key:
            return data["silences"], data["duration"]
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-af", f"silencedetect=n={noise}:d={min_len}", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", proc.stderr)]
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
        capture_output=True, text=True,
    ).stdout.strip()
    duration = float(dur) if dur else 0.0
    if len(ends) < len(starts):  # silence runs to the end of the file
        ends.append(duration)
    spans = [[round(max(s, 0), 3), round(e, 3)] for s, e in zip(starts, ends)]
    cache.write_text(json.dumps({"key": key, "silences": spans, "duration": duration}))
    return spans, duration


def phrases(words, spans, max_gap):
    """Split before a word when the ASR gap is long or a measured silence sits between the two words."""
    out, cur = [], []
    for w in words:
        if cur:
            prev = cur[-1]
            pm, wm = (prev["start"] + prev["end"]) / 2, (w["start"] + w["end"]) / 2
            split = w["start"] - prev["end"] >= max_gap or any(pm <= (s + e) / 2 <= wm for s, e in spans)
            if split:
                out.append(cur)
                cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def fmt(t):
    return f"{t:06.2f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--edit-dir", default="edit")
    ap.add_argument("--noise", default="-35dB", help="silencedetect threshold (default -35dB)")
    ap.add_argument("--min-silence", type=float, default=0.4, help="shortest silence to report, s (default 0.4)")
    ap.add_argument("--max-gap", type=float, default=0.5, help="ASR word gap that also splits a phrase, s")
    args = ap.parse_args()

    edit = Path(args.edit_dir)
    tdir, sdir = edit / "transcripts", edit / "silences"
    sdir.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in tdir.glob("*.json") if not p.name.endswith(".meta.json"))
    if not files:
        sys.exit(f"no transcripts in {tdir}; run transcribe.py first")

    lines = ["# takes_packed", "",
             "Phrase times are ASR estimates. Silence lines are measured from the audio: put cut edges inside them.", ""]
    for tf in files:
        meta = json.loads((tdir / f"{tf.stem}.meta.json").read_text())
        spans, duration = silences(meta["source"], sdir / f"{tf.stem}.json", args.noise, args.min_silence)
        groups = phrases(load_words(tf), spans, args.max_gap)
        lines.append(f"## {tf.stem}  ({duration:.2f}s, {len(groups)} phrases)  source: {meta['source']}  "
                     f"model: {Path(meta['model']).name}  lang: {meta['lang']}")
        # interleave phrases and the silences that fall outside any phrase
        events = [(g[0]["start"], "p", g) for g in groups]
        for s, e in spans:
            inside = any(g[0]["start"] < (s + e) / 2 < g[-1]["end"] for g in groups)
            if not inside:
                events.append((s, "s", (s, e)))
        for _, kind, item in sorted(events, key=lambda x: (x[0], x[1])):
            if kind == "p":
                text = " ".join(w["text"] for w in item)
                lines.append(f"  [{fmt(item[0]['start'])}-{fmt(item[-1]['end'])}] {text}")
            else:
                s, e = item
                lines.append(f"  ~ silence {fmt(s)}-{fmt(e)} ({e - s:.2f}s)")
        lines.append("")
    out = edit / "takes_packed.md"
    out.write_text("\n".join(lines))
    print(f"wrote {out}  ({len(files)} sources)")


if __name__ == "__main__":
    main()
