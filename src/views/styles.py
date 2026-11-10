"""Streamlit styling for the metadata editor page."""

PAGE_CSS = """
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
"""
