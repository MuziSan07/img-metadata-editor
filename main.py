"""
Upwork Image Metadata Optimizer
================================
Strips old metadata and writes fresh IPTC/EXIF metadata
(Title, Author, Keywords, Description, Rating) into JPEG images.
Also supports custom file renaming with auto-numbering.

Run:
    pip install streamlit pillow piexif
    streamlit run upwork_image_metadata.py
"""

import io
import re
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

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #F5F2ED; }
#MainMenu, footer, header { visibility: hidden; }

.top-bar {
    background: #FFFFFF;
    border-bottom: 1px solid #E4DED5;
    padding: 18px 40px;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.brand { font-family: 'DM Serif Display', serif; font-size: 1.4rem; color: #1A1714; letter-spacing: -0.4px; }
.brand span { color: #C1440E; }
.tagline { font-size: 0.78rem; color: #7A746C; margin-top: 1px; }
.badge { background: #F5E8E2; color: #C1440E; font-size: 0.7rem; font-weight: 600; padding: 4px 12px; border-radius: 99px; letter-spacing: 0.05em; text-transform: uppercase; }

.card { background: #FFFFFF; border: 1px solid #E4DED5; border-radius: 12px; padding: 24px 28px; margin-bottom: 20px; }
.card-title { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #7A746C; margin-bottom: 16px; }

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
.stTextInput label, .stTextArea label, .stFileUploader label {
    font-size: 0.8rem !important; font-weight: 600 !important;
    color: #1A1714 !important; margin-bottom: 4px !important;
}

.stButton > button {
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    border-radius: 8px !important; padding: 10px 22px !important;
    font-size: 0.875rem !important; transition: all 0.18s !important;
}
.stButton > button[kind="primary"] { background: #C1440E !important; border: none !important; color: white !important; }
.stButton > button[kind="primary"]:hover { background: #d94e16 !important; }
.stButton > button[kind="secondary"] { background: #FFFFFF !important; border: 1px solid #E4DED5 !important; color: #1A1714 !important; }

.stDownloadButton > button {
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    border-radius: 8px !important; padding: 10px 22px !important;
    font-size: 0.875rem !important; background: #2A6049 !important;
    color: white !important; border: none !important; width: 100% !important;
}
.stDownloadButton > button:hover { background: #235040 !important; }

.stFileUploader > div {
    border: 2px dashed #E4DED5 !important; border-radius: 10px !important;
    background: #FAFAF8 !important; padding: 20px !important;
}
.stFileUploader > div:hover { border-color: #C1440E !important; }

.meta-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.meta-table tr { border-bottom: 1px solid #E4DED5; }
.meta-table tr:last-child { border-bottom: none; }
.meta-table td { padding: 9px 0; vertical-align: top; }
.meta-table td:first-child { color: #7A746C; font-weight: 500; width: 38%; padding-right: 12px; }
.meta-table td:last-child { color: #1A1714; word-break: break-word; }

.pill-green { background: #E3EDE9; color: #2A6049; font-size: 0.7rem; font-weight: 600; padding: 3px 10px; border-radius: 99px; display: inline-block; }
.pill-red   { background: #F5E8E2; color: #C1440E; font-size: 0.7rem; font-weight: 600; padding: 3px 10px; border-radius: 99px; display: inline-block; }
.pill-grey  { background: #EEEBE6; color: #7A746C; font-size: 0.7rem; font-weight: 600; padding: 3px 10px; border-radius: 99px; display: inline-block; }

.info-box { background: #F5EDD8; border: 1px solid #e8d9a8; border-radius: 8px; padding: 12px 16px; font-size: 0.78rem; color: #7A5C1A; line-height: 1.55; margin-bottom: 16px; }

.tip-item { display: flex; gap: 8px; font-size: 0.78rem; color: #7A746C; margin-bottom: 7px; line-height: 1.5; }
.tip-dot { width: 5px; height: 5px; background: #C1440E; border-radius: 50%; flex-shrink: 0; margin-top: 6px; }

.divider { border: none; border-top: 1px solid #E4DED5; margin: 18px 0; }

/* Star rating row */
.star-display {
    display: flex; gap: 4px; align-items: center;
    margin: 8px 0 6px;
}
.star-filled { color: #F59E0B; font-size: 1.7rem; line-height: 1; cursor: pointer; transition: transform 0.1s; }
.star-empty  { color: #D1C9BE; font-size: 1.7rem; line-height: 1; cursor: pointer; transition: transform 0.1s; }
.star-filled:hover, .star-empty:hover { transform: scale(1.2); }
.star-caption { font-size: 0.75rem; color: #7A746C; margin-top: 3px; }

/* Rename preview */
.rename-preview {
    background: #F5F2ED; border: 1px solid #E4DED5; border-radius: 8px;
    padding: 10px 14px; font-size: 0.78rem; color: #1A1714;
    margin-top: 8px; line-height: 1.75;
}
.rename-preview .arrow { color: #C1440E; font-weight: 700; }
.rename-preview .old   { color: #7A746C; }
.rename-preview .new   { color: #1A1714; font-weight: 600; }

.stSelectbox > div > div {
    background: #F5F2ED !important; border: 1px solid #E4DED5 !important;
    border-radius: 8px !important; font-size: 0.875rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Top Bar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <div>
        <div class="brand">Upwork Image <span>Metadata</span> Optimizer</div>
        <div class="tagline">Strip old metadata &nbsp;·&nbsp; Inject fresh IPTC/EXIF &nbsp;·&nbsp; Rename &nbsp;·&nbsp; Rate &nbsp;·&nbsp; Rank higher</div>
    </div>
    <div class="badge">Portfolio Tool</div>
</div>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def read_existing_metadata(img: Image.Image) -> dict:
    info = {}
    exif_data = img.info.get("exif", None)
    if exif_data:
        try:
            exif_dict = piexif.load(exif_data)
            ifd0    = exif_dict.get("0th", {})
            img_ifd = exif_dict.get("Exif", {})

            def decode(val):
                return val.decode("utf-8", errors="ignore").strip() if isinstance(val, bytes) else str(val)

            if piexif.ImageIFD.DocumentName     in ifd0: info["Title"]        = decode(ifd0[piexif.ImageIFD.DocumentName])
            if piexif.ImageIFD.Artist           in ifd0: info["Author"]       = decode(ifd0[piexif.ImageIFD.Artist])
            if piexif.ImageIFD.ImageDescription in ifd0: info["Description"]  = decode(ifd0[piexif.ImageIFD.ImageDescription])
            if piexif.ImageIFD.XPKeywords       in ifd0:
                raw = bytes(ifd0[piexif.ImageIFD.XPKeywords])
                info["Keywords"] = raw.decode("utf-16-le", errors="ignore").strip("\x00")
            if piexif.ImageIFD.Rating           in ifd0: info["Rating"]       = str(ifd0[piexif.ImageIFD.Rating]) + " / 5"
            if piexif.ImageIFD.Copyright        in ifd0: info["Copyright"]    = decode(ifd0[piexif.ImageIFD.Copyright])
            if piexif.ImageIFD.Software         in ifd0: info["Software"]     = decode(ifd0[piexif.ImageIFD.Software])
            if piexif.ImageIFD.Make             in ifd0: info["Camera Make"]  = decode(ifd0[piexif.ImageIFD.Make])
            if piexif.ImageIFD.Model            in ifd0: info["Camera Model"] = decode(ifd0[piexif.ImageIFD.Model])
            if piexif.ExifIFD.DateTimeOriginal  in img_ifd: info["Date Taken"] = decode(img_ifd[piexif.ExifIFD.DateTimeOriginal])
        except Exception:
            pass
    for key in ("title", "description", "keywords", "author", "comment"):
        if key in img.info and key.capitalize() not in info:
            val = img.info[key]
            if isinstance(val, bytes): val = val.decode("utf-8", errors="ignore")
            info[key.capitalize()] = str(val)
    return info


def build_xp_field(text: str) -> list:
    return list((text + "\x00").encode("utf-16-le"))


STAR_TO_PERCENT = {0: 0, 1: 1, 2: 25, 3: 50, 4: 75, 5: 99}
STAR_LABELS     = {1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent"}


def inject_metadata(img: Image.Image, title: str, author: str,
                    keywords: str, description: str, rating: int) -> bytes:
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    ifd0 = exif_dict["0th"]

    if title:
        ifd0[piexif.ImageIFD.DocumentName]      = title.encode("utf-8")
        ifd0[piexif.ImageIFD.XPTitle]           = build_xp_field(title)
    if author:
        ifd0[piexif.ImageIFD.Artist]             = author.encode("utf-8")
        ifd0[piexif.ImageIFD.XPAuthor]          = build_xp_field(author)
    if description:
        ifd0[piexif.ImageIFD.ImageDescription]  = description.encode("utf-8")
        ifd0[piexif.ImageIFD.XPComment]         = build_xp_field(description)
    if keywords:
        ifd0[piexif.ImageIFD.XPKeywords]        = build_xp_field(keywords)
        ifd0[piexif.ImageIFD.XPSubject]         = build_xp_field(keywords)

    ifd0[piexif.ImageIFD.Rating]                = rating
    ifd0[piexif.ImageIFD.RatingPercent]         = STAR_TO_PERCENT.get(rating, 99)

    exif_bytes = piexif.dump(exif_dict)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", exif=exif_bytes, quality=95, optimize=True)
    buf.seek(0)
    return buf.read()


def verify_metadata(jpeg_bytes: bytes) -> dict:
    img = Image.open(io.BytesIO(jpeg_bytes))
    return read_existing_metadata(img)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "image"


def build_output_name(custom_name: str, naming_mode: str,
                      original_name: str, title: str,
                      index: int, total: int) -> str:
    base = original_name.rsplit(".", 1)[0]
    pad  = max(2, len(str(total)))

    if naming_mode == "Keep original name":
        return f"{base}_optimized.jpg"

    elif naming_mode == "Custom name (same for all)":
        slug = slugify(custom_name) if custom_name.strip() else "image"
        if total == 1:
            return f"{slug}.jpg"
        return f"{slug}_{str(index + 1).zfill(pad)}.jpg"

    elif naming_mode == "Custom name + number":
        slug = slugify(custom_name) if custom_name.strip() else "image"
        return f"{slug}_{str(index + 1).zfill(pad)}.jpg"

    elif naming_mode == "Use Title as filename":
        slug = slugify(title) if title.strip() else "image"
        if total == 1:
            return f"{slug}.jpg"
        return f"{slug}_{str(index + 1).zfill(pad)}.jpg"

    return f"{base}_optimized.jpg"


# ── Session State ──────────────────────────────────────────────────────────────
if "processed"   not in st.session_state: st.session_state.processed   = []
if "star_rating" not in st.session_state: st.session_state.star_rating  = 5

# ── Layout ─────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1.15, 1], gap="large")


# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN
# ══════════════════════════════════════════════════════════════════════════════
with col_left:

    # 1. Upload
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">1 — Upload Images</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop JPEG / PNG files here",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        st.markdown(
            f'<span class="pill-green">{len(uploaded_files)} file{"s" if len(uploaded_files) > 1 else ""} loaded</span>&nbsp; '
            + " &nbsp; ".join(f'<span class="pill-grey">{f.name}</span>' for f in uploaded_files),
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Metadata
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">2 — Enter New Metadata</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        These fields replace <strong>all existing metadata</strong> in your images.
        Write keyword-rich, Upwork-optimised values to improve discoverability.
    </div>
    """, unsafe_allow_html=True)

    title_val = st.text_input(
        "Title",
        placeholder="e.g. Professional Business Team Meeting in Modern Office",
        help="Main title — descriptive and searchable.",
    )
    author_val = st.text_input(
        "Author / Creator",
        placeholder="e.g. John Smith Photography",
        help="Your name or studio name.",
    )
    keywords_val = st.text_input(
        "Keywords / Tags",
        placeholder="e.g. business, team, office, meeting, professional, corporate",
        help="Comma-separated. Use relevant, high-volume search terms.",
    )
    description_val = st.text_area(
        "Description",
        placeholder="e.g. Diverse business professionals collaborating in a bright modern office. Ideal for corporate, teamwork, and business themes.",
        height=100,
        help="Detailed description of the image content and ideal use cases.",
    )

    # Star Rating
    st.markdown(
        '<div style="font-size:0.8rem;font-weight:600;color:#1A1714;margin-top:14px;margin-bottom:6px">Star Rating</div>',
        unsafe_allow_html=True,
    )

    # Render 5 clickable star buttons in one row
    s_cols = st.columns(5)
    for i in range(1, 6):
        with s_cols[i - 1]:
            is_filled = i <= st.session_state.star_rating
            label = "★" if is_filled else "☆"
            # Use a styled button — colour applied via markdown overlay
            if st.button(label, key=f"star_btn_{i}", use_container_width=True):
                st.session_state.star_rating = i
                st.rerun()
            colour = "#F59E0B" if is_filled else "#C8C0B6"
            st.markdown(
                f'<div style="text-align:center;font-size:1.55rem;color:{colour};'
                f'margin-top:-44px;pointer-events:none;line-height:1">{label}</div>',
                unsafe_allow_html=True,
            )

    current = st.session_state.star_rating
    filled_stars = "★" * current
    empty_stars  = "☆" * (5 - current)
    st.markdown(
        f'<div style="margin-top:8px;font-size:0.8rem;">'
        f'<span style="color:#F59E0B;font-size:1.1rem">{filled_stars}</span>'
        f'<span style="color:#C8C0B6;font-size:1.1rem">{empty_stars}</span>'
        f'&nbsp; <strong>{current} / 5</strong>'
        f' <span style="color:#7A746C">— {STAR_LABELS[current]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # 3. File Renaming
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">3 — File Renaming</div>', unsafe_allow_html=True)

    naming_mode = st.selectbox(
        "Naming mode",
        options=[
            "Keep original name",
            "Custom name (same for all)",
            "Custom name + number",
            "Use Title as filename",
        ],
        index=2,
        label_visibility="collapsed",
    )

    custom_name_val = ""
    if naming_mode in ("Custom name (same for all)", "Custom name + number"):
        custom_name_val = st.text_input(
            "Custom filename (no extension needed)",
            placeholder="e.g. upwork-business-team-photo",
            help="Spaces become hyphens. Special characters are removed automatically.",
        )

    # Live rename preview
    if uploaded_files:
        total = len(uploaded_files)
        preview_rows = []
        for idx, f in enumerate(uploaded_files[:4]):
            out = build_output_name(custom_name_val, naming_mode, f.name, title_val, idx, total)
            preview_rows.append(
                f'<div><span class="old">{f.name}</span> '
                f'<span class="arrow">→</span> '
                f'<span class="new">{out}</span></div>'
            )
        suffix = f'<div style="color:#7A746C;font-size:0.7rem">... and {total - 4} more</div>' if total > 4 else ""
        st.markdown(
            '<div style="font-size:0.72rem;font-weight:600;color:#7A746C;margin-bottom:4px">Preview</div>'
            f'<div class="rename-preview">{"".join(preview_rows)}{suffix}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="font-size:0.78rem;color:#7A746C">Upload images to see a rename preview.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Tips
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Upwork Ranking Tips</div>', unsafe_allow_html=True)
    for tip in [
        "Use 10–30 comma-separated keywords covering subject, style, mood, and use case.",
        "Write titles in sentence case — avoid ALL CAPS and excessive punctuation.",
        "Match your description to how a client searches, not how a photographer thinks.",
        "Include colour, lighting, and setting terms (e.g. 'warm lighting', 'white background').",
        "Always set 5 stars — the Rating EXIF tag signals high quality to metadata readers.",
        "Use keyword-rich filenames. Search engines and stock sites index the filename itself.",
        "Batch images of the same theme together for faster, consistent processing.",
    ]:
        st.markdown(f'<div class="tip-item"><div class="tip-dot"></div><span>{tip}</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Process button
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
            results  = []
            errors   = []
            total    = len(uploaded_files)
            progress = st.progress(0, text="Processing images...")

            for i, file in enumerate(uploaded_files):
                try:
                    file.seek(0)
                    img        = Image.open(file)
                    jpeg_bytes = inject_metadata(
                        img,
                        title=title_val.strip(),
                        author=author_val.strip(),
                        keywords=keywords_val.strip(),
                        description=description_val.strip(),
                        rating=st.session_state.star_rating,
                    )
                    out_name = build_output_name(
                        custom_name_val, naming_mode, file.name,
                        title_val, i, total
                    )
                    results.append((out_name, jpeg_bytes))
                except Exception as e:
                    errors.append(f"{file.name}: {e}")

                progress.progress((i + 1) / total, text=f"Processed {i+1} / {total}")

            progress.empty()
            st.session_state.processed = results

            if results:
                st.success(f"{len(results)} image{'s' if len(results) > 1 else ''} processed and renamed successfully.")
            for err in errors:
                st.error(err)


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN
# ══════════════════════════════════════════════════════════════════════════════
with col_right:

    # Before
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

        st.image(preview_img, use_container_width=True)
        st.markdown(
            f'<div style="font-size:0.72rem;color:#7A746C;margin-top:4px;margin-bottom:12px">'
            f'{preview_img.width} × {preview_img.height} px &nbsp;·&nbsp; {preview_img.mode} &nbsp;·&nbsp; {preview_img.format or "JPEG"}'
            f'</div>',
            unsafe_allow_html=True,
        )

        existing = read_existing_metadata(preview_img)
        if existing:
            rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in existing.items())
            st.markdown(f'<table class="meta-table">{rows}</table>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<span class="pill-red">No metadata found</span>'
                '<div style="font-size:0.78rem;color:#7A746C;margin-top:8px">'
                'This image carries no embedded metadata — a fresh set will be written.</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:48px 28px">
            <div style="font-size:2.5rem;margin-bottom:12px;opacity:0.2">&#128444;</div>
            <div style="font-size:0.875rem;font-weight:600;color:#1A1714;margin-bottom:6px">No images uploaded yet</div>
            <div style="font-size:0.78rem;color:#7A746C">Upload one or more JPEG / PNG files on the left to get started.</div>
        </div>
        """, unsafe_allow_html=True)

    # After
    if st.session_state.processed:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Written Metadata (After)</div>', unsafe_allow_html=True)

        if uploaded_files:
            idx_map = {f.name: i for i, f in enumerate(uploaded_files)}
            sel_idx = idx_map.get(selected_name, 0)

            if sel_idx < len(st.session_state.processed):
                proc_name, proc_data = st.session_state.processed[sel_idx]
                verified = verify_metadata(proc_data)

                # New filename
                st.markdown(
                    f'<div style="font-size:0.72rem;font-weight:600;color:#7A746C;margin-bottom:3px">Output filename</div>'
                    f'<div style="font-size:0.85rem;font-weight:700;color:#C1440E;margin-bottom:14px">{proc_name}</div>',
                    unsafe_allow_html=True,
                )

                if verified:
                    # Pretty-print star rating
                    raw = verified.get("Rating", f"{st.session_state.star_rating} / 5")
                    try:
                        n = int(str(raw).split("/")[0].strip().split(" ")[0])
                    except Exception:
                        n = st.session_state.star_rating
                    star_vis = (
                        f'<span style="color:#F59E0B">{"★" * n}</span>'
                        f'<span style="color:#C8C0B6">{"☆" * (5 - n)}</span>'
                        f' ({n}/5 — {STAR_LABELS.get(n, "")})'
                    )
                    verified["Rating"] = star_vis

                    rows = "".join(
                        f"<tr><td>{k}</td><td>{v}</td></tr>"
                        for k, v in verified.items()
                    )
                    st.markdown(f'<table class="meta-table">{rows}</table>', unsafe_allow_html=True)
                    st.markdown('<br><span class="pill-green">Metadata verified</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="pill-red">Verification failed — no metadata read back</span>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # Download
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

            file_list = " &nbsp;·&nbsp; ".join(f'<strong>{n}</strong>' for n, _ in st.session_state.processed)
            st.markdown(
                f'<div style="font-size:0.7rem;color:#7A746C;margin-top:8px;line-height:1.8">{file_list}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Process Another Batch", type="secondary", use_container_width=True):
            st.session_state.processed   = []
            st.session_state.star_rating = 5
            st.rerun()
