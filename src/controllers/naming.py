"""Output filename generation for processed images."""

from __future__ import annotations

import re

# Naming modes, in the order shown in the UI. The default (index 2) is
# "Custom name + number".
KEEP_ORIGINAL = "Keep original name"
CUSTOM_SAME = "Custom name (same for all)"
CUSTOM_NUMBER = "Custom name + number"
TITLE_AS_NAME = "Use Title as filename"

NAMING_MODES = [KEEP_ORIGINAL, CUSTOM_SAME, CUSTOM_NUMBER, TITLE_AS_NAME]


def slugify(text: str) -> str:
    """Convert arbitrary text into a safe, hyphenated filename slug."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "image"


def build_output_name(
    custom_name: str,
    naming_mode: str,
    original_name: str,
    title: str,
    index: int,
    total: int,
) -> str:
    """Build the output filename for one image based on the selected mode."""
    base = original_name.rsplit(".", 1)[0]
    pad = max(2, len(str(total)))

    if naming_mode == KEEP_ORIGINAL:
        return f"{base}_optimized.jpg"

    if naming_mode == CUSTOM_SAME:
        slug = slugify(custom_name) if custom_name.strip() else "image"
        if total == 1:
            return f"{slug}.jpg"
        return f"{slug}_{str(index + 1).zfill(pad)}.jpg"

    if naming_mode == CUSTOM_NUMBER:
        slug = slugify(custom_name) if custom_name.strip() else "image"
        return f"{slug}_{str(index + 1).zfill(pad)}.jpg"

    if naming_mode == TITLE_AS_NAME:
        slug = slugify(title) if title.strip() else "image"
        if total == 1:
            return f"{slug}.jpg"
        return f"{slug}_{str(index + 1).zfill(pad)}.jpg"

    return f"{base}_optimized.jpg"
