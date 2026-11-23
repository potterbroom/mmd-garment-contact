"""Measure consecutive, Y-up world-space root/tip samples from one garment chain."""
import argparse
import csv
import math
from pathlib import Path


def summarize(path, fps):
    speeds = []
    below = frames = 0
    previous = None
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            frame = int(row["frame"])
            offset = tuple(float(row["tip_" + a]) - float(row["root_" + a]) for a in "xyz")
            if not all(map(math.isfinite, offset)):
                raise ValueError(f"non-finite position at frame {frame}")
            if previous:
                if frame != previous[0] + 1:
                    raise ValueError(f"expected consecutive frames at {frame}")
                speeds.append(math.dist(offset, previous[1]) * fps)
            below += offset[1] < 0
            frames += 1
            previous = frame, offset
    if not speeds:
        raise ValueError("at least two consecutive frames required")
    speeds.sort()
    return speeds[math.ceil(0.95 * len(speeds)) - 1], below / frames


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--fps", required=True, type=float)
    args = parser.parse_args()
    if not math.isfinite(args.fps) or args.fps <= 0:
        parser.error("--fps must be finite and positive")
    try:
        speed, fraction = summarize(args.csv, args.fps)
    except (ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))
    print(f"Relative tip speed p95: {speed:.3f} units/s")
    print(f"Tip below root: {fraction:.1%} of frames")
