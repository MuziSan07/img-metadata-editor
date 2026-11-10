"""Image metadata read, write, and verification.

Pure functions built on Pillow and piexif, with no Streamlit dependency so the
metadata logic can be reasoned about and tested on its own.
"""

from __future__ import annotations

import io

import piexif
from PIL import Image

from src.config import JPEG_QUALITY, STAR_TO_PERCENT


def _decode(val) -> str:
    return val.decode("utf-8", errors="ignore").strip() if isinstance(val, bytes) else str(val)


def read_existing_metadata(img: Image.Image) -> dict:
    """Return a human-readable dict of metadata already embedded in ``img``."""
    info: dict = {}
    exif_data = img.info.get("exif", None)
    if exif_data:
        try:
            exif_dict = piexif.load(exif_data)
            ifd0 = exif_dict.get("0th", {})
            img_ifd = exif_dict.get("Exif", {})

            if piexif.ImageIFD.DocumentName in ifd0:
                info["Title"] = _decode(ifd0[piexif.ImageIFD.DocumentName])
            if piexif.ImageIFD.Artist in ifd0:
                info["Author"] = _decode(ifd0[piexif.ImageIFD.Artist])
            if piexif.ImageIFD.ImageDescription in ifd0:
                info["Description"] = _decode(ifd0[piexif.ImageIFD.ImageDescription])
            if piexif.ImageIFD.XPKeywords in ifd0:
                raw = bytes(ifd0[piexif.ImageIFD.XPKeywords])
                info["Keywords"] = raw.decode("utf-16-le", errors="ignore").strip("\x00")
            if piexif.ImageIFD.Rating in ifd0:
                info["Rating"] = str(ifd0[piexif.ImageIFD.Rating]) + " / 5"
            if piexif.ImageIFD.Copyright in ifd0:
                info["Copyright"] = _decode(ifd0[piexif.ImageIFD.Copyright])
            if piexif.ImageIFD.Software in ifd0:
                info["Software"] = _decode(ifd0[piexif.ImageIFD.Software])
            if piexif.ImageIFD.Make in ifd0:
                info["Camera Make"] = _decode(ifd0[piexif.ImageIFD.Make])
            if piexif.ImageIFD.Model in ifd0:
                info["Camera Model"] = _decode(ifd0[piexif.ImageIFD.Model])
            if piexif.ExifIFD.DateTimeOriginal in img_ifd:
                info["Date Taken"] = _decode(img_ifd[piexif.ExifIFD.DateTimeOriginal])
        except Exception:
            # Corrupt or unreadable EXIF should not break the preview.
            pass

    for key in ("title", "description", "keywords", "author", "comment"):
        if key in img.info and key.capitalize() not in info:
            val = img.info[key]
            if isinstance(val, bytes):
                val = val.decode("utf-8", errors="ignore")
            info[key.capitalize()] = str(val)
    return info


def _build_xp_field(text: str) -> list:
    """Encode a string as a Windows XP* EXIF field (UTF-16-LE byte list)."""
    return list((text + "\x00").encode("utf-16-le"))


def inject_metadata(
    img: Image.Image,
    title: str,
    author: str,
    keywords: str,
    description: str,
    rating: int,
) -> bytes:
    """Strip existing metadata and return JPEG bytes with fresh metadata."""
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    ifd0 = exif_dict["0th"]

    if title:
        ifd0[piexif.ImageIFD.DocumentName] = title.encode("utf-8")
        ifd0[piexif.ImageIFD.XPTitle] = _build_xp_field(title)
    if author:
        ifd0[piexif.ImageIFD.Artist] = author.encode("utf-8")
        ifd0[piexif.ImageIFD.XPAuthor] = _build_xp_field(author)
    if description:
        ifd0[piexif.ImageIFD.ImageDescription] = description.encode("utf-8")
        ifd0[piexif.ImageIFD.XPComment] = _build_xp_field(description)
    if keywords:
        ifd0[piexif.ImageIFD.XPKeywords] = _build_xp_field(keywords)
        ifd0[piexif.ImageIFD.XPSubject] = _build_xp_field(keywords)

    ifd0[piexif.ImageIFD.Rating] = rating
    ifd0[piexif.ImageIFD.RatingPercent] = STAR_TO_PERCENT.get(rating, 99)

    exif_bytes = piexif.dump(exif_dict)
    buf = io.BytesIO()
    img.convert("RGB").save(
        buf, format="JPEG", exif=exif_bytes, quality=JPEG_QUALITY, optimize=True
    )
    buf.seek(0)
    return buf.read()


def verify_metadata(jpeg_bytes: bytes) -> dict:
    """Read back the metadata from freshly written JPEG bytes."""
    img = Image.open(io.BytesIO(jpeg_bytes))
    return read_existing_metadata(img)
