"""Image Metadata Editor.

A Streamlit tool that strips existing metadata from images and writes fresh
IPTC/EXIF metadata (title, author, keywords, description, rating), with optional
batch renaming. Code is organised with an MVC layout:

- ``src.config``       Application settings and shared constants.
- ``src.controllers``  Metadata read/write/verify and filename logic (no UI).
- ``src.views``        The Streamlit user interface and styling.
"""

__version__ = "1.0.0"
