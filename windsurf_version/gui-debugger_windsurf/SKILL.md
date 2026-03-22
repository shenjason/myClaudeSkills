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

A structured loop for finding and fixing visual bugs in GUI applications. The approach is:
identify the issue → boot the app → delegate visual inspection to sub-agents → diagnose →
fix → reboot → repeat.

**Key principle:** Visual inspection work (launching, navigating, screenshotting) is delegated
to sub-agents. The main agent stays focused on diagnosis and fixes. When multiple apps need
checking, spawn one sub-agent per app and run them in parallel.

---

## Step 1 — Identify the Issue

Before touching the app, get precise about what's broken.

**Sources (check in order):**
1. The user's description in the current message
2. Error logs, crash reports, or console output the user shared
3. A previous failed screenshot already in context
4. Code the user is pointing at

**Write down:**
- What the user expects to see
- What is actually happening (if known)
- Which screen / view / component to navigate to
- How many distinct applications need checking

If the issue is still vague after reading everything available, ask one focused clarifying
question — don't ask several at once. Then proceed.

---

## Step 2 — Delegate Visual Inspection to Sub-Agents

Instead of launching and screenshotting inline, spawn a **Visual Inspector sub-agent** for
each application that needs to be checked. If multiple apps need checking, launch all
sub-agents **in the same turn** so they run in parallel.

### Sub-agent prompt template

Give each sub-agent a self-contained prompt like this:

```
You are a Visual Inspector sub-agent. Your job is to launch an application, navigate to a
specific screen, take screenshots, and report back what you see. Do NOT diagnose or fix anything —
just observe and report.

## Application
<name or path of the app>

## How to launch
<command to start the app — e.g. `python3 app.py &`, `open -a "AppName"` (macOS),
`AppName &` (Linux), `start AppName` (Windows) — plus any build steps needed first>

## Where to navigate
<describe the specific screen, tab, dialog, or state that needs to be checked — be precise>

## Navigation steps (if known)
<list of clicks, keyboard shortcuts, or menu items to reach the target screen, if the user
provided them or they're obvious from context>

## What to look for
<specific visual elements, error states, or behaviors to observe and describe>

## How to screenshot
Use the screenshot-eval skill scripts:

```bash
# Full screen
python3 ~/.codeium/windsurf/skills/screenshot-eval/scripts/screenshot.py

# Specific window (macOS)
python3 ~/.codeium/windsurf/skills/screenshot-eval/scripts/screenshot.py --window "AppName"

# With delay if app is still loading
python3 ~/.codeium/windsurf/skills/screenshot-eval/scripts/screenshot.py --window "AppName" --delay 1
```

Then view the image at the printed path.

For navigation automation, use pyautogui with coordinates from the screenshot:
```bash
pip install pyautogui pillow  # if not installed
```
```python
import pyautogui, time
pyautogui.PAUSE = 0.3
pyautogui.click(x, y)       # click a button
pyautogui.hotkey('ctrl', 't')
pyautogui.write('search term')
time.sleep(1)
```

Take a screenshot after every navigation step, not just at the start.

## Report format
Return a structured report:
- **App state**: Is it running? Crashed? Loading?
- **Screenshot path(s)**: Paths to all screenshots taken (e.g. /tmp/screenshot_*.png)
- **Visual observations**: Describe exactly what you see — layout, colors, text, errors,
  missing elements, anything unusual. Be specific enough that someone who can't see the
  screenshots can understand the state.
- **Navigation taken**: What steps you actually performed to get there
- **Blockers**: Anything that prevented you from reaching the target screen
```

### When to spawn multiple sub-agents

Spawn one sub-agent per app if the user mentions multiple applications, or if the bug
involves interaction between apps (e.g., a client and server UI, or two browser windows).

### Tiling windows when multiple apps are running

When two or more applications need to be visible at the same time, **tile their windows
across the screen** immediately after launching them. This prevents apps from stacking on
top of each other and lets screenshots show each app independently without overlap.

