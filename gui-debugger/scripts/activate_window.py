#!/usr/bin/env python3
"""
Bring a window to the foreground by its title (partial match).
Usage: python3 activate_window.py "Window Title"

Works on macOS (AppleScript), Linux (wmctrl), and Windows (Win32).
Linux requires wmctrl: sudo apt install wmctrl
"""
import subprocess, sys, time


def activate_window(title):
    if sys.platform == 'darwin':
        # Search by window title across all visible processes
        script = f'''
tell application "System Events"
    repeat with proc in (every process whose background only is false)
        try
            repeat with w in (every window of proc)
                if name of w contains "{title}" then
                    set frontmost of proc to true
                    try
                        perform action "AXRaise" of w
                    end try
                    return name of proc as text
                end if
            end repeat
        end try
    end repeat
    return "NOT_FOUND"
end tell
'''
        result = subprocess.run(
            ['osascript', '-e', script], capture_output=True, text=True)
        output = result.stdout.strip()
        if output == "NOT_FOUND" or not output:
            # Fallback: try treating the argument as an application name
            subprocess.run(
                ['osascript', '-e', f'tell application "{title}" to activate'],
                capture_output=True, text=True)
            print(f"Fallback: activated application '{title}'")
        else:
            print(f"Activated window in process '{output}'")

    elif sys.platform.startswith('linux'):
        subprocess.run(['wmctrl', '-a', title])

    elif sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes

        # Try exact title match first
        hwnd = ctypes.windll.user32.FindWindowW(None, title)
        if hwnd:
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        else:
            # Partial title match via EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(
                ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
            found = []

            def callback(hwnd, _):
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                    if title.lower() in buf.value.lower():
                        if ctypes.windll.user32.IsWindowVisible(hwnd):
                            found.append(hwnd)
                return True

            ctypes.windll.user32.EnumWindows(EnumWindowsProc(callback), 0)
            if found:
                ctypes.windll.user32.SetForegroundWindow(found[0])
            else:
                print(f"Warning: no window matching '{title}' found",
                      file=sys.stderr)

    time.sleep(0.5)  # let the window finish coming to front


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: activate_window.py "Window Title"')
        sys.exit(1)
    activate_window(sys.argv[1])
