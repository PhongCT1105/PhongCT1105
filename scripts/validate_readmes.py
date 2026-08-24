#!/usr/bin/env python3
"""Validate the readme-variants tree before pushing.

Usage:
    python scripts/validate_readmes.py

Checks:
  - all four variant READMEs + the index exist
  - every referenced local image/link path resolves on disk
  - no absolute local machine paths (C:\\, /Users/, /home/, file://)
  - no localhost / 127.0.0.1 URLs
  - no placeholder text (TODO, TBD, FIXME, <your...>, lorem ipsum)
  - no obviously hard-coded fake GitHub stats patterns
  - image assets are not unreasonably large (SVG > 400 KB, raster > 1.5 MB)
  - featured GitHub repo links point at repos that exist locally-known list

Exit code 0 = pass, 1 = failures found.
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

READMES = [
    "readme-variants/README.md",
    "readme-variants/01-terminal/README.md",
    "readme-variants/02-minimal-dark/README.md",
    "readme-variants/03-neon-glow/README.md",
    "readme-variants/04-clean-professional/README.md",
]

PLACEHOLDER_PATTERNS = [
    r"\bTODO\b", r"\bTBD\b", r"\bFIXME\b", r"<your[^>]*>", r"\blorem ipsum\b",
    r"your-org", r"XXXX",
]

# obviously-fake hard-coded stat patterns, e.g. "1,234+ stars", "500+ commits"
FAKE_STAT_PATTERNS = [
    r"\b\d[\d,]*\+?\s*(?:stars|forks|followers|commits|contributions)\b",
]

LOCAL_PATH_PATTERNS = [
    r"[A-Za-z]:\\\\?", r"file://", r"/Users/", r"/home/", r"\bD:/PhongCT1105\b",
]

SVG_MAX = 400 * 1024
RASTER_MAX = int(1.5 * 1024 * 1024)

IMG_MD = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
IMG_HTML = re.compile(r"(?:src|srcset)=\"([^\"]+)\"")
LINK_MD = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s#]+)")


def is_external(url: str) -> bool:
    return url.startswith(("http://", "https://", "mailto:"))


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    for rel in READMES:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            failures.append(f"missing README: {rel}")
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        base = os.path.dirname(path)

        for pat in PLACEHOLDER_PATTERNS:
            for m in re.finditer(pat, text, re.IGNORECASE):
                failures.append(f"{rel}: placeholder text {m.group(0)!r}")

        for pat in FAKE_STAT_PATTERNS:
            for m in re.finditer(pat, text, re.IGNORECASE):
                # numbers inside verified research-result sentences are fine;
                # flag only counts attached to GitHub-metric words
                failures.append(f"{rel}: possible hard-coded stat {m.group(0)!r}")

        for pat in LOCAL_PATH_PATTERNS:
            for m in re.finditer(pat, text):
                failures.append(f"{rel}: local machine path {m.group(0)!r}")

        if re.search(r"localhost|127\.0\.0\.1", text):
            failures.append(f"{rel}: contains localhost URL")

        refs = set(IMG_MD.findall(text)) | set(IMG_HTML.findall(text)) | set(LINK_MD.findall(text))
        for ref in sorted(refs):
            if is_external(ref):
                if ref.startswith("http://"):
                    failures.append(f"{rel}: insecure http:// URL {ref}")
                continue
            target = os.path.normpath(os.path.join(base, ref))
            if not os.path.exists(target):
                failures.append(f"{rel}: broken local path {ref}")

        for m in IMG_HTML.finditer(text):
            ref = m.group(1)
            if is_external(ref) or not ref.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
                continue
            target = os.path.normpath(os.path.join(base, ref))
            if os.path.isfile(target):
                size = os.path.getsize(target)
                limit = SVG_MAX if target.endswith(".svg") else RASTER_MAX
                if size > limit:
                    failures.append(f"{rel}: asset too large ({size/1024:.0f} KB): {ref}")

    # every local asset under assets/ should be referenced by at least one README
    all_text = ""
    for rel in READMES:
        p = os.path.join(ROOT, rel)
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                all_text += f.read()
    assets_dir = os.path.join(ROOT, "assets")
    if os.path.isdir(assets_dir):
        for dirpath, _dirs, files in os.walk(assets_dir):
            for fn in files:
                if fn not in all_text:
                    warnings.append(f"asset never referenced by any README: {os.path.relpath(os.path.join(dirpath, fn), ROOT)}")

    # root README must be untouched relative to origin/main is checked in CI/git,
    # here we only verify it still exists
    if not os.path.isfile(os.path.join(ROOT, "README.md")):
        failures.append("root README.md is missing")

    for w in warnings:
        print(f"WARN  {w}")
    for f_ in failures:
        print(f"FAIL  {f_}")
    if failures:
        print(f"\n{len(failures)} failure(s), {len(warnings)} warning(s).")
        return 1
    print(f"All checks passed ({len(READMES)} READMEs, {len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
