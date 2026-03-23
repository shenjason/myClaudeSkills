#!/usr/bin/env python3
"""
Compare two screenshots and report visual differences.
Usage: python3 screenshot_diff.py before.png after.png [--out diff.png]

Outputs:
- Percentage of pixels that changed
- A diff image highlighting changes (if --out specified)

Requires: pip install Pillow
"""
import sys


def diff_screenshots(path1, path2, out_path=None):
    try:
        from PIL import Image, ImageChops
    except ImportError:
        print("Pillow not installed. Run: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    img1 = Image.open(path1).convert('RGB')
    img2 = Image.open(path2).convert('RGB')

    # Resize to match if dimensions differ
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)

    diff = ImageChops.difference(img1, img2)

    # Count changed pixels (threshold: any channel differs by >10)
    pixels = list(diff.getdata())
    total = len(pixels)
    changed = sum(1 for r, g, b in pixels if max(r, g, b) > 10)
    pct = (changed / total) * 100 if total > 0 else 0

    print(f"Changed pixels: {changed}/{total} ({pct:.1f}%)")
    if pct < 0.1:
        print("Result: IDENTICAL (no meaningful visual change)")
    elif pct < 5:
        print("Result: MINOR changes detected")
    else:
        print("Result: SIGNIFICANT changes detected")

    if out_path:
        enhanced = diff.point(lambda x: min(x * 5, 255))
        enhanced.save(out_path)
        print(f"Diff image saved to: {out_path}")

    return pct


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: screenshot_diff.py before.png after.png [--out diff.png]")
        sys.exit(1)

    out = None
    args = list(sys.argv)
    if '--out' in args:
        idx = args.index('--out')
        out = args[idx + 1]
        del args[idx:idx + 2]

    diff_screenshots(args[1], args[2], out)
