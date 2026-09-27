#!/usr/bin/env python3
"""Filmstrip + waveform PNG of one time window, for looking at a decision point.

    python3 timeline_view.py edit/preview.mp4 3.5 6.5 --mark 5.06
    python3 timeline_view.py footage/take1.mp4 12 18 --frames 10 -o edit/verify/take1_12.png

Top row: N evenly spaced frames, each labelled with its absolute timestamp.
Bottom row: the audio waveform of the same window. --mark draws a red line at
that absolute time (for example a cut point in the rendered output), so a
spike or a visual jump at the boundary is easy to spot. It also prints the
short measured silences in the window: ASR word times drift, so put an
in-phrase cut edge inside one of these. ffmpeg only.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TILE_W = 200


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("start", type=float)
    ap.add_argument("end", type=float)
    ap.add_argument("--frames", type=int, default=8)
    ap.add_argument("--mark", type=float, action="append", default=[], help="absolute time to mark; repeatable")
    ap.add_argument("--noise", default="-35dB", help="silencedetect threshold (default -35dB)")
    ap.add_argument("--min-silence", type=float, default=0.05, help="shortest silence to list, s (default 0.05)")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    dur = args.end - args.start
    if dur <= 0:
        sys.exit("end must be after start")
    streams = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "json", args.video],
        capture_output=True, text=True).stdout)["streams"]
    has_audio = any(s["codec_type"] == "audio" for s in streams)

    n, width = args.frames, TILE_W * args.frames
    label = f"drawtext=text='%{{pts\\:hms\\:{args.start}}}':fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6:x=4:y=4"
    graph = f"[0:v]fps={n}/{dur},scale={TILE_W}:-2,{label},tile={n}x1,format=rgb24[strip]"
    if has_audio:
        marks = "".join(
            f",drawbox=x={int((m - args.start) / dur * width)}:y=0:w=2:h=160:color=red:t=fill"
            for m in args.mark if args.start <= m <= args.end)
        graph += (f";[0:a]showwavespic=s={width}x160:split_channels=0:colors=0x55ccff,format=rgb24{marks}[wave]"
                  f";[strip][wave]vstack[out]")
    else:
        graph += ";[strip]null[out]"

    out = Path(args.output or f"edit/verify/{Path(args.video).stem}_{args.start:.2f}-{args.end:.2f}.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", str(args.start), "-t", str(dur), "-i", args.video,
         "-filter_complex", graph, "-map", "[out]", "-frames:v", "1", str(out)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(proc.stderr[-2000:])
    print(out)
    if has_audio:
        print(f"silences >= {args.min_silence}s at {args.noise}: " + (", ".join(silences(args)) or "none"))


def silences(args):
    """Short measured silences in the window, in absolute time: where an in-phrase cut edge can go."""
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-ss", str(args.start), "-t", str(args.end - args.start),
         "-i", args.video, "-af", f"silencedetect=n={args.noise}:d={args.min_silence}", "-f", "null", "-"],
        capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", proc.stderr)]
    ends += [args.end - args.start] * (len(starts) - len(ends))
    return [f"{max(s, 0) + args.start:.3f}-{e + args.start:.3f}" for s, e in zip(starts, ends)]


if __name__ == "__main__":
    main()
