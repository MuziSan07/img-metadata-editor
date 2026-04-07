"""
Upwork Image Metadata Optimizer
================================
Strips old metadata and writes fresh IPTC/EXIF metadata
(Title, Author, Keywords, Description) into JPEG images.

Run:
    pip install streamlit pillow piexif iptcinfo3
    streamlit run upwork_image_metadata.py
"""

import io
import struct
import zipfile
import streamlit as st
from PIL import Image
import piexif

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Upwork Image Metadata Optimizer",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Page background */
.stApp {
    background: #F5F2ED;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Top bar */
.top-bar {
    background: #FFFFFF;
    border-bottom: 1px solid #E4DED5;
    padding: 18px 40px;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.brand {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #1A1714;
    letter-spacing: -0.4px;
}
.brand span { color: #C1440E; }
.tagline {
    font-size: 0.78rem;
    color: #7A746C;
    margin-top: 1px;
}
.badge {
    background: #F5E8E2;
    color: #C1440E;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 99px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Section cards */
.card {
    background: #FFFFFF;
    border: 1px solid #E4DED5;
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 20px;
}
.card-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #7A746C;
    margin-bottom: 16px;
}

/* Override Streamlit input styling */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #F5F2ED !important;
    border: 1px solid #E4DED5 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    color: #1A1714 !important;
    padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #C1440E !important;
    box-shadow: 0 0 0 2px rgba(193,68,14,0.12) !important;
}

/* Labels */
.stTextInput label, .stTextArea label, .stFileUploader label {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #1A1714 !important;
    margin-bottom: 4px !important;
}

/* Buttons */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 10px 22px !important;
    font-size: 0.875rem !important;
    transition: all 0.18s !important;
}
.stButton > button[kind="primary"] {
    background: #C1440E !important;
    border: none !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    background: #d94e16 !important;
}
.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #E4DED5 !important;
    color: #1A1714 !important;
}

/* Download button */
.stDownloadButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 10px 22px !important;
    font-size: 0.875rem !important;
    background: #2A6049 !important;
    color: white !important;
    border: none !important;
    width: 100% !important;
}
.stDownloadButton > button:hover {
    background: #235040 !important;
}

/* File uploader */
.stFileUploader > div {
    border: 2px dashed #E4DED5 !important;
    border-radius: 10px !important;
    background: #FAFAF8 !important;
    padding: 20px !important;
}
.stFileUploader > div:hover {
    border-color: #C1440E !important;
}

