# ghost-font-reader

Decode [mixfont "ghost font"](https://www.mixfont.com/ghost-font) videos into readable images.

A ghost-font video hides a text message inside a field of random dots. Any single
frame looks like pure noise — the message is invisible in a still image. But the
whole dot field **scrolls rigidly by a fixed vertical offset every frame**, while
the letters stay put. Re-aligning one frame onto the next cancels the scrolling
background and leaves the stationary letters behind, spelling out the message.

| Single frame (noise) | Decoded output |
| --- | --- |
| unreadable random dots | the message, white on black |

## How it works

1. Read the first two frames of the video.
2. Search for the vertical shift `dy` that best re-aligns frame 0 onto frame 1
   (mean-absolute-difference over the top strip of the image — a sharp minimum
   marks the true scroll amount).
3. Shift frame 0 down by `dy` and take the absolute difference with frame 1.
   The background cancels to black; the letters remain.

## Setup

Requires Python 3 and the packages in `requirements.txt` (OpenCV + NumPy).

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# decode a video -> writes output/<video-name>.png
python main.py inputs/message1.webm

# choose your own output path
python main.py inputs/message2.webm -o output/msg2.png

# widen the scroll search if a video scrolls more than 40px/frame
python main.py inputs/message2.webm --max-shift 60

# help
python main.py -h
```

It prints the detected scroll and where the image was written:

```
scroll detected: 11px/frame (match score 2.03, lower is better)
decoded image written to: output/message1.png
```

Open the PNG to read the message.

## Use as a library

```python
from ghostreader import decode_message

reveal, dy, score = decode_message("inputs/message1.webm")
# reveal: uint8 image (message in white on black)
# dy:     detected per-frame scroll in pixels
# score:  alignment match score (lower = more confident)
```

## Use as an MCP server

The repo ships an [MCP](https://modelcontextprotocol.io) server (`server.py`) so any
MCP-capable agent can decode ghost-font videos on request. It exposes one tool:

- **`decode_ghost_font(video_path, max_shift=40)`** — decodes the video at
  `video_path` (a local file), writes the message image to `<video>_decoded.png`,
  and returns a text note with that file path.

The tool deliberately does **not** return the image inline (which MCP clients
would render straight into the user's view). Instead it saves the image and tells
the agent to open that file itself, read the message, and reply with just the
text. The decoded image stays out of the user's sight unless it's necessary — i.e.
the agent can't read images, in which case it hands the user the file path to open.

The server does not bundle an OCR/vision model. It does the motion-based decode
the LLM can't do, and leaves reading the (now legible) text to the agent.

### Install in Claude Code

```bash
claude mcp add ghost-font -- /abs/path/to/ghost-font-reader/venv/bin/python \
  /abs/path/to/ghost-font-reader/server.py
```

### Install in Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ghost-font": {
      "command": "/abs/path/to/ghost-font-reader/venv/bin/python",
      "args": ["/abs/path/to/ghost-font-reader/server.py"]
    }
  }
}
```

Use absolute paths, and point `command` at the venv's Python so `cv2`, `numpy`,
and `mcp` are available. Then just ask your agent to "read this ghost-font video"
and give it the path.

## Project layout

```
ghost-font-reader/
├── ghostreader/          # the module
│   ├── __init__.py       # exports decode_message, find_vertical_shift, read_frames
│   └── decoder.py        # core align-and-subtract logic
├── main.py               # CLI entry point
├── requirements.txt
├── inputs/               # source videos
└── output/               # decoded images (gitignored)
```
