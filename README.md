# Image Metadata Editor

A Streamlit tool that strips existing metadata from images and writes a fresh
set of IPTC/EXIF fields (title, author, keywords, description, and a star
rating), with optional batch renaming. It is built for preparing portfolio and
stock images so they are clean, consistent, and discoverable.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B.svg)](https://streamlit.io/)

---

## Features

- Upload one or many JPEG / PNG images at once
- Strip all existing metadata and write fresh Title, Author, Keywords,
  Description, and Rating fields (standard EXIF plus Windows XP tags)
- Star rating with EXIF `Rating` and `RatingPercent`
- Batch renaming: keep original, custom name, custom name with numbering, or
  use the title as the filename, with a live preview
- Before/after metadata comparison with read-back verification
- Download a single image or all processed images as a ZIP

---

## Tech stack

| Layer | Technology |
|-------|------------|
| UI | Streamlit |
| Image handling | Pillow |
| EXIF read/write | piexif |

---

## Project structure

The code follows a Model-View-Controller layout:

```
img-metadata-editor/
├── main.py                     # Entry point (streamlit run main.py)
├── src/
│   ├── config.py               # Settings and shared constants
│   ├── controllers/
│   │   ├── metadata.py         # read / inject / verify EXIF metadata
│   │   └── naming.py           # slugify and output-filename logic
│   └── views/
│       ├── styles.py           # Page CSS
│       └── editor_page.py      # Streamlit UI
├── requirements.txt
├── LICENSE
└── README.md
```

The controller functions (`src/controllers`) are pure and free of any Streamlit
dependency, so the metadata and naming logic can be reused or tested on its own.

---

## Prerequisites

- Python 3.9 or newer

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/MuziSan07/img-metadata-editor.git
cd img-metadata-editor

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run main.py
```

The app opens at `http://localhost:8501`.

---

## Usage

1. Upload one or more JPEG / PNG images.
2. Enter the new metadata (fill in at least one field).
3. Set the star rating.
4. Choose a renaming mode and preview the output names.
5. Click **Strip Old Metadata & Apply New**.
6. Review the before/after metadata and download the results.

All processing happens locally in the app; images are never uploaded to an
external service.

---

## Notes

- Output is always written as JPEG (quality 95). PNG inputs are converted to
  JPEG so that EXIF metadata can be embedded.
- Processing replaces all existing metadata rather than merging with it.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
