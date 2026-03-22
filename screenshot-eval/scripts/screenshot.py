#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
screenshot.py - Capture a screenshot for dev output evaluation.

Usage:
    python3 screenshot.py [--window TITLE] [--delay SECONDS] [--out PATH]

Options:
    --window TITLE   Capture only the window whose title contains TITLE
                     (macOS: AppleScript; Linux: xdotool focus then scrot;
                      Windows: pygetwindow activation then full screen)
    --delay SECONDS  Wait N seconds before capturing (default: 0.5)
    --out PATH       Output file path (default: /tmp/screenshot_<timestamp>.png)

Outputs: prints the absolute path of the saved screenshot to stdout.

Platform dependencies:
    macOS   - built-in screencapture (no install needed)
    Linux   - scrot (preferred), gnome-screenshot, or ImageMagick import
              xdotool for --window support
              Fallback: pip install Pillow
    Windows - pip install Pillow  (pygetwindow optional for --window)
"""

import argparse
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# macOS
# ---------------------------------------------------------------------------

def capture_macos(out_path: Path, window_title: str | None) -> Path:
    """Use macOS screencapture (built-in). Supports window targeting via AppleScript."""
    if window_title:
        script = (
            f'tell application "System Events" to get id of '
            f'(first window of (first process whose windows contains '
            f'(first window whose name contains "{window_title}")))'
        )
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip().isdigit():
            wid = result.stdout.strip()
            subprocess.run(
                ["screencapture", "-l", wid, "-x", str(out_path)],
                check=True
            )
            return out_path
        # AppleScript failed (permissions not granted) - activate app, then full screen
        activate = f'tell application "{window_title}" to activate'
        subprocess.run(["osascript", "-e", activate], capture_output=True)
        time.sleep(0.5)

    subprocess.run(["screencapture", "-x", str(out_path)], check=True)
    return out_path


# ---------------------------------------------------------------------------
# Linux
# ---------------------------------------------------------------------------

def _cmd_exists(cmd: str) -> bool:
    return subprocess.run(["which", cmd], capture_output=True).returncode == 0


def capture_linux(out_path: Path, window_title: str | None) -> Path:
    """Screenshot on Linux. Tries scrot, gnome-screenshot, import (ImageMagick), then Pillow."""
    if window_title:
        # Activate the target window so it's on top before capturing
        if _cmd_exists("xdotool"):
            subprocess.run(
                ["xdotool", "search", "--name", window_title, "windowactivate", "--sync"],
                capture_output=True
            )
            time.sleep(0.3)
        elif _cmd_exists("wmctrl"):
            subprocess.run(
                ["wmctrl", "-a", window_title],
                capture_output=True
            )
            time.sleep(0.3)

    # scrot: lightweight, common on Debian/Ubuntu/Arch
    if _cmd_exists("scrot"):
        if window_title and _cmd_exists("xdotool"):
            # -u captures the currently focused window
            subprocess.run(["scrot", "-u", str(out_path)], check=True)
        else:
            subprocess.run(["scrot", str(out_path)], check=True)
        return out_path

    # gnome-screenshot: standard on GNOME desktops
    if _cmd_exists("gnome-screenshot"):
        subprocess.run(["gnome-screenshot", "-f", str(out_path)], check=True)
        return out_path

    # ImageMagick import: captures root window (full screen)
    if _cmd_exists("import"):
        subprocess.run(["import", "-window", "root", str(out_path)], check=True)
        return out_path

    # Last resort: Pillow (works on X11, not Wayland)
    print(
        "Warning: no preferred screenshot tool found (scrot, gnome-screenshot, import).\n"
        "Install one: sudo apt install scrot   OR   pip install Pillow",
        file=sys.stderr,
    )
    return capture_pillow(out_path)


# ---------------------------------------------------------------------------
# Windows
# ---------------------------------------------------------------------------

def capture_windows(out_path: Path, window_title: str | None) -> Path:
    """Screenshot on Windows using Pillow, with optional window activation via pygetwindow."""
    if window_title:
        try:
            import pygetwindow as gw  # type: ignore
            wins = gw.getWindowsWithTitle(window_title)
            if wins:
                wins[0].activate()
                time.sleep(0.4)
        except ImportError:
            # pygetwindow not installed; just take full screen
            pass
        except Exception:
            pass

    return capture_pillow(out_path)


# ---------------------------------------------------------------------------
# Pillow fallback (cross-platform, X11 only on Linux)
# ---------------------------------------------------------------------------

def capture_pillow(out_path: Path) -> Path:
    """Full-screen screenshot using Pillow. Requires: pip install Pillow."""
    try:
        from PIL import ImageGrab  # type: ignore
    except ImportError:
        print(
            "Error: Pillow not installed.\n"
            "  macOS/Windows: pip install Pillow\n"
            "  Linux:         pip install Pillow  (X11 only; Wayland not supported)",
            file=sys.stderr,
        )
        sys.exit(1)
    img = ImageGrab.grab()
    img.save(str(out_path))
    return out_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Take a screenshot for dev evaluation")
    parser.add_argument("--window", "-w", default=None,
                        help="Capture window whose title contains this string")
    parser.add_argument("--delay", "-d", type=float, default=0.5,
                        help="Seconds to wait before capturing (default: 0.5)")
    parser.add_argument("--out", "-o", default=None,
                        help="Output file path (default: /tmp/screenshot_<timestamp>.png)")
    args = parser.parse_args()

    if args.delay > 0:
        time.sleep(args.delay)

    if args.out:
        out_path = Path(args.out)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = Path(f"/tmp/screenshot_{ts}.png")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    system = platform.system()
    if system == "Darwin":
        capture_macos(out_path, args.window)
    elif system == "Linux":
        capture_linux(out_path, args.window)
    elif system == "Windows":
        capture_windows(out_path, args.window)
    else:
        # Unknown platform - try Pillow
        capture_pillow(out_path)

    print(str(out_path))


if __name__ == "__main__":
    main()
