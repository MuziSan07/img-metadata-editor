"""Business logic: metadata read/write and filename generation."""

from src.controllers.metadata import (
    inject_metadata,
    read_existing_metadata,
    verify_metadata,
)
from src.controllers.naming import (
    NAMING_MODES,
    build_output_name,
    slugify,
)

__all__ = [
    "inject_metadata",
    "read_existing_metadata",
    "verify_metadata",
    "NAMING_MODES",
    "build_output_name",
    "slugify",
]
