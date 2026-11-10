"""Streamlit metadata editor page.

The view collects input and delegates all metadata and filename work to the
controllers in :mod:`src.controllers`.
"""

from __future__ import annotations

import io
import zipfile

import streamlit as st
from PIL import Image

from src import config
from src.controllers import (
    NAMING_MODES,
    build_output_name,
    inject_metadata,
    read_existing_metadata,
    verify_metadata,
)
from src.controllers.naming import CUSTOM_NUMBER, CUSTOM_SAME
from src.views.styles import PAGE_CSS

STAR_FILLED = "★"  # black star
STAR_EMPTY = "☆"  # white star


def _init_state() -> None:
    if "processed" not in st.session_state:
        st.session_state.processed = []
    if "star_rating" not in st.session_state:
        st.session_state.star_rating = config.DEFAULT_RATING


def _top_bar() -> None:
    st.markdown(
        """
        <div class="top-bar">
            <div>
                <div class="brand">Upwork Image <span>Metadata</span> Optimizer</div>
                <div class="tagline">Strip old metadata &nbsp;·&nbsp; Inject fresh IPTC/EXIF &nbsp;·&nbsp; Rename &nbsp;·&nbsp; Rate &nbsp;·&nbsp; Rank higher</div>
            </div>
            <div class="badge">Portfolio Tool</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _upload_card():
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
    return uploaded_files


def _metadata_card():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">2 — Enter New Metadata</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="info-box">
            These fields replace <strong>all existing metadata</strong> in your images.
            Write keyword-rich, Upwork-optimised values to improve discoverability.
        </div>
        """,
        unsafe_allow_html=True,
    )
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

    _star_rating_widget()

    st.markdown("</div>", unsafe_allow_html=True)
    return title_val, author_val, keywords_val, description_val


def _star_rating_widget() -> None:
    st.markdown(
        '<div style="font-size:0.8rem;font-weight:600;color:#1A1714;margin-top:14px;margin-bottom:6px">Star Rating</div>',
        unsafe_allow_html=True,
    )
    s_cols = st.columns(config.MAX_RATING)
    for i in range(1, config.MAX_RATING + 1):
        with s_cols[i - 1]:
            is_filled = i <= st.session_state.star_rating
            label = STAR_FILLED if is_filled else STAR_EMPTY
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
    filled_stars = STAR_FILLED * current
    empty_stars = STAR_EMPTY * (config.MAX_RATING - current)
    st.markdown(
        f'<div style="margin-top:8px;font-size:0.8rem;">'
        f'<span style="color:#F59E0B;font-size:1.1rem">{filled_stars}</span>'
        f'<span style="color:#C8C0B6;font-size:1.1rem">{empty_stars}</span>'
        f'&nbsp; <strong>{current} / 5</strong>'
        f' <span style="color:#7A746C">— {config.STAR_LABELS[current]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _renaming_card(uploaded_files, title_val):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">3 — File Renaming</div>', unsafe_allow_html=True)
    naming_mode = st.selectbox(
        "Naming mode",
        options=NAMING_MODES,
        index=2,
        label_visibility="collapsed",
    )

    custom_name_val = ""
    if naming_mode in (CUSTOM_SAME, CUSTOM_NUMBER):
        custom_name_val = st.text_input(
            "Custom filename (no extension needed)",
            placeholder="e.g. upwork-business-team-photo",
            help="Spaces become hyphens. Special characters are removed automatically.",
        )

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
        suffix = (
            f'<div style="color:#7A746C;font-size:0.7rem">... and {total - 4} more</div>'
            if total > 4
            else ""
        )
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
    return naming_mode, custom_name_val


