# SETUP.md — instructions for the agent

You are an AI agent (e.g. Claude Code) setting up **ghost-font-reader** on the
user's behalf, so the user does not have to run any setup commands themselves.

When the user asks you to set this project up (or points you at this file),
follow the steps below in order.

## Step 0 — Announce the plan

Before running anything, tell the user in plain language what you are about to
do. Say something equivalent to:

> I'm going to set up ghost-font-reader for you in three steps:
> 1. Create a Python virtual environment and install the requirements.
> 2. Register the ghost-font decoder as an MCP server in Claude Code.
> 3. Once that's done, I'll ask you to open a **new** Claude session and give it
>    the ghost-font video to decode.
>
> You won't need to install anything yourself. Ready?

Proceed once the user agrees.

## Step 1 — Create the venv and install requirements

Run from the repository root (use the repo's own absolute path — get it with
`pwd`; do not hardcode the example paths below):

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

Verify the core imports succeed:

```bash
venv/bin/python -c "import cv2, numpy, mcp; print('deps ok')"
```

If venv creation fails because the platform lacks `venv`, tell the user which
system package to install (e.g. `python3-venv`) and stop — do not silently switch
to a system-wide install.

## Step 2 — Register the MCP server

Register the server with Claude Code, pointing at the **venv's** Python (that's
where `cv2`, `numpy`, and `mcp` live) and using **absolute paths**:

```bash
claude mcp add ghost-font -- "$(pwd)/venv/bin/python" "$(pwd)/server.py"
```

Add `--scope user` if the user wants it available in every project rather than
just this one.

Confirm it registered and is healthy:

```bash
claude mcp list
```

You should see `ghost-font` marked `✔ Connected`. If it shows as failed, check
that both paths are absolute and that Step 1's import check passed.

## Step 3 — Hand off to a new session

The MCP tool (`decode_ghost_font`) is loaded when a Claude session **starts**, so
it will not be available in the current session where you just registered it.
Tell the user:

> Setup is done. Please open a **new** Claude Code session in this project, then
> give it the path to your ghost-font video, e.g.:
>
> > Read this ghost-font video: /path/to/message.webm
>
> The new session will decode it and reply with the message text.

Do not attempt to call `decode_ghost_font` yourself in the current session — it
won't be there yet. Your job ends at a successful `claude mcp list`.

## Notes

- The tool takes a **video** (`.webm`/`.mp4`), not a still image — the message
  exists only in the motion between frames.
- The decoded image is written to `<video>_decoded.png` next to the input; the
  agent that decodes reads it and answers with text, so the user isn't shown the
  raw image unless it's needed.
