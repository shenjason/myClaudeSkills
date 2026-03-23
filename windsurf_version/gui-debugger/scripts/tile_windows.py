#!/usr/bin/env python3
"""
Tile application windows in a grid across the screen.
Usage: python3 tile_windows.py "App1" "App2" "App3" ...

Works on macOS (AppleScript), Linux (wmctrl), and Windows (Win32 ctypes).
Linux requires wmctrl: sudo apt install wmctrl
"""
import subprocess, math, sys, re

def get_screen_size():
    if sys.platform == 'darwin':
        result = subprocess.run(
            ['osascript', '-e',
             'tell application "Finder" to get bounds of window of desktop'],
            capture_output=True, text=True)
        parts = result.stdout.strip().split(', ')
        return int(parts[2]), int(parts[3])
    elif sys.platform.startswith('linux'):
        result = subprocess.run(['xrandr'], capture_output=True, text=True)
        m = re.search(r'(\d+)x(\d+)\+0\+0', result.stdout)
        return (int(m.group(1)), int(m.group(2))) if m else (1920, 1080)
    elif sys.platform == 'win32':
        import ctypes
        u = ctypes.windll.user32
        return u.GetSystemMetrics(0), u.GetSystemMetrics(1)
    return (1920, 1080)  # fallback

def tile_window(app_name, x, y, w, h):
    if sys.platform == 'darwin':
        script = f'''
tell application "System Events"
    tell process "{app_name}"
        set position of window 1 to {{{x}, {y}}}
        set size of window 1 to {{{w}, {h}}}
    end tell
end tell
'''
        subprocess.run(['osascript', '-e', script])
    elif sys.platform.startswith('linux'):
        subprocess.run(['wmctrl', '-r', app_name, '-e', f'0,{x},{y},{w},{h}'])
    elif sys.platform == 'win32':
        import ctypes
        hwnd = ctypes.windll.user32.FindWindowW(None, app_name)
        if hwnd:
            ctypes.windll.user32.MoveWindow(hwnd, x, y, w, h, True)

if __name__ == '__main__':
    apps = sys.argv[1:]
    if not apps:
        print("Usage: tile_windows.py \"App1\" \"App2\" ...")
        sys.exit(1)

    sw, sh = get_screen_size()
    cols = math.ceil(math.sqrt(len(apps)))
    rows = math.ceil(len(apps) / cols)
    tw, th = sw // cols, sh // rows

    for i, app in enumerate(apps):
        col, row = i % cols, i // cols
        tile_window(app, col * tw, row * th, tw, th)
        print(f"Tiled '{app}' → ({col * tw}, {row * th}, {tw}, {th})")