def _tips_card() -> None:
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
        st.markdown(
            f'<div class="tip-item"><div class="tip-dot"></div><span>{tip}</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _process(uploaded_files, title_val, author_val, keywords_val, description_val, naming_mode, custom_name_val):
    if not any([title_val, author_val, keywords_val, description_val]):
        st.warning("Fill in at least one metadata field before processing.")
        return

    results = []
    errors = []
    total = len(uploaded_files)
    progress = st.progress(0, text="Processing images...")

    for i, file in enumerate(uploaded_files):
        try:
            file.seek(0)
            img = Image.open(file)
            jpeg_bytes = inject_metadata(
                img,
                title=title_val.strip(),
                author=author_val.strip(),
                keywords=keywords_val.strip(),
                description=description_val.strip(),
                rating=st.session_state.star_rating,
            )
            out_name = build_output_name(
                custom_name_val, naming_mode, file.name, title_val, i, total
            )
            results.append((out_name, jpeg_bytes))
        except Exception as e:  # noqa: BLE001 - reported per-file to the user.
            errors.append(f"{file.name}: {e}")

        progress.progress((i + 1) / total, text=f"Processed {i + 1} / {total}")

    progress.empty()
    st.session_state.processed = results

    if results:
        st.success(
            f"{len(results)} image{'s' if len(results) > 1 else ''} processed and renamed successfully."
        )
    for err in errors:
        st.error(err)


def _before_card(uploaded_files):
    """Render the 'before' preview and return the selected file name (or None)."""
    if not uploaded_files:
        st.markdown(
            """
            <div class="card" style="text-align:center;padding:48px 28px">
                <div style="font-size:0.875rem;font-weight:600;color:#1A1714;margin-bottom:6px">No images uploaded yet</div>
                <div style="font-size:0.78rem;color:#7A746C">Upload one or more JPEG / PNG files on the left to get started.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return None

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
    return selected_name


def _after_card(uploaded_files, selected_name):
    if not st.session_state.processed:
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Written Metadata (After)</div>', unsafe_allow_html=True)

    if uploaded_files and selected_name is not None:
        idx_map = {f.name: i for i, f in enumerate(uploaded_files)}
        sel_idx = idx_map.get(selected_name, 0)

        if sel_idx < len(st.session_state.processed):
            proc_name, proc_data = st.session_state.processed[sel_idx]
            verified = verify_metadata(proc_data)

            st.markdown(
                f'<div style="font-size:0.72rem;font-weight:600;color:#7A746C;margin-bottom:3px">Output filename</div>'
                f'<div style="font-size:0.85rem;font-weight:700;color:#C1440E;margin-bottom:14px">{proc_name}</div>',
                unsafe_allow_html=True,
            )

            if verified:
                raw = verified.get("Rating", f"{st.session_state.star_rating} / 5")
                try:
                    n = int(str(raw).split("/")[0].strip().split(" ")[0])
                except Exception:
                    n = st.session_state.star_rating
                filled = STAR_FILLED * n
                empty = STAR_EMPTY * (config.MAX_RATING - n)
                label = config.STAR_LABELS.get(n, "")
                verified["Rating"] = (
                    f'<span style="color:#F59E0B">{filled}</span>'
                    f'<span style="color:#C8C0B6">{empty}</span>'
                    f' ({n}/5 — {label})'
                )
                rows = "".join(
                    f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in verified.items()
                )
                st.markdown(f'<table class="meta-table">{rows}</table>', unsafe_allow_html=True)
                st.markdown('<br><span class="pill-green">Metadata verified</span>', unsafe_allow_html=True)
            else:
                st.markdown(
                    '<span class="pill-red">Verification failed — no metadata read back</span>',
                    unsafe_allow_html=True,
                )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    _download_section()
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Process Another Batch", type="secondary", use_container_width=True):
        st.session_state.processed = []
        st.session_state.star_rating = config.DEFAULT_RATING
        st.rerun()


def _download_section() -> None:
    processed = st.session_state.processed
    if len(processed) == 1:
        name, data = processed[0]
        st.download_button(
            label=f"Download  {name}",
            data=data,
            file_name=name,
            mime="image/jpeg",
            use_container_width=True,
        )
        return

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in processed:
            zf.writestr(name, data)
    zip_buf.seek(0)
    st.download_button(
        label=f"Download All ({len(processed)} images as ZIP)",
        data=zip_buf.read(),
        file_name="upwork_optimized_images.zip",
        mime="application/zip",
        use_container_width=True,
    )
    file_list = " &nbsp;·&nbsp; ".join(f"<strong>{n}</strong>" for n, _ in processed)
    st.markdown(
        f'<div style="font-size:0.7rem;color:#7A746C;margin-top:8px;line-height:1.8">{file_list}</div>',
        unsafe_allow_html=True,
    )


def render() -> None:
    """Render the full metadata editor page."""
    st.set_page_config(
        page_title=config.APP_TITLE,
        layout=config.LAYOUT,
        initial_sidebar_state="collapsed",
    )
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    _top_bar()
    _init_state()

    col_left, col_right = st.columns([1.15, 1], gap="large")

    with col_left:
        uploaded_files = _upload_card()
        title_val, author_val, keywords_val, description_val = _metadata_card()
        naming_mode, custom_name_val = _renaming_card(uploaded_files, title_val)
        _tips_card()
        if st.button(
            "Strip Old Metadata & Apply New",
            type="primary",
            disabled=not uploaded_files,
            use_container_width=True,
        ):
            _process(
                uploaded_files,
                title_val,
                author_val,
                keywords_val,
                description_val,
                naming_mode,
                custom_name_val,
            )

    with col_right:
        selected_name = _before_card(uploaded_files)
        _after_card(uploaded_files, selected_name)
