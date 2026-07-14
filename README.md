# ghost-font-reader

Decode [mixfont "ghost font"](https://www.mixfont.com/ghost-font) videos into
readable text. A ghost-font video hides a message in a field of random dots —
every still frame is pure noise; the message only appears through motion. This
tool recovers it.

Primary use is as an **MCP server**: install it, then ask your agent to read a
ghost-font video and it answers with the message.

## Quick start

**1. Clone the repo:**

```bash
git clone https://github.com/hatafatif/ghost-font-reader.git
cd ghost-font-reader
```

**2. Open it in Claude Code and say:**

> Read SETUP.md and set this up for me.

Your agent will walk you through it — creating the venv, installing requirements,
and registering the MCP server, telling you what it's doing at each step. When
it's finished it asks you to open a new session and hand it a ghost-font video,
which it decodes and answers in text. You don't install anything yourself.

---

<details>
<summary>Manual setup (if you'd rather not use an agent)</summary>

**Claude Code**
```bash
python -m venv venv && venv/bin/pip install -r requirements.txt

claude mcp add ghost-font -- /abs/path/to/ghost-font-reader/venv/bin/python \
  /abs/path/to/ghost-font-reader/server.py
```

**Claude Desktop** — add to `claude_desktop_config.json`, then restart:
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

Use absolute paths, and point `command` at the venv's Python (that's where
`cv2`, `numpy`, and `mcp` live). Then just ask:

> Read this ghost-font video: /path/to/message.webm

The agent decodes it, reads the result, and replies with the text.

</details>

### How the MCP tool behaves

One tool, **`decode_ghost_font(video_path, max_shift=40)`**. It decodes the local
video, writes the message image to `<video>_decoded.png`, and returns a text note
with that path — **not** an inline image. So the noisy decoded picture never lands
in the user's view: the agent opens the file itself, reads the message, and
replies with just the text. Only if the agent can't read images does it fall back
to handing the user the file path. No OCR/vision model is bundled — the server
does the motion-based decode the LLM can't, and lets the agent read the result.

## CLI

```bash
python main.py inputs/message1.webm          # -> output/message1.png
python main.py inputs/message2.webm -o out.png
python main.py inputs/message2.webm --max-shift 60   # widen scroll search
```

Prints the detected scroll and output path; open the PNG to read the message.

## Library

```python
from ghostreader import decode_message

reveal, dy, score = decode_message("inputs/message1.webm")
# reveal: uint8 image (message in white on black)
# dy:     detected per-frame scroll in pixels
# score:  alignment match score (lower = more confident)
```

## How it works

The whole dot field scrolls rigidly by a fixed vertical offset every frame while
the letters stay put. So:

1. Read the first two frames.
2. Find the vertical shift `dy` that best re-aligns frame 0 onto frame 1
   (mean-absolute-difference over the top strip — a sharp minimum marks the true
   scroll).
3. Shift frame 0 down by `dy` and take the absolute difference with frame 1. The
   scrolling background cancels to black; the stationary letters remain.

## Project layout

```
ghost-font-reader/
├── server.py             # MCP server (primary entry point)
├── main.py               # CLI entry point
├── ghostreader/          # core module
│   ├── __init__.py       # exports decode_message, find_vertical_shift, read_frames
│   └── decoder.py        # align-and-subtract logic
├── requirements.txt
├── inputs/               # source videos
└── output/               # decoded images (gitignored)
```
