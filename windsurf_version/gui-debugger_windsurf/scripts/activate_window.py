#!/usr/bin/env python3
"""
Bring an application window to the foreground.
Usage: python3 activate_window.py "AppName"

Works on macOS (AppleScript), Linux (wmctrl), and Windows (Win32 ctypes).
Linux requires wmctrl: sudo apt install wmctrl
"""
import subprocess, sys, time

def activate_window(app_name):
    if sys.platform == 'darwin':
        subprocess.run(
            ['osascript', '-e', f'tell application "{app_name}" to activate'])
    elif sys.platform.startswith('linux'):
        subprocess.run(['wmctrl', '-a', app_name])
    elif sys.platform == 'win32':
        import ctypes
        hwnd = ctypes.windll.user32.FindWindowW(None, app_name)
        if hwnd:
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        else:
            print(f"Warning: window '{app_name}' not found", file=sys.stderr)
    time.sleep(0.5)  # let the window finish coming to front

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: activate_window.py \"AppName\"")
        sys.exit(1)
    activate_window(sys.argv[1])
    print(f"Activated '{sys.argv[1]}'")