Use the bundled script — it auto-detects the OS (macOS: AppleScript, Linux: wmctrl,
Windows: Win32). Pass the app names as arguments:

```bash
python3 ~/.codeium/windsurf/skills/gui-debugger/scripts/tile_windows.py "App1" "App2" "App3"
# Linux: requires wmctrl — sudo apt install wmctrl
```

Include the tiling step in the sub-agent launch instructions. Run it after all apps are
up (add a `sleep 1` if needed for apps that take time to open their window). With windows
tiled, screenshotting `--window "AppName"` reliably captures the right region for each app.

**Critical: there is only one mouse.** Two sub-agents using pyautogui at the same time
will fight over the cursor — clicks will land in the wrong window, screenshots will capture
mid-transition states, and both runs will produce garbage. Follow this rule:

| Sub-agent needs... | Strategy |
|---|---|
| Screenshots only (no clicks, no typing) | Parallel is fine — screenshotting doesn't move the mouse |
| Mouse clicks or keyboard input | **Run sequentially**, one sub-agent at a time |
| Mixed (some need clicks, some don't) | Start screenshot-only agents in parallel; run navigation agents after they finish |

So if the user says "the poker client and server lobby both look wrong":
- If you can screenshot both without navigating: spawn both in the same turn
- If either needs mouse interaction to reach the relevant screen: run client first, then server (or vice versa)

To reduce how often you need mouse navigation at all, prefer:
1. **Window activation + keyboard shortcuts** over mouse clicks when possible
   (`python3 ~/.codeium/windsurf/skills/gui-debugger/scripts/activate_window.py "AppName"` then `pyautogui.hotkey(...)`)
2. **Deep-linking or CLI flags** to launch directly at the right screen, skipping navigation entirely
3. **Log/console inspection** to diagnose state without interacting with the UI

Only reach for `pyautogui.click()` when there's no other way to reach the target state.

### Hand-off protocol — ask before mouse/keyboard automation

Before any `pyautogui` mouse click or keyboard input, **pause and ask the user for a ready
signal.** Mouse automation moves the physical cursor — if the user's hands are on the
keyboard, clicks will land in the wrong place.

**Critical sequencing issue:** When the user types the ready signal (e.g. `'go'`) in the
IDE/terminal, their reply brings the IDE window to the front and gives it keyboard focus.
If you call `pyautogui.click()` immediately after, the click lands in the IDE, not the app.
Always re-activate the target app window **after** receiving the signal and **before** any
pyautogui call:

```bash
# Correct sequence after receiving the ready signal:
python3 ~/.codeium/windsurf/skills/gui-debugger/scripts/activate_window.py "AppName"
# (script includes a 0.5s sleep — the window is front before control returns)
```
```python
pyautogui.click(x, y)
```

Prompt the user with something specific:

> "I'm about to automate mouse/keyboard input to [describe the action].
> Please move your hands away from the keyboard and mouse, then type **'go'** and press Enter."

Wait for the reply, then run the full automation sequence without further interruption.

Include this in sub-agent prompts whenever mouse/keyboard automation is planned:

```
## Before automating input
STOP before using pyautogui for mouse clicks or keyboard input. Output this message and wait:

"Ready to automate [describe what you're about to do].
Please step away from keyboard and mouse, then type 'go' and press Enter."

After the user replies, re-activate the target app window before any pyautogui call:
  python3 ~/.codeium/windsurf/skills/gui-debugger/scripts/activate_window.py "AppName"
Then proceed with pyautogui automation.
```

---

## Step 3 — Collect Reports and Diagnose

Wait for all sub-agents to finish. Then:

1. **View the screenshots** they captured (use the paths they reported)
2. **Synthesize the reports** — compare observations across apps if multiple were checked
3. **Write a short diagnosis before touching any code:**

> "The settings panel is blank because `loadSettings()` is called before the panel is
> added to the view hierarchy — the data is loaded but there's nowhere to render it."

Ask yourself:
- Is the app running at all? (blank window, crash dialog, nothing visible)
- Is the layout correct? (elements misaligned, overflowing, clipped, invisible)
- Are there error states? (red text, missing assets, "undefined", placeholder text)
- Does the interactive state look right? (wrong tab, checkbox unchecked, wrong value)
- How does this relate to the code? Read the relevant source files now.

This discipline prevents shooting in the dark.

---

## Step 4 — Implement the Fix

Make the smallest code change that addresses the root cause. Avoid refactoring unrelated
code alongside a visual bug fix — keep the diff focused and easy to verify.

After editing, confirm the change is syntactically valid if possible:

```bash
# Python
python3 -m py_compile path/to/file.py

# JavaScript / TypeScript
npx tsc --noEmit

# C++ / compiled language
cmake --build build --parallel 2>&1 | tail -20
```

---

## Step 5 — Relaunch and Re-inspect

Kill the old process(es) and start fresh so the fix is loaded:

```bash
# macOS / Linux
pkill -f "AppName" 2>/dev/null; sleep 1
# Windows (PowerShell)
Stop-Process -Name "AppName" -Force -ErrorAction SilentlyContinue; Start-Sleep 1
```

Then **spawn fresh sub-agent(s)** using the same template from Step 2, updated with any
new navigation context from the previous round. The sub-agents from the previous round are
done — start new ones so they have no residual state.

Compare the new reports against the previous ones.

---

## Step 6 — Evaluate and Decide

After each cycle, make an explicit decision:

| Result | Action |
|--------|--------|
| Issue is gone, everything looks right | Done — report to user |
| Issue is partially fixed, root cause is now clearer | Go to Step 4 with updated diagnosis |
| Issue is unchanged | Re-read the code; diagnosis was probably wrong — restart Step 3 |
| New issue introduced | Revert the change, re-diagnose |

**Hard stop:** If you've cycled 4+ times without progress, pause and explain your findings
to the user rather than continuing to guess. Show them the latest screenshot paths and
describe exactly what you've tried. Ask for any additional context (log files, environment
details, how to reproduce manually). Then **kill all apps that were launched during the
debug session** — leave no orphaned processes:

