"""Validate local Markdown targets, without network access."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINKS = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SKIP = ("https://", "http://", "mailto:", "#", "data:", "tel:")
errors: list[str] = []
checked = 0

for md in sorted(ROOT.rglob("*.md")):
    if ".git" in md.parts:
        continue
    content = md.read_text(encoding="utf-8")
    for match in LINKS.finditer(content):
        target = match.group(1).strip().split(" ", 1)[0].strip("<>")
        if not target or target.startswith(SKIP):
            continue
        # Anchor validation belongs to a separate pass.
        local = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not local:
            continue
        resolved = (md.parent / local).resolve()
        checked += 1
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            errors.append(f"{md.relative_to(ROOT)}: escapes repository: {local}")
            continue
        if not resolved.exists():
            errors.append(f"{md.relative_to(ROOT)}: broken link -> {local}")

if errors:
    for error in errors:
        print("ERROR", error, file=sys.stderr)
    print(f"FAILED: {len(errors)} local links broken; {checked} checked")
    raise SystemExit(1)
print(f"PASS: {checked} local Markdown links resolved")
