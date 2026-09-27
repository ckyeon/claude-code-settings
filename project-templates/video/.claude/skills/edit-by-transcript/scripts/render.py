#!/usr/bin/env python3
"""Render an EDL: per-range extract, lossless concat, overlays, subtitles last, loudness.

    python3 render.py edit/edl.json -o edit/preview.mp4 --preview
    python3 render.py edit/edl.json -o edit/final.mp4 --subtitles

Run from the project root; every path in the EDL is relative to it (or absolute).

Pipeline (each step exists to avoid a failure seen in production edits):
  1. Every range is extracted and re-encoded to one uniform spec, cut to whole
     frames, with 30 ms audio fades at both edges (hard cuts pop). Audio stays
     PCM until the last step: AAC pads each segment by up to ~21 ms, which
     concat turns into a one-frame video gap at every join.
  2. Segments are joined with the concat demuxer and -c copy (no second encode).
  3. Overlays are PTS-shifted so their frame 0 lands at start_in_output.
  4. Subtitles are burned last, so no overlay covers them. With --subtitles the
     SRT is built from the word transcripts on the OUTPUT timeline.
  5. Two-pass loudnorm via ffmpeg-recipes/scripts/loudnorm.py (skipped in --preview),
     which is also where the audio is encoded to AAC, once.
"""
import argparse
import json
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

FADE = 0.03
LOUDNORM = Path(__file__).resolve().parents[2] / "ffmpeg-recipes" / "scripts" / "loudnorm.py"
DEFAULT_FONT = "Apple SD Gothic Neo" if platform.system() == "Darwin" else "Noto Sans CJK KR"
SUB_STYLE = ("FontName={font},FontSize=20,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
             "BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=40")


def run(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{proc.stderr[-3000:]}")
    return proc


def probe(path):
    out = run(["ffprobe", "-v", "error", "-show_entries",
               "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", path]).stdout
    data = json.loads(out)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    has_audio = any(s["codec_type"] == "audio" for s in data["streams"])
    fps = None
    if v and v.get("r_frame_rate", "0/0") != "0/0":
        n, d = v["r_frame_rate"].split("/")
        fps = round(int(n) / int(d), 3)
    return {"duration": float(data["format"]["duration"]), "width": v and v["width"],
            "height": v and v["height"], "fps": fps, "audio": has_audio}


def even(x):
    return int(round(x / 2)) * 2


def extract(i, rng, src, info, spec, user_filter, clips):
    start, end = float(rng["start"]), float(rng["end"])
    end = min(end, info["duration"])
    # Whole frames only: a 2.95 s range at 30 fps holds 88 frames (2.933 s) of
    # video but 2.95 s of audio, and concat then leaves a one-frame gap at the join.
    dur = int((end - start) * spec["fps"]) / spec["fps"]
    if dur <= 2 * FADE:
        sys.exit(f"range {i} is too short ({dur:.3f}s): {rng}")
    w, h, fps = spec["width"], spec["height"], spec["fps"]
    vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},format=yuv420p"
    if user_filter:  # the EDL's "filter": a grade, a crop, anything applied to every range
        vf = f"{user_filter},{vf}"
    # After a seek the first source frame can sit a fraction of a frame past 0
    # (a 25 fps source seeked to 0.5 s starts at 0.52 s); fps would then drop
    # output frame 0 and leave a gap at the join.
    vf = f"setpts=PTS-STARTPTS,{vf}"
    af = (f"aformat=sample_rates=48000:channel_layouts=stereo,"
          f"afade=t=in:st=0:d={FADE},afade=t=out:st={dur - FADE:.3f}:d={FADE}")
    out = clips / f"seg_{i:03d}.mkv"
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-i", src]
    if info["audio"]:
        amap = "0:a:0"
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        amap = "1:a"
    cmd += ["-t", f"{dur:.6f}", "-map", "0:v:0", "-map", amap, "-vf", vf, "-af", af,
            "-c:v", "libx264", "-preset", spec["preset"], "-crf", str(spec["crf"]),
            "-c:a", "pcm_s16le", "-shortest", str(out)]
    run(cmd)
    return out, dur


def load_words(path):
    words = []
    for line in path.read_text().splitlines():
        if line.strip():
            w = json.loads(line)
            words.append((w["start"] / 1000, w["end"] / 1000, w["text"]))
    return words


