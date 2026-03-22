#!/usr/bin/env python3
"""
Tile application windows in a grid across the screen.
Usage: python3 tile_windows.py "Window1" "Window2" "Window3" ...

Matches windows by title (partial match).
Works on macOS (AppleScript), Linux (wmctrl), and Windows (Win32).
Linux requires wmctrl: sudo apt install wmctrl
"""
import subprocess, math, sys, re


def get_screen_size():
    if sys.platform == 'darwin':
        # Primary: Finder desktop bounds (logical coordinates, works in most setups)
        result = subprocess.run(
            ['osascript', '-e',
             'tell application "Finder" to get bounds of window of desktop'],
            capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(', ')
            if len(parts) >= 4:
                return int(parts[2]), int(parts[3])
        # Fallback: NSScreen via JXA (logical coordinates)
        result = subprocess.run(
            ['osascript', '-l', 'JavaScript', '-e',
             'ObjC.import("AppKit"); '
             'var f = $.NSScreen.mainScreen.frame; '
             'JSON.stringify({w: f.size.width, h: f.size.height})'],
            capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            import json
            d = json.loads(result.stdout.strip())
            return int(d['w']), int(d['h'])
        return (1920, 1080)

    elif sys.platform.startswith('linux'):
        result = subprocess.run(['xrandr'], capture_output=True, text=True)
        m = re.search(r'(\d+)x(\d+)\+0\+0', result.stdout)
        return (int(m.group(1)), int(m.group(2))) if m else (1920, 1080)

    elif sys.platform == 'win32':
        import ctypes
        u = ctypes.windll.user32
        return u.GetSystemMetrics(0), u.GetSystemMetrics(1)

    return (1920, 1080)


def tile_window(title, x, y, w, h):
    if sys.platform == 'darwin':
        # Search by window title across all processes
        script = f'''
tell application "System Events"
    repeat with proc in (every process whose background only is false)
        try
            repeat with win in (every window of proc)
                if name of win contains "{title}" then
                    set position of win to {{{x}, {y}}}
                    set size of win to {{{w}, {h}}}
                    return
                end if
            end repeat
        end try
    end repeat
end tell
'''
        subprocess.run(['osascript', '-e', script])

    elif sys.platform.startswith('linux'):
        subprocess.run(['wmctrl', '-r', title, '-e', f'0,{x},{y},{w},{h}'])

    elif sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes

        EnumWindowsProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        found_hwnd = []

        def callback(hwnd, _):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                if title.lower() in buf.value.lower():
                    if ctypes.windll.user32.IsWindowVisible(hwnd):
                        found_hwnd.append(hwnd)
                        return False
            return True

        ctypes.windll.user32.EnumWindows(EnumWindowsProc(callback), 0)
        if found_hwnd:
            ctypes.windll.user32.MoveWindow(found_hwnd[0], x, y, w, h, True)


if __name__ == '__main__':
    apps = sys.argv[1:]
    if not apps:
        print('Usage: tile_windows.py "Window1" "Window2" ...')
        sys.exit(1)

    sw, sh = get_screen_size()
    cols = math.ceil(math.sqrt(len(apps)))
    rows = math.ceil(len(apps) / cols)
    tw, th = sw // cols, sh // rows

    for i, app in enumerate(apps):
        col, row = i % cols, i // cols
        tile_window(app, col * tw, row * th, tw, th)
        print(f"Tiled '{app}' -> ({col * tw}, {row * th}, {tw}, {th})")
