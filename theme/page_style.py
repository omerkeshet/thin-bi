"""
Page-level styling — typography, spacing, sidebar polish, header.

This is global Streamlit CSS injected once at app boot. No per-dashboard
HTML; just a consistent shell that makes the whole portal feel like one
product.
"""

from __future__ import annotations

import streamlit as st


_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Base typography */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Page background — soft off-white, easier on the eyes than pure white */
.stApp {
    background: #F8FAFC;
}

/* Main content padding — a touch more breathing room than default */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1400px;
}

/* Headings */
h1 {
    font-weight: 700 !important;
    color: #0F172A !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem !important;
}
h2, h3 {
    font-weight: 600 !important;
    color: #0F172A !important;
    letter-spacing: -0.01em;
}

/* Captions — tone them down */
[data-testid="stCaptionContainer"] {
    color: #64748B;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}
section[data-testid="stSidebar"] .stMarkdown p {
    margin-bottom: 0.4rem;
}

/* Sidebar nav buttons — pill-ish, less Streamlit-default-y */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    color: #334155;
    border: 1px solid transparent;
    text-align: left;
    justify-content: flex-start;
    font-weight: 500;
    border-radius: 8px;
    padding: 0.4rem 0.75rem;
    transition: all 0.15s ease;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #F1F5F9;
    border-color: #E2E8F0;
    color: #0F172A;
}
/* Primary (selected) button */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #2E5BFF;
    color: white;
    border-color: #2E5BFF;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: #1E48E8;
    border-color: #1E48E8;
}

/* Department labels in sidebar */
section[data-testid="stSidebar"] strong {
    color: #94A3B8;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    font-weight: 600;
}

/* Plotly chart containers — subtle card treatment */
[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1rem 1rem 0.5rem 1rem;
    box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.04);
}

/* Hide the default Streamlit footer + hamburger for a cleaner demo */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
"""


def apply_page_style() -> None:
    """Inject global CSS. Call once near the top of app.py."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def render_app_header(title: str, subtitle: str | None = None) -> None:
    """
    A polished page-level header for when no dashboard is selected.
    Use sparingly — most pages get the dashboard's own title instead.
    """
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
          <div style="
              font-size: 2rem;
              font-weight: 700;
              color: #0F172A;
              letter-spacing: -0.02em;
              line-height: 1.2;
          ">{title}</div>
          {f'<div style="color:#64748B; font-size:1rem; margin-top:0.25rem;">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