/* Metadata display table */
.meta-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
}
.meta-table tr {
    border-bottom: 1px solid #E4DED5;
}
.meta-table tr:last-child { border-bottom: none; }
.meta-table td {
    padding: 9px 0;
    vertical-align: top;
}
.meta-table td:first-child {
    color: #7A746C;
    font-weight: 500;
    width: 38%;
    padding-right: 12px;
}
.meta-table td:last-child { color: #1A1714; word-break: break-word; }

/* Status pills */
.pill-green {
    background: #E3EDE9; color: #2A6049;
    font-size: 0.7rem; font-weight: 600;
    padding: 3px 10px; border-radius: 99px;
    display: inline-block;
}
.pill-red {
    background: #F5E8E2; color: #C1440E;
    font-size: 0.7rem; font-weight: 600;
    padding: 3px 10px; border-radius: 99px;
    display: inline-block;
}
.pill-grey {
    background: #EEEBE6; color: #7A746C;
    font-size: 0.7rem; font-weight: 600;
    padding: 3px 10px; border-radius: 99px;
    display: inline-block;
}

/* Info box */
.info-box {
    background: #F5EDD8;
    border: 1px solid #e8d9a8;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.78rem;
    color: #7A5C1A;
    line-height: 1.55;
    margin-bottom: 16px;
}

/* Tip list */
.tip-item {
    display: flex;
    gap: 8px;
    font-size: 0.78rem;
    color: #7A746C;
    margin-bottom: 7px;
    line-height: 1.5;
}
.tip-dot {
    width: 5px; height: 5px;
    background: #C1440E;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 6px;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #E4DED5;
    margin: 18px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Top Bar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <div>
        <div class="brand">Upwork Image <span>Metadata</span> Optimizer</div>
        <div class="tagline">Strip old metadata · Inject fresh IPTC/EXIF · Rank higher on Upwork</div>
    </div>
    <div class="badge">Portfolio Tool</div>
</div>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def read_existing_metadata(img: Image.Image) -> dict:
    """Extract whatever metadata already exists in the image."""
    info = {}
    exif_data = img.info.get("exif", None)
    if exif_data:
        try:
            exif_dict = piexif.load(exif_data)
            ifd0 = exif_dict.get("0th", {})
            img_ifd = exif_dict.get("Exif", {})

            def decode(val):
                return val.decode("utf-8", errors="ignore").strip() if isinstance(val, bytes) else str(val)

            if piexif.ImageIFD.DocumentName in ifd0:
                info["Title"] = decode(ifd0[piexif.ImageIFD.DocumentName])
            if piexif.ImageIFD.Artist in ifd0:
                info["Author"] = decode(ifd0[piexif.ImageIFD.Artist])
            if piexif.ImageIFD.ImageDescription in ifd0:
                info["Description"] = decode(ifd0[piexif.ImageIFD.ImageDescription])
            if piexif.ImageIFD.XPKeywords in ifd0:
                raw = bytes(ifd0[piexif.ImageIFD.XPKeywords])
                info["Keywords"] = raw.decode("utf-16-le", errors="ignore").strip("\x00")
            if piexif.ImageIFD.Copyright in ifd0:
                info["Copyright"] = decode(ifd0[piexif.ImageIFD.Copyright])
            if piexif.ImageIFD.Software in ifd0:
                info["Software"] = decode(ifd0[piexif.ImageIFD.Software])
            if piexif.ImageIFD.Make in ifd0:
                info["Camera Make"] = decode(ifd0[piexif.ImageIFD.Make])
            if piexif.ImageIFD.Model in ifd0:
                info["Camera Model"] = decode(ifd0[piexif.ImageIFD.Model])
            if piexif.ExifIFD.DateTimeOriginal in img_ifd:
                info["Date Taken"] = decode(img_ifd[piexif.ExifIFD.DateTimeOriginal])
        except Exception:
            pass

    # IPTC-like data sometimes in info dict
    for key in ("title", "description", "keywords", "author", "comment"):
        if key in img.info and key.capitalize() not in info:
            val = img.info[key]
            if isinstance(val, bytes):
                val = val.decode("utf-8", errors="ignore")
            info[key.capitalize()] = str(val)

    return info


def build_xp_field(text: str) -> list:
    """Encode a string as UTF-16-LE bytes for Windows XP EXIF fields."""
    encoded = (text + "\x00").encode("utf-16-le")
    return list(encoded)


def inject_metadata(img: Image.Image, title: str, author: str,
                    keywords: str, description: str) -> bytes:
    """
    Strip all existing EXIF, then write fresh EXIF with our four fields.
    Returns the processed JPEG as bytes.
    """
    # Build a clean EXIF dict
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    ifd0 = exif_dict["0th"]

    if title:
        ifd0[piexif.ImageIFD.DocumentName]    = title.encode("utf-8")
        ifd0[piexif.ImageIFD.XPTitle]         = build_xp_field(title)

    if author:
        ifd0[piexif.ImageIFD.Artist]           = author.encode("utf-8")
        ifd0[piexif.ImageIFD.XPAuthor]         = build_xp_field(author)

    if description:
        ifd0[piexif.ImageIFD.ImageDescription] = description.encode("utf-8")
        ifd0[piexif.ImageIFD.XPComment]        = build_xp_field(description)

    if keywords:
        ifd0[piexif.ImageIFD.XPKeywords]       = build_xp_field(keywords)
        ifd0[piexif.ImageIFD.XPSubject]        = build_xp_field(keywords)

    exif_bytes = piexif.dump(exif_dict)

    buf = io.BytesIO()
    # Convert to RGB (handles RGBA PNGs etc.)
    rgb = img.convert("RGB")
    rgb.save(buf, format="JPEG", exif=exif_bytes, quality=95, optimize=True)
    buf.seek(0)
    return buf.read()


def verify_metadata(jpeg_bytes: bytes) -> dict:
    """Re-read the saved JPEG and confirm metadata was written."""
    img = Image.open(io.BytesIO(jpeg_bytes))
    return read_existing_metadata(img)


# ── Session State ──────────────────────────────────────────────────────────────
if "processed" not in st.session_state:
    st.session_state.processed = []   # list of (filename, bytes)

# ── Layout: two columns ────────────────────────────────────────────────────────
col_left, col_right = st.columns([1.15, 1], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT — Upload + Metadata Form
# ══════════════════════════════════════════════════════════════════════════════
with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">1 — Upload Images</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop JPEG / PNG files here",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        names = [f.name for f in uploaded_files]
        st.markdown(
            f'<span class="pill-green">{len(uploaded_files)} file{"s" if len(uploaded_files)>1 else ""} loaded</span> '
            + " &nbsp; ".join(f'<span class="pill-grey">{n}</span>' for n in names),
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Metadata Fields ────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">2 — Enter New Metadata</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        These fields will replace <strong>all existing metadata</strong> in your images.
        Write keyword-rich, Upwork-optimised values to improve discoverability.
    </div>
    """, unsafe_allow_html=True)

    title_val = st.text_input(
        "Title",
        placeholder="e.g. Professional Business Team Meeting in Modern Office",
        help="The main title of the image. Use descriptive, searchable language.",
    )

    author_val = st.text_input(
        "Author / Creator",
        placeholder="e.g. John Smith Photography",
        help="Your name or studio name.",
    )

    keywords_val = st.text_input(
        "Keywords / Tags",
        placeholder="e.g. business, team, office, meeting, professional, corporate",
        help="Comma-separated keywords. Use relevant, high-volume search terms.",
    )

    description_val = st.text_area(
        "Description",
        placeholder="e.g. A group of diverse business professionals collaborating around a conference table in a bright, modern office environment. Ideal for corporate, teamwork, and business themes.",
        height=110,
        help="A detailed description of the image content and ideal use cases.",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Tips ───────────────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Upwork Ranking Tips</div>', unsafe_allow_html=True)
    tips = [
        "Use 10–30 comma-separated keywords covering subject, style, mood, and use case.",
        "Write titles in sentence case — avoid ALL CAPS and excessive punctuation.",
        "Match your description to how a client would search, not how a photographer thinks.",
        "Include colour, lighting, and setting terms (e.g. 'warm lighting', 'white background').",
        "Batch process images that share the same theme with identical metadata for consistency.",
    ]
    for tip in tips:
        st.markdown(f'<div class="tip-item"><div class="tip-dot"></div><span>{tip}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Process Button ─────────────────────────────────────────────────────────
    process_clicked = st.button(
        "Strip Old Metadata & Apply New",
        type="primary",
        disabled=not uploaded_files,
        use_container_width=True,
    )

    if process_clicked:
        if not any([title_val, author_val, keywords_val, description_val]):
            st.warning("Fill in at least one metadata field before processing.")
        else:
            results = []
            progress = st.progress(0, text="Processing images...")
            errors = []

            for i, file in enumerate(uploaded_files):
                try:
                    img = Image.open(file)
                    jpeg_bytes = inject_metadata(
                        img,
                        title=title_val.strip(),
                        author=author_val.strip(),
                        keywords=keywords_val.strip(),
                        description=description_val.strip(),
                    )
                    # Force .jpg extension
                    out_name = file.name.rsplit(".", 1)[0] + "_optimized.jpg"
                    results.append((out_name, jpeg_bytes))
                except Exception as e:
                    errors.append(f"{file.name}: {e}")

                progress.progress((i + 1) / len(uploaded_files),
                                  text=f"Processed {i+1} / {len(uploaded_files)}")

            progress.empty()
            st.session_state.processed = results

            if results:
                st.success(f"{len(results)} image{'s' if len(results)>1 else ''} processed successfully.")
            if errors:
                for err in errors:
                    st.error(err)


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT — Preview + Download
# ══════════════════════════════════════════════════════════════════════════════
with col_right:

    # ── Before/After metadata display ─────────────────────────────────────────
    if uploaded_files:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Existing Metadata (Before)</div>', unsafe_allow_html=True)

        selected_name = st.selectbox(
            "Preview file",
            options=[f.name for f in uploaded_files],
            label_visibility="collapsed",
        )
        selected_file = next(f for f in uploaded_files if f.name == selected_name)
        selected_file.seek(0)
        preview_img = Image.open(selected_file)

        # Image preview
        st.image(preview_img, use_container_width=True)
        st.markdown(f"""
        <div style="font-size:0.72rem;color:#7A746C;margin-top:4px;margin-bottom:12px">
            {preview_img.width} × {preview_img.height} px &nbsp;·&nbsp; {preview_img.mode} &nbsp;·&nbsp; {preview_img.format or 'JPEG'}
        </div>""", unsafe_allow_html=True)

        # Existing metadata
        existing = read_existing_metadata(preview_img)
        if existing:
            rows = "".join(
                f"<tr><td>{k}</td><td>{v}</td></tr>"
                for k, v in existing.items()
            )
            st.markdown(
                f'<table class="meta-table">{rows}</table>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="pill-red">No metadata found</span>'
                '<div style="font-size:0.78rem;color:#7A746C;margin-top:8px">This image has no embedded metadata — a fresh set will be written.</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:48px 28px">
            <div style="font-size:2rem;margin-bottom:12px;opacity:0.3">🖼</div>
            <div style="font-size:0.875rem;font-weight:600;color:#1A1714;margin-bottom:6px">No images uploaded yet</div>
            <div style="font-size:0.78rem;color:#7A746C">Upload one or more JPEG / PNG files on the left to get started.</div>
        </div>
        """, unsafe_allow_html=True)

    # ── After: verification + download ────────────────────────────────────────
    if st.session_state.processed:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Written Metadata (After)</div>', unsafe_allow_html=True)

        # Find matching processed file
        proc_names = [p[0] for p in st.session_state.processed]
        if uploaded_files:
            base = selected_name.rsplit(".", 1)[0] + "_optimized.jpg"
            match = next((p for p in st.session_state.processed if p[0] == base), None)
            if match:
                verified = verify_metadata(match[1])
                if verified:
                    rows = "".join(
                        f"<tr><td>{k}</td><td>{v}</td></tr>"
                        for k, v in verified.items()
                    )
                    st.markdown(
                        f'<table class="meta-table">{rows}</table>',
                        unsafe_allow_html=True,
                    )
                    st.markdown('<br><span class="pill-green">Metadata verified</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="pill-red">Verification failed — no metadata read back</span>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # Download options
        if len(st.session_state.processed) == 1:
            name, data = st.session_state.processed[0]
            st.download_button(
                label=f"Download  {name}",
                data=data,
                file_name=name,
                mime="image/jpeg",
                use_container_width=True,
            )
        else:
            # Bundle into a zip
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for name, data in st.session_state.processed:
                    zf.writestr(name, data)
            zip_buf.seek(0)

            st.download_button(
                label=f"Download All ({len(st.session_state.processed)} images as ZIP)",
                data=zip_buf.read(),
                file_name="upwork_optimized_images.zip",
                mime="application/zip",
                use_container_width=True,
            )

            st.markdown(
                f'<div style="font-size:0.72rem;color:#7A746C;margin-top:8px;text-align:center">'
                f'Individual files: ' + " · ".join(f'<strong>{n}</strong>' for n, _ in st.session_state.processed) +
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Reset button
        if st.button("Process Another Batch", type="secondary", use_container_width=True):
            st.session_state.processed = []
            st.rerun()