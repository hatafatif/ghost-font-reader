"""MCP server exposing the ghost-font decoder as a tool.

An agent whose user says "read this ghost-font video" calls `decode_ghost_font`
with the local path to the video. The server does the motion-based decode (which
an LLM cannot do by itself) and returns a clean image of the message, which the
vision-capable agent then simply reads back to its user.

Run standalone (stdio transport):
    python server.py
"""
from pathlib import Path

import cv2
from mcp.server.fastmcp import FastMCP

from ghostreader import decode_message

mcp = FastMCP("ghost-font-reader")

VIDEO_SUFFIXES = {".webm", ".mp4", ".mov", ".mkv", ".avi", ".m4v"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}


@mcp.tool()
def decode_ghost_font(video_path: str, max_shift: int = 40) -> str:
    """Decode a mixfont "ghost font" video into a readable image on disk.

    A ghost-font video hides a text message in a field of random dots: every
    single frame looks like noise, and the message is revealed only by motion
    across frames. This tool performs that motion-based decode and writes the
    result — the message rendered in white on black — to an image file, then
    returns the path to that file.

    To answer the user, OPEN the saved image file yourself and read the message
    text in it, then reply with the text. Do NOT surface the image to the user
    unless you cannot read images, in which case give the user the file path so
    they can open it.

    Args:
        video_path: Local filesystem path to the ghost-font VIDEO (e.g. a .webm
            or .mp4). A still image cannot be decoded — the message only exists
            in the motion between frames.
        max_shift: Largest per-frame scroll to search for, in pixels (default 40).

    Returns:
        A status note containing the path to the decoded image file.
    """
    path = Path(video_path).expanduser()

    if not path.exists():
        return f"Error: no file found at '{video_path}'. Provide a local path to the ghost-font video."
    if path.suffix.lower() in IMAGE_SUFFIXES:
        return (
            f"Error: '{path.name}' is a still image, which cannot be decoded. "
            "Ghost-font messages exist only in the motion between video frames — "
            "provide the source VIDEO (e.g. .webm or .mp4) instead."
        )
    if path.suffix.lower() not in VIDEO_SUFFIXES:
        return (
            f"Error: '{path.name}' does not look like a supported video "
            f"({', '.join(sorted(VIDEO_SUFFIXES))}). Provide the ghost-font video file."
        )

    try:
        reveal, dy, score = decode_message(str(path), max_shift=max_shift)
    except Exception as exc:  # decode/read failure -> report to the agent
        return f"Error decoding '{path.name}': {exc}"

    # Persist the decoded image to disk instead of returning it inline. Returning
    # an inline image block would make MCP clients render it into the user's view;
    # writing a file keeps the image out of sight until it is actually needed.
    saved = path.with_name(f"{path.stem}_decoded.png")
    try:
        if not cv2.imwrite(str(saved), reveal):
            raise OSError("cv2.imwrite returned False")
    except OSError as exc:
        return f"Error: decoded '{path.name}' but could not write the image file: {exc}"

    return (
        f"Decoded '{path.name}': detected {dy}px/frame scroll "
        f"(match score {score:.2f}, lower is better). "
        f"The message image was written to: {saved.resolve()}\n\n"
        "To answer the user: open that image file and read the message text in it "
        "(it is rendered in white on black), then reply with the text. Do not show the "
        "image to the user unless you are unable to read it yourself — in that case, give "
        "the user the file path above so they can open it."
    )


if __name__ == "__main__":
    mcp.run()
