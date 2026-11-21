#!/usr/bin/env python3
"""Ship the pre-rendered front page to the grader's output folder.

The image (entry.png) is already rendered and committed next to this
file. At grade time the sandbox has no Pillow and no network, so this
entrypoint does no rendering at all: it only copies the finished PNG
into MAKEFUN_OUTPUT_DIR (or /output when that variable is unset).
Standard library only.
"""

import os
import sys
from pathlib import Path
from shutil import copyfile

IMAGE_NAME = "entry.png"
DEFAULT_OUTPUT = "/output"


def output_dir() -> Path:
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    cleaned = raw.strip()
    return Path(cleaned if cleaned else DEFAULT_OUTPUT)


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / IMAGE_NAME
    if not source.is_file():
        print(f"missing source image: {source}", file=sys.stderr)
        return 1
    dest_dir = output_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / IMAGE_NAME
    copyfile(source, dest)
    print(f"copied {source.name} -> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
