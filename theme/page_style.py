"""
Page-level styling — typography, spacing, sidebar polish.
"""

from __future__ import annotations

import streamlit as st


_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.stApp {
    background: #F8FAFC;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1400px;
}

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
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #2E5BFF;
    color: white;
    border-color: #2E5BFF;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: #1E48E8;
    border-color: #1E48E8;
}
section[data-testid="stSidebar"] strong {
    color: #94A3B8;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    font-weight: 600;
}

/* Hide Streamlit chrome for a cleaner demo */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* ---------- Chart card ---------- */
.tbi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.25rem 1.25rem 0.5rem 1.25rem;
    box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.04);
    margin-bottom: 1rem;
}
.tbi-chart-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #0F172A;
    letter-spacing: -0.01em;
    margin: 0 0 0.25rem 0;
    line-height: 1.3;
}
.tbi-chart-subtitle {
    font-size: 0.8rem;
    color: #64748B;
    margin: 0 0 0.75rem 0;
    line-height: 1.4;
}

/* Streamlit wraps each plotly chart; remove its own padding so our card
   handles all spacing. */
[data-testid="stPlotlyChart"] {
    padding: 0;
}
</style>
"""


def apply_page_style() -> None:
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def render_app_header(title: str, subtitle: str | None = None) -> None:
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
