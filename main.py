"""CLI: decode a mixfont ghost-font video into a readable image.

Usage:
    python main.py inputs/message1.webm
    python main.py inputs/message2.webm -o output/msg2.png
"""
import argparse
from pathlib import Path

import cv2

from ghostreader import decode_message


def main():
    parser = argparse.ArgumentParser(
        description="Decode a mixfont ghost-font video into a readable image."
    )
    parser.add_argument(
        "video", type=Path,
        help="path to the ghost-font video (e.g. inputs/message1.webm)",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="output image path (default: output/<video-stem>.png)",
    )
    parser.add_argument(
        "--max-shift", type=int, default=40,
        help="maximum per-frame scroll to search for, in pixels (default: 40)",
    )
    args = parser.parse_args()

    if not args.video.exists():
        parser.error(f"video not found: {args.video}")

    output = args.output or Path("output") / f"{args.video.stem}.png"
    output.parent.mkdir(parents=True, exist_ok=True)

    reveal, dy, score = decode_message(args.video, max_shift=args.max_shift)
    cv2.imwrite(str(output), reveal)

    print(f"scroll detected: {dy}px/frame (match score {score:.2f}, lower is better)")
    print(f"decoded image written to: {output}")


if __name__ == "__main__":
    main()
