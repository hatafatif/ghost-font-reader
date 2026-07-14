"""Decode mixfont ghost-font messages from a video.

A ghost-font video hides text inside a field of random dots. Any single frame
looks like pure noise, but the whole field scrolls rigidly by a fixed vertical
offset every frame while the letters stay put. Re-aligning one frame onto the
next cancels the scrolling background and leaves the stationary letters behind.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def read_frames(video_path, count: int = 2):
    """Read the first `count` frames of a video as BGR arrays."""
    cap = cv2.VideoCapture(str(video_path))
    frames = []
    try:
        for _ in range(count):
            ok, frame = cap.read()
            if not ok:
                break
            frames.append(frame)
    finally:
        cap.release()
    if len(frames) < count:
        raise ValueError(
            f"needed {count} frames but only read {len(frames)} from {video_path}"
        )
    return frames


def find_vertical_shift(a, b, max_shift: int = 40, strip: int = 120):
    """Find how far `a` scrolled down to become `b`.

    Compares the top `strip` rows of `a` against the same rows of `b` at each
    candidate downward offset, scoring with mean absolute difference (0 = exact
    match). Returns ``(dy, score)`` for the best-matching offset.
    """
    best_dy, best_score = 0, float("inf")
    for dy in range(max_shift + 1):
        score = float(np.abs(a[:strip] - b[dy:dy + strip]).mean())
        if score < best_score:
            best_dy, best_score = dy, score
    return best_dy, best_score


def decode_message(video_path, max_shift: int = 40):
    """Decode a ghost-font video into a readable grayscale image.

    Returns ``(reveal, dy, score)`` where `reveal` is a uint8 image with the
    message in white on black, `dy` is the detected per-frame scroll in pixels,
    and `score` is the alignment match score (lower = more confident).
    """
    f0, f1 = read_frames(video_path, 2)
    g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY).astype(np.float32)
    g1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY).astype(np.float32)

    dy, score = find_vertical_shift(g0, g1, max_shift=max_shift)

    h, w = g0.shape
    translate = np.float32([[1, 0, 0], [0, 1, dy]])
    shifted = cv2.warpAffine(
        g0, translate, (w, h),
        borderMode=cv2.BORDER_CONSTANT, borderValue=255,
    )
    reveal = cv2.absdiff(shifted, g1).astype(np.uint8)
    return reveal, dy, score
