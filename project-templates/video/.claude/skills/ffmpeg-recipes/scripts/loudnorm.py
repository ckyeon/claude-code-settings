#!/usr/bin/env python3
"""Two-pass EBU R128 loudness normalization with ffmpeg's loudnorm filter.

Pass 1 measures the input; pass 2 feeds those measurements back so loudnorm
can apply a linear gain instead of dynamic compression. Video is stream-copied.

    python3 loudnorm.py in.mp4 out.mp4                # -14 LUFS, -1.5 dBTP
    python3 loudnorm.py in.mp4 out.mp4 --i -23 --tp -2
    python3 loudnorm.py in.mp4 --measure              # print loudness, write nothing
"""
import argparse
import json
import re
import subprocess
import sys


def measure(src, i, tp, lra):
    af = f"loudnorm=I={i}:TP={tp}:LRA={lra}:print_format=json"
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-af", af, "-f", "null", "-"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.exit(proc.stderr[-2000:])
    # loudnorm prints its JSON block last on stderr
    blocks = re.findall(r"\{[^{}]*\}", proc.stderr)
    if not blocks:
        sys.exit("loudnorm printed no measurement; does the input have an audio stream?")
    return json.loads(blocks[-1])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst", nargs="?")
    ap.add_argument("--i", type=float, default=-14.0, help="integrated loudness target, LUFS (default -14)")
    # -1.5, not -1: aiming at -1 measured -0.84 dBTP after AAC encoding (lossy
    # codecs add inter-sample peaks), while -1.5 measured -1.49
    ap.add_argument("--tp", type=float, default=-1.5, help="true-peak ceiling, dBTP (default -1.5)")
    ap.add_argument("--lra", type=float, default=11.0, help="loudness range target, LU (default 11)")
    ap.add_argument("--audio-codec", default="aac", help="output audio codec (default aac)")
    ap.add_argument("--audio-bitrate", default="192k")
    ap.add_argument("--measure", action="store_true", help="only print the pass-1 measurement")
    args = ap.parse_args()

    m = measure(args.src, args.i, args.tp, args.lra)
    print(f"input: I={m['input_i']} LUFS  TP={m['input_tp']} dBTP  LRA={m['input_lra']} LU")
    if args.measure:
        return
    if not args.dst:
        ap.error("dst is required unless --measure is given")

    af = (
        f"loudnorm=I={args.i}:TP={args.tp}:LRA={args.lra}"
        f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
        f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
        f":offset={m['target_offset']}:linear=true"
    )
    # loudnorm upsamples to 192 kHz internally; -ar 48000 brings it back down
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", args.src,
        "-map", "0", "-c", "copy", "-af", af,
        "-c:a", args.audio_codec, "-b:a", args.audio_bitrate, "-ar", "48000",
    ]
    if args.dst.lower().endswith((".mp4", ".mov", ".m4a")):
        cmd += ["-movflags", "+faststart"]
    cmd.append(args.dst)
    subprocess.run(cmd, check=True)
    out = measure(args.dst, args.i, args.tp, args.lra)
    print(f"output: I={out['input_i']} LUFS  TP={out['input_tp']} dBTP  LRA={out['input_lra']} LU")


if __name__ == "__main__":
    main()
