## Dark Mode Toggle Bug — GUI Debugger Walkthrough

### Step 1 — Identify the Issue

**What the user expects:** Clicking the dark mode checkbox turns the window background dark (`#1e1e1e`) with white text.

**What is actually happening:** The checkbox visually toggles but the window background stays white.

**Component to navigate to:** The main window, specifically the area around the dark mode checkbox.

---

### Step 2 — Launch the Application

```bash
python3 app.py &
APP_PID=$!
sleep 2
```

---

### Step 3 — Capture a Screenshot (initial state)

```bash
python3 ~/.claude/skills/screenshot-eval/scripts/screenshot.py --window "MyApp" --delay 1
```

**Expected to see:** White background, unchecked checkbox. This is the baseline.

---

### Step 4 — Navigate to the Problem Area

Use pyautogui to click the checkbox (coordinates read from the baseline screenshot):

```python
import pyautogui, time
pyautogui.PAUSE = 0.3
pyautogui.click(x=220, y=150)  # adjust to actual checkbox position
time.sleep(0.5)
```

Take a second screenshot. **Expected to see (bug present):** Checked checkbox, but still a white background.

---

### Step 5 — Diagnose

Looking at the screenshot and the code:

```python
def toggle_dark_mode(self, checked):
    if checked:
        self.setStyleSheet('QWidget { background-color: #1e1e1e; color: #ffffff; }')
```

Connected via `checkbox.stateChanged.connect(self.toggle_dark_mode)`.

**Root cause — two compounding bugs:**

**Bug 1 (the visual bug): `self.setStyleSheet(...)` targets the wrong object.**

If `self` is a child widget rather than the top-level `QMainWindow` — or if the central widget of a `QMainWindow` is a separate object — the stylesheet is applied to the child's subtree. The `QMainWindow`'s own background area (what the user sees as the white window) is never repainted. Qt applies the rule correctly to `self`, but `self` is not what owns the visible white surface.

**Bug 2 (correctness): No `else` branch.**

`stateChanged` passes a `Qt::CheckState` int: `0` = Unchecked, `2` = Checked. There is no `else`, so unchecking the box leaves the dark stylesheet permanently applied (or if the dark style never visually applied, toggling off does nothing either way).

**Diagnosis statement:**

> The stylesheet is applied to a widget that does not own the visible window background, so Qt repaints that widget's subtree but the user-visible white surface (owned by `QMainWindow` or the OS frame) is never touched. Additionally, the missing `else` branch means unchecking the box never restores the light theme.

---

### Step 6 — Implement the Fix

Smallest correct change — apply the stylesheet to `QApplication.instance()` (covers the entire app) and add the `else` branch:

```python
def toggle_dark_mode(self, checked):
    # stateChanged emits Qt::CheckState: 2 = Checked, 0 = Unchecked
    app = QtWidgets.QApplication.instance()
    if checked == 2:
        app.setStyleSheet('QWidget { background-color: #1e1e1e; color: #ffffff; }')
    else:
        app.setStyleSheet('')   # restore system default
```

If only this window should change (not the whole app), use `self.window()` to walk up to the `QMainWindow` root:

```python
def toggle_dark_mode(self, checked):
    root = self.window()
    if checked == 2:
        root.setStyleSheet('QWidget { background-color: #1e1e1e; color: #ffffff; }')
    else:
        root.setStyleSheet('')
```

Verify syntax: `python3 -m py_compile app.py`

---

### Step 7 — Relaunch and Re-screenshot

```bash
kill $APP_PID 2>/dev/null; sleep 1
python3 app.py & sleep 2
```

1. Screenshot baseline (white, unchecked).
2. Click checkbox, screenshot — expect dark background with white text.
3. Uncheck checkbox, screenshot — expect white background restored.

---

### Step 8 — Evaluate and Decide

| Result | Action |
|--------|--------|
| White → dark → white on each toggle | Done |
| Dark applies but unchecking keeps it dark | `else` branch not firing — verify signal value with a print |
| Still no visual change | Confirm `app.setStyleSheet` is actually reached; check for a higher-priority stylesheet overriding it |
| New issues (invisible buttons, etc.) | Narrow the stylesheet selector; e.g., `QMainWindow { background-color: #1e1e1e; }` |

---

### Summary

**Root cause:** `self.setStyleSheet(...)` was applied to a child widget, not the top-level window or the `QApplication`, so Qt never repainted the visible white surface. A missing `else` branch also meant unchecking would never restore the light theme.

**Fix:** Apply the stylesheet to `QApplication.instance()` (or `self.window()`) and add an `else` branch that clears the stylesheet on uncheck. Use `checked == 2` instead of `if checked:` for robustness against Qt's tri-state checkbox integer values.

**Visual verification plan:** Three screenshots — baseline (white/unchecked), after check (dark/checked), after uncheck (white/unchecked) — confirm the full toggle cycle works correctly.
