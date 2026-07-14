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
