# Troubleshooting Guide

Common failures during GUI debugging and how to recover.

## App won't launch

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `ModuleNotFoundError` | Missing Python dep | `pip install <module>` (check you're in the right venv) |
| `No module named tkinter` | tkinter not packaged | Linux: `sudo apt install python3-tk` |
| `could not connect to display` | No X11 display | `export DISPLAY=:0` or run under Xvfb |
| `Permission denied` | Not executable | `chmod +x app` |
| Exits immediately, no window | Crash on startup | Run foreground: `python3 app.py 2>&1 | tail -30` |
| `Address already in use` | Port conflict | Kill the old process or use a different port |

## Screenshot is blank or shows desktop only

1. **Window hasn't rendered yet** — add `--delay 2` or `sleep 2` before capture
2. **Window is behind others** — activate it first:
   ```bash
   python3 ~/.codeium/windsurf/skills/gui-debugger/scripts/activate_window.py "WindowTitle"
   ```
3. **`--window` can't find the window** — check the exact title:
   ```bash
   # macOS: list all window titles
   osascript -e 'tell application "System Events" to get name of every window of every process whose background only is false'
   # Linux
   wmctrl -l
   # Windows (PowerShell)
   Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object MainWindowTitle
   ```
4. **App creates window lazily** — it may not exist yet; wait longer or trigger via CLI

## pyautogui not working

- **macOS**: Requires Accessibility permissions. System Settings → Privacy & Security →
  Accessibility → add your terminal app. Without this, clicks silently do nothing.
- **Linux**: Requires X11 (`$DISPLAY` must be set). Wayland has limited support — consider
  `xdotool` as an alternative.
- **Clicks land in wrong window**: The IDE/terminal took focus when the user replied "go".
  Always re-activate the target window after receiving user input and before any pyautogui call.
- **`pip install pyautogui` fails**: Try `pip install --user pyautogui` or check if you're
  in a virtual environment that needs activation.

## Window can't be activated

- **Title mismatch**: The search is partial-match, but the title must be a substring. Check
  the actual title using the commands above.
- **Python apps**: The window title is set by the framework (e.g., tkinter's `root.title()`),
  not by the process name. Search for the title string in the source code if unsure.
- **App hasn't created a window yet**: Increase the sleep before activation, or check logs
  to confirm the app reached window creation.

## Process won't die

1. `kill <PID>` sends SIGTERM — the app may take a moment to exit
2. If it ignores SIGTERM: `kill -9 <PID>`
3. If you lost the PID: `ps aux | grep <app pattern>` to find it, then kill by PID
4. **Never use `pkill -f`** — it matches broadly and can kill unrelated processes

## No graphical display

If you're running over SSH, in Docker, or in CI:
```bash
# Linux: check for display
[ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ] && echo "No display available"
```

Options:
- **Xvfb** (virtual framebuffer): `Xvfb :99 -screen 0 1920x1080x24 & export DISPLAY=:99`
- **VNC**: Start a VNC server and connect remotely
- **Not possible**: Tell the user this skill requires a graphical desktop session

macOS and Windows always have a display when logged in.
