#!/usr/bin/env python3
"""Shift every cue in an SRT file by a fixed offset (seconds, may be negative).

ffmpeg's -itsoffset only delays subtitles; a negative value or -ss leaves the
times unchanged. Cues pushed entirely before 0 are dropped; cues that straddle
0 are clipped to start at 0.

    python3 srt_shift.py in.srt out.srt -0.5     # subtitles appear 0.5 s earlier
    python3 srt_shift.py in.srt out.srt 1.2      # 1.2 s later
"""
import re
import sys

TIME = re.compile(r"(\d+):(\d{2}):(\d{2})[,.](\d{3})")


def to_sec(m):
    h, mi, s, ms = (int(g) for g in m.groups())
    return h * 3600 + mi * 60 + s + ms / 1000


def fmt(t):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    src, dst, offset = sys.argv[1], sys.argv[2], float(sys.argv[3])
    blocks = re.split(r"\n\s*\n", open(src, encoding="utf-8-sig").read().strip())
    out = []
    for block in blocks:
        lines = block.splitlines()
        idx = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if idx is None:
            continue
        times = list(TIME.finditer(lines[idx]))
        if len(times) != 2:
            continue
        start, end = (to_sec(m) + offset for m in times)
        if end <= 0:
            continue
        out.append(f"{len(out) + 1}\n{fmt(max(start, 0))} --> {fmt(end)}\n" + "\n".join(lines[idx + 1:]))
    open(dst, "w", encoding="utf-8").write("\n\n".join(out) + "\n")
    print(f"{len(out)} cues written, shifted {offset:+.3f}s")


if __name__ == "__main__":
    main()
