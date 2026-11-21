#!/usr/bin/env python3
"""Entrypoint: render the Friday 20 November 2026 front page to entry.png.

Standard library only. Reads MAKEFUN_OUTPUT_DIR (defaults to this file's
own directory) and writes entry.png there via build_image.render().
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_image import render


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