def srt_time(t):
    ms = max(0, round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def norm(text):
    return re.sub(r"[\W_]+", "", text.lower())


def pick_words(words, rng, start, end, i):
    """The transcript words a range keeps.

    ASR times drift by up to a few hundred ms, so a word next to a cut can sit
    on the wrong side of the edge. When the range has a quote copied from the
    transcript, match it against the words near the range instead of trusting
    the times.
    """
    quote = rng.get("quote")
    if quote:
        target = norm(quote)
        near = [w for w in words if w[1] > start - 0.5 and w[0] < end + 0.5]
        for a in range(len(near)):
            acc = ""
            for b in range(a, len(near)):
                acc += norm(near[b][2])
                if acc == target:
                    return near[a:b + 1]
                if not target.startswith(acc):
                    break
        print(f"warn: range {i} quote not found in transcript words; subtitles fall back to word times")
    return [w for w in words if start <= (w[0] + w[1]) / 2 < end]


def build_srt(edl, durations, edit_dir, out, max_words, max_chars):
    """Kept words re-timed onto the output: word.start - range.start + range offset, clamped to the range."""
    cues, offset = [], 0.0
    for i, (rng, dur) in enumerate(zip(edl["ranges"], durations)):
        src = Path(edl["sources"][rng["source"]])
        tf = edit_dir / "transcripts" / f"{src.stem}.json"
        if not tf.exists():
            sys.exit(f"--subtitles needs {tf}; run transcribe.py on {src}")
        start = float(rng["start"])
        clamp = lambda t: min(max(t, start), start + dur) - start + offset
        words = [(clamp(ws), clamp(we), t) for ws, we, t in pick_words(load_words(tf), rng, start, start + dur, i)]
        chunk = []
        for w in words:
            text = " ".join(x[2] for x in chunk + [w])
            gap = chunk and w[0] - chunk[-1][1] > 0.35
            if chunk and (len(chunk) >= max_words or len(text) > max_chars or gap):
                cues.append(chunk)
                chunk = []
            chunk.append(w)
            if w[2].endswith((".", "?", "!", "。")):
                cues.append(chunk)
                chunk = []
        if chunk:
            cues.append(chunk)
        offset += dur
    lines = []
    for n, c in enumerate(cues):
        end = max(c[-1][1], c[0][0] + 0.35)  # a cue shorter than ~0.35 s flashes by unread
        if n + 1 < len(cues):
            end = min(end, cues[n + 1][0][0])
        lines.append(f"{n + 1}\n{srt_time(c[0][0])} --> {srt_time(end)}\n{' '.join(x[2] for x in c)}\n")
    out.write_text("\n".join(lines))
    return len(cues)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edl")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--preview", action="store_true", help="720p, fast encode, no loudnorm")
    ap.add_argument("--subtitles", action="store_true", help="build <edit-dir>/master.srt from transcripts and burn it")
    ap.add_argument("--font", default=DEFAULT_FONT)
    ap.add_argument("--sub-style", help="full ASS force_style string (overrides the default and --font)")
    ap.add_argument("--sub-max-words", type=int, default=4)
    ap.add_argument("--sub-max-chars", type=int, default=20)
    ap.add_argument("--no-loudnorm", action="store_true")
    ap.add_argument("--edit-dir", default="edit")
    args = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)  # keep our lines ordered with loudnorm.py's output

    edit_dir = Path(args.edit_dir)
    edl_path = Path(args.edl)
    edl = json.loads(edl_path.read_text())
    clips = edit_dir / "clips"
    if clips.exists():
        shutil.rmtree(clips)
    clips.mkdir(parents=True)

    infos = {k: probe(v) for k, v in edl["sources"].items()}
    first = infos[edl["ranges"][0]["source"]]
    o = edl.get("output", {})
    spec = {"width": o.get("width", first["width"]), "height": o.get("height", first["height"]),
            "fps": o.get("fps", first["fps"] or 30), "preset": "medium", "crf": 18}
    if args.preview:
        scale = min(1.0, 720 / spec["height"])
        spec.update(width=even(spec["width"] * scale), height=even(spec["height"] * scale), preset="veryfast", crf=28)

    segs, durs = [], []
    for i, rng in enumerate(edl["ranges"]):
        seg, dur = extract(i, rng, edl["sources"][rng["source"]], infos[rng["source"]], spec, edl.get("filter"), clips)
        segs.append(seg)
        durs.append(dur)
        print(f"segment {i:03d}  {rng['source']} {float(rng['start']):.2f}-{float(rng['start']) + dur:.2f}  ({dur:.2f}s)")

    listing = clips / "concat.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in segs))
    base = clips / "base.mkv"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(base)])

    subs = None
    if args.subtitles:
        subs = edit_dir / "master.srt"
        n = build_srt(edl, durs, edit_dir, subs, args.sub_max_words, args.sub_max_chars)
        print(f"subtitles {subs}  ({n} cues)")
    elif edl.get("subtitles"):
        subs = Path(edl["subtitles"])

    overlays = edl.get("overlays", [])
    composite = clips / "composite.mkv"
    if overlays or subs:
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(base)]
        chain, cur = [], "[0:v]"
        for k, ov in enumerate(overlays, start=1):
            if ov["file"].lower().endswith(".webm"):
                # ffmpeg's native VP9 decoder drops the alpha channel; libvpx keeps it
                cmd += ["-c:v", "libvpx-vp9"]
            cmd += ["-i", ov["file"]]
            t, d = float(ov["start_in_output"]), float(ov["duration"])
            chain.append(f"[{k}:v]setpts=PTS-STARTPTS+{t}/TB[o{k}]")
            chain.append(f"{cur}[o{k}]overlay=enable='between(t,{t},{t + d})':eof_action=pass[v{k}]")
            cur = f"[v{k}]"
        if subs:
            style = args.sub_style or SUB_STYLE.format(font=args.font)
            chain.append(f"{cur}subtitles={subs}:force_style='{style}'[vout]")
            cur = "[vout]"
        cmd += ["-filter_complex", ";".join(chain), "-map", cur, "-map", "0:a",
                "-c:v", "libx264", "-preset", spec["preset"], "-crf", str(spec["crf"]), "-pix_fmt", "yuv420p",
                "-c:a", "copy", str(composite)]
        run(cmd)
    else:
        shutil.copy(base, composite)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.preview or args.no_loudnorm:
        run(["ffmpeg", "-y", "-v", "error", "-i", str(composite), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-movflags", "+faststart", str(out)])
    else:
        subprocess.run([sys.executable, str(LOUDNORM), str(composite), str(out)], check=True)

    expected = sum(durs)
    actual = probe(str(out))["duration"]
    flag = "ok" if abs(actual - expected) <= 1.5 / spec["fps"] else "CHECK"
    print(f"{flag}  {out}  duration {actual:.2f}s (EDL {expected:.2f}s)  {spec['width']}x{spec['height']}@{spec['fps']}")


if __name__ == "__main__":
    main()
