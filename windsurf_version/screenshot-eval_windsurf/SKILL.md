---
name: screenshot-eval
description: >
  Use this skill whenever you want to see the visual output of a running application or program
  to evaluate whether it's working correctly. Triggers when you need to verify UI rendering,
  check that a GUI launched, inspect visual progress of a running process, observe error dialogs,
  or evaluate development output that cannot be seen from terminal logs alone. Use it any time
  the program has a graphical interface and you are unsure whether the result looks right.
  Also triggers when the user says things like "can you check what it looks like", "take a
  screenshot", "see if it's working", or "verify the output visually".
---

# Screenshot Evaluation

When you need to see the visual output of a running application—rather than just reading logs
or terminal output—use this skill to capture and evaluate a screenshot.

## When to use this skill

- You've launched a GUI app or opened a browser and want to verify it rendered correctly.
- You're iterating on a UI and need to confirm a change had the expected visual effect.
- The program produces graphical output (a window, a game screen, a rendered chart) and logs
  alone can't tell you if it's right.
- You're debugging a visual glitch and need to see what the user actually sees.
- The user explicitly asks you to "take a screenshot" or "check what it looks like".

## Step 1 — Launch (if needed)

Make sure the application is running and its window is visible. If you just started it,
give it a moment to render (1–3 seconds is usually enough).

## Step 2 — Capture the screenshot

Run the bundled Python script from your shell:

```bash
python3 ~/.codeium/windsurf/skills/screenshot-eval/scripts/screenshot.py
```

**Common options:**

| Option | Effect |
|--------|--------|
| `--window "App Name"` | Capture only that window (macOS) |
| `--delay 2` | Wait 2 s before capturing (useful for animations/loading) |
| `--out /tmp/result.png` | Save to a specific path |

The script prints the path to the saved PNG. Example:

```
/tmp/screenshot_20260321_143022.png
```

**Dependencies by platform:**
- **macOS**: none (uses built-in `screencapture`)
- **Linux**: install `scrot` (preferred) or `gnome-screenshot`; for `--window`, also install `xdotool`
  ```bash
  sudo apt install scrot xdotool        # Debian/Ubuntu
  sudo pacman -S scrot xdotool          # Arch
  ```
- **Windows**: `pip install Pillow`; optionally `pip install pygetwindow` for `--window` support

## Step 3 — Read and evaluate the screenshot

Open or view the image file at the printed path. Cascade can view images directly — just
read the file at the path the script outputs.

Examine the screenshot and answer:

1. **Is the application running and visible?** (No blank window, no crash dialog)
2. **Does the layout look correct?** (Elements positioned as expected)
3. **Are there visible errors?** (Error messages, missing assets, garbled text)
4. **Does the output match the intended design or requirement?**
5. **What, specifically, is wrong or incomplete?**

## Step 4 — Report findings

Describe what you see concisely:

- **Status**: working / partially working / broken
- **What looks right**: list specific elements that are correct
- **What looks wrong**: describe each issue with enough detail to fix it
- **Suggested next step**: what to change to fix the visual problem

## Tips

- If the window is hidden behind other windows, bring it to front before capturing:
  - macOS: `osascript -e 'tell application "YourApp" to activate'`
  - Linux: `xdotool search --name "YourApp" windowactivate --sync`
  - Windows: `python3 -c "import pygetwindow as gw; gw.getWindowsWithTitle('YourApp')[0].activate()"`
- For animated content, use `--delay 1` and capture at a stable frame.
- For a game (like Geometry Dash running via Geode), use `--window "Geometry Dash"` to
  isolate just the game window rather than the whole desktop.
- Re-capture after every change to track progress. Screenshots are cheap.
- If the screenshot looks totally wrong (blank, desktop only), the window may not have
  focus — activate it and try again.

## Example workflow

```bash
# 1. Launch app (if not running)
# macOS:
open -a "MyApp" && sleep 2
# Linux:
./MyApp & sleep 2
# Windows:
start MyApp.exe & timeout 2

# 2. Capture
python3 ~/.codeium/windsurf/skills/screenshot-eval/scripts/screenshot.py --window "MyApp" --delay 1

# => /tmp/screenshot_20260321_143022.png

# 3. View the image at the printed path and evaluate
```
