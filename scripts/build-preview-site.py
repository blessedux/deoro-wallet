#!/usr/bin/env python3
"""Copy the static Wallet preview (landing, preview, counter, pass) into dist/."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PUBLIC = ("index.html", "preview", "counter", "pass", "install")


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    for name in PUBLIC:
        src = ROOT / name
        dest = DIST / name
        if src.is_dir():
            shutil.copytree(src, dest)
        elif src.is_file():
            shutil.copy2(src, dest)
        else:
            raise SystemExit(f"missing public path: {src}")
    print(f"wrote {DIST} ({', '.join(PUBLIC)})")


if __name__ == "__main__":
    main()