```bash
# macOS / Linux
pkill -f "AppName1" 2>/dev/null
pkill -f "AppName2" 2>/dev/null
# Windows (PowerShell)
Stop-Process -Name "AppName1" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "AppName2" -Force -ErrorAction SilentlyContinue
# or by PID if you tracked them: kill <PID>  /  Stop-Process -Id <PID>
```

---

## Completing the Loop

When the issue is fixed, report:

1. **What the bug was** (root cause, not just symptoms)
2. **What you changed** (file, line range, and a one-line summary)
3. **Screenshot evidence** that it's now working — view the final screenshot at its path
4. **Kill all apps launched during the session** — don't leave orphaned processes running:

```bash
# macOS / Linux
pkill -f "AppName" 2>/dev/null
# Windows (PowerShell)
Stop-Process -Name "AppName" -Force -ErrorAction SilentlyContinue
# repeat for each app that was launched
```

---

## Notes

- Screenshots are cheap — instruct sub-agents to take one after every interaction.
- Sub-agents are stateless — give them everything they need in the prompt; don't assume they
  remember anything from previous rounds.
- If the window is hidden, the sub-agent should bring it forward before capturing. Include
  this in the launch instructions if needed:
  `python3 ~/.codeium/windsurf/skills/gui-debugger/scripts/activate_window.py "AppName"`
- Use `--window "AppName"` to isolate the app window and avoid capturing irrelevant desktop content.
- Keep navigation automation scripts minimal and throw-away in the sub-agent.
- If the fix requires a full rebuild (compiled apps), budget time for it and include the
  build step in the sub-agent's launch instructions.
- **Mouse is a shared resource.** Never run two sub-agents with pyautogui mouse/keyboard
  automation at the same time — serialize them. Parallel is only safe when neither agent
  touches the mouse.
