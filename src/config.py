"""Application settings and shared constants."""

from __future__ import annotations

# --- Page ---------------------------------------------------------------------
APP_TITLE = "Upwork Image Metadata Optimizer"
LAYOUT = "wide"

# --- Image output -------------------------------------------------------------
JPEG_QUALITY = 95

# --- Star rating --------------------------------------------------------------
DEFAULT_RATING = 5
MAX_RATING = 5
STAR_TO_PERCENT = {0: 0, 1: 1, 2: 25, 3: 50, 4: 75, 5: 99}
STAR_LABELS = {1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent"}
