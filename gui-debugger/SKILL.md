---
name: gui-debugger
description: >
  Systematic visual debugging loop for GUI applications. Use this skill whenever you need to
  debug a problem in a running desktop app, web browser, game window, or any program with a
  graphical interface — even if the user just says "the button looks wrong", "the window is
  blank", "the layout is broken", or "it crashes on startup". This skill should trigger any
  time there's a visual or interactive bug that requires launching the application and
  observing it directly. It drives a tight identify → launch → screenshot → navigate →
  diagnose → fix → relaunch loop until the issue is gone.
---

# GUI Debugger

A structured loop for finding and fixing visual bugs in GUI applications.

**Core principles:**
- Delegate visual inspection to sub-agents — the main agent focuses on diagnosis and fixes.
- Always capture both screenshots AND process logs (stdout/stderr).
- Track PIDs at launch — use `kill <PID>` for cleanup, never `pkill -f`.
- If the root cause is already obvious, skip straight to the fix and just verify visually.

---

## Step 0 — Triage

Before entering the full loop, check whether you already know the answer.

**Fast path:** If the user's description + code snippet reveals a clear bug (wrong argument
type, missing return, misordered calls, off-by-one), fix it directly and jump to Step 5 to
visually verify. No need to launch, screenshot, and diagnose when the cause is staring at you.

**Full loop:** If the cause is unclear or you need to see the app's state to understand the
problem, proceed to Step 1.

---

## Step 1 — Identify the Issue

Get precise about what's broken before touching the app.

**Check in order:**
1. The user's description in the current message
2. Error logs, crash reports, or console output
3. Previous screenshots already in context
4. Code the user is pointing at

**Write down:** what the user expects, what's actually happening, which screen/component to
check, how many apps need inspecting.

If still vague, ask one focused clarifying question. Then proceed.

---

## Step 2 — Delegate Visual Inspection

Spawn a **Visual Inspector sub-agent** per app. Read the prompt template at
`~/.claude/skills/gui-debugger/agents/visual-inspector.md` and adapt it for the specific app.

**Key rules:**
- Multiple apps → one sub-agent per app, spawned in the same turn (parallel)
- Sub-agents needing mouse/keyboard → run sequentially (shared mouse)
- Sub-agents only screenshotting → safe to run in parallel
- Always instruct sub-agents to capture the PID and redirect stdout/stderr to a log file

For multi-app scenarios, tile windows after launch:
```bash
python3 ~/.claude/skills/gui-debugger/scripts/tile_windows.py "App1" "App2"
```

If mouse automation is needed, the sub-agent template includes a hand-off protocol — the
sub-agent will ask the user for a ready signal before any pyautogui interaction, then
re-activate the target window before clicking.

---

## Step 3 — Diagnose

1. Read the screenshots and logs from the sub-agent reports
2. Write a short diagnosis **before touching any code**:
   > "The settings panel is blank because `loadSettings()` runs before `self.pack()` —
   > data loads but has nowhere to render."
3. For web apps, also check: browser console errors, network responses, DOM state
4. Read the relevant source files now

If something went wrong during inspection (app didn't launch, screenshot blank, window not
found), check `~/.claude/skills/gui-debugger/references/troubleshooting.md` for recovery steps.

---

## Step 4 — Fix

Make the smallest code change that addresses the root cause. No unrelated refactoring.

Confirm syntax after editing:
```bash
python3 -m py_compile path/to/file.py        # Python
npx tsc --noEmit                               # TypeScript
```

---

## Step 5 — Relaunch and Re-inspect

Kill the old process by PID (from the sub-agent report), then start fresh:
```bash
kill <PID> 2>/dev/null; sleep 1
```

Spawn a **fresh** sub-agent using the visual-inspector template. Compare new screenshots
against previous ones. For objective comparison:
```bash
python3 ~/.claude/skills/gui-debugger/scripts/screenshot_diff.py before.png after.png
```

---

## Step 6 — Evaluate and Decide

| Result | Action |
|--------|--------|
| Fixed, looks right | Done — report to user with screenshot evidence |
| Partially fixed, clearer now | Go to Step 4 with updated diagnosis |
| Unchanged | Re-read code; diagnosis was wrong — restart Step 3 |
| New issue introduced | Revert, re-diagnose |

**Hard stop at 4 cycles:** If you've looped 4 times without resolving it, stop. Show the
user the latest screenshot, explain what you've tried, and ask for more context. Then kill
all processes you launched (by PID).

---

## Completing the Loop

When fixed, report:
1. Root cause (not just symptoms)
2. What you changed (file, line range, one-line summary)
3. Screenshot evidence (read the final screenshot inline)
4. Kill all launched processes by PID

---

## Environment Check

Before launching anything, verify you have a graphical display:
```bash
# Linux only — macOS/Windows always have a display when logged in
[ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ] && echo "No display available"
```
If there's no display, tell the user this skill requires a graphical desktop session.
See `references/troubleshooting.md` for Xvfb setup instructions.

---

## Reference Files

| File | When to read |
|------|-------------|
| `agents/visual-inspector.md` | Before spawning any inspection sub-agent |
| `references/troubleshooting.md` | When something fails (launch, screenshot, activation) |
| `scripts/activate_window.py` | Bundled — brings a window to front by title |
| `scripts/tile_windows.py` | Bundled — arranges windows in a grid |
| `scripts/screenshot_diff.py` | Bundled — pixel-diffs two screenshots |
