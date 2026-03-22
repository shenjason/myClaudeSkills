# Dark Mode Toggle Bug: Diagnosis and Fix

## Bug Diagnosis

There are two distinct bugs in the code as shown.

### Bug 1: Signal/slot argument mismatch (the primary bug)

`QCheckBox.stateChanged` emits an `int`, not a `bool`. The integer values are:
- `0` = unchecked (`Qt.Unchecked`)
- `1` = partially checked (`Qt.PartiallyChecked`)
- `2` = checked (`Qt.Checked`)

When `stateChanged` fires with `checked = 2` (the checked state), the condition `if checked:` evaluates to `True` — so that part actually works for enabling dark mode.

However, the real problem becomes clear in Bug 2.

### Bug 2: No `else` branch — light mode is never restored

The method only handles the `checked` case. When the user unchecks the box, `checked` is `0`, which is falsy, and nothing happens. The stylesheet set previously remains in place. But more importantly, if the app starts in light mode and the user never checks the box, the stylesheet is never applied at all.

More critically: if the user checks then unchecks, there is no code path to restore the original appearance. The window stays dark forever once enabled.

### Bug 3 (likely root cause if it "does nothing"): Wrong signal or connection not firing

If the background truly never changes even on first check, the most probable cause is that `stateChanged` is connected but the slot receives `2` (an int), and if the developer added a type annotation like `def toggle_dark_mode(self, checked: bool)`, PyQt5 may silently fail to invoke the slot due to a signature mismatch in strict mode, or the developer may have accidentally connected to a lambda or different slot.

Alternatively, `checkbox.stateChanged.connect(self.toggle_dark_mode)` may have been called on a different instance than the one being displayed, so the stylesheet is applied to an invisible widget.

## Step-by-Step Reasoning

1. `stateChanged` emits `int` (0 or 2 for a standard two-state checkbox).
2. `toggle_dark_mode(self, checked)` receives that int.
3. `if checked:` with value `2` is `True`, so `setStyleSheet(...)` should be called.
4. `self.setStyleSheet(...)` applies to `self` — this is only correct if `self` is the top-level window. If `self` is a child widget or a non-visible container, the background of the actual window will not change.
5. Even if applied to the right widget, `QWidget` in a stylesheet selector only matches the exact widget, not necessarily all children. The correct selector to cascade to children is to use `*` as the selector.

## The Fix

```python
def toggle_dark_mode(self, state):
    if state == 2:  # Qt.Checked — be explicit about the int value
        self.setStyleSheet('* { background-color: #1e1e1e; color: #ffffff; }')
    else:
        self.setStyleSheet('')  # Reset to default / light mode
```

Key changes:
- Compare against `2` (or `Qt.Checked`) rather than relying on truthiness of an int, to be explicit.
- Add the `else` branch to restore light mode when unchecked.
- Use `*` as the selector instead of `QWidget` so the style cascades to all child widgets (buttons, labels, etc.), not just the top-level widget itself.

If `self` is not the main window, change `self.setStyleSheet` to `self.window().setStyleSheet` to ensure it targets the top-level window:

```python
def toggle_dark_mode(self, state):
    window = self.window()
    if state == 2:
        window.setStyleSheet('* { background-color: #1e1e1e; color: #ffffff; }')
    else:
        window.setStyleSheet('')
```

Alternatively, use `toggled` instead of `stateChanged` — `toggled` emits an actual `bool`:

```python
checkbox.toggled.connect(self.toggle_dark_mode)

def toggle_dark_mode(self, checked: bool):
    if checked:
        self.window().setStyleSheet('* { background-color: #1e1e1e; color: #ffffff; }')
    else:
        self.window().setStyleSheet('')
```

## Verification Steps

1. Add a `print(f"toggle_dark_mode called with: {checked!r} ({type(checked).__name__})")` at the top of the slot. Run the app, click the checkbox, and confirm the slot is actually being called and with what value. If nothing prints, the connection is broken or pointing to the wrong instance.

2. Confirm `self` is the right widget. Add `print(self, self.isVisible(), self.parent())` to check the widget hierarchy.

3. After applying the stylesheet, call `print(self.styleSheet())` to confirm it was actually set.

4. If the slot fires and the stylesheet is set but the background does not change visually, the issue is the CSS selector. Change `QWidget` to `*` and retest.

5. Test both the check and uncheck paths to confirm the `else` branch restores light mode.
