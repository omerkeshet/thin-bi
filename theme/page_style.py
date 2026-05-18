"""
Page-level styling — Frappe-Insights-inspired density and aesthetic.
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
}

.stApp { background: #FFFFFF; }

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Streamlit default heading sizes are too large for a dense BI tool. */
h1 {
    font-weight: 600 !important;
    color: #0F172A !important;
    letter-spacing: -0.01em;
    font-size: 1.25rem !important;
    margin: 0 !important;
}
h2 {
    font-weight: 600 !important;
    color: #0F172A !important;
    font-size: 1.05rem !important;
}
h3 {
    font-weight: 600 !important;
    color: #0F172A !important;
    font-size: 0.95rem !important;
}

[data-testid="stCaptionContainer"] {
    color: #64748B;
    font-size: 0.78rem;
}

/* --- Page header --- */
.tbi-page-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 1.25rem;
}
.tbi-page-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #0F172A;
    letter-spacing: -0.01em;
    line-height: 1.2;
}
.tbi-page-meta {
    font-size: 0.78rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 500;
}
.tbi-page-description {
    color: #64748B;
    font-size: 0.85rem;
    margin: -0.5rem 0 1rem 0;
}

/* --- Sidebar --- */
section[data-testid="stSidebar"] {
    background: #FAFAFB;
    border-right: 1px solid #E2E8F0;
}
section[data-testid="stSidebar"] .stMarkdown p {
    margin-bottom: 0.3rem;
    font-size: 0.85rem;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    color: #334155;
    border: 1px solid transparent;
    text-align: left;
    justify-content: flex-start;
    font-weight: 500;
    border-radius: 6px;
    padding: 0.35rem 0.6rem;
    font-size: 0.85rem;
    transition: background 0.12s ease, color 0.12s ease;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #F1F5F9;
    color: #0F172A;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #EEF2FF;
    color: #2563EB;
    font-weight: 600;
    border-color: transparent;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: #E0E7FF;
    color: #1E40AF;
}
section[data-testid="stSidebar"] strong {
    color: #94A3B8;
    text-transform: uppercase;
    font-size: 0.65rem;
    letter-spacing: 0.08em;
    font-weight: 600;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* --- Brand logo --- */
@keyframes tbi-logo-pulse {
    0%, 100% {
        transform: scale(1);
        filter: drop-shadow(0 0 0 rgba(46, 91, 255, 0));
    }
    50% {
        transform: scale(1.025);
        filter: drop-shadow(0 0 10px rgba(46, 91, 255, 0.18));
    }
}
.tbi-logo-img {
    display: block;
    width: 100%;
    height: auto;
    animation: tbi-logo-pulse 2.6s ease-in-out infinite;
    transform-origin: center center;
    will-change: transform, filter;
}
.tbi-sidebar-brand {
    margin: 0.25rem 0 1.25rem 0;
    width: 100%;
}
.tbi-landing-logo {
    display: flex;
    justify-content: center;
    margin: 1rem 0 1.25rem 0;
}
.tbi-landing-logo .tbi-logo-img {
    max-width: 480px;
    width: 100%;
    height: auto;
}

/* --- Chart card --- */
.tbi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1rem 1rem 0.5rem 1rem;
    margin-bottom: 0.75rem;
}
.tbi-chart-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #0F172A;
    letter-spacing: -0.005em;
    margin: 0 0 0.15rem 0;
    line-height: 1.3;
}
.tbi-chart-subtitle {
    font-size: 0.75rem;
    color: #64748B;
    margin: 0 0 0.6rem 0;
    line-height: 1.4;
}
[data-testid="stPlotlyChart"] { padding: 0; }
.element-container:has(> iframe) { margin-bottom: 0 !important; }

/* --- Filter bar --- */
.tbi-filter-bar {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 0.6rem 0.9rem 0.15rem 0.9rem;
    margin-bottom: 1rem;
}
.tbi-filter-bar [data-testid="stWidgetLabel"] p,
.tbi-filter-bar label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: #64748B !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* --- Auth login card --- */
.tbi-auth-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1.75rem 1.75rem 0.75rem 1.75rem;
    margin-top: 4rem;
    text-align: center;
}
.tbi-auth-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.02em;
    margin-bottom: 0.15rem;
}
.tbi-auth-subtitle {
    font-size: 0.85rem;
    color: #64748B;
    margin-bottom: 0.5rem;
}

/* ============================================================
   Light funnel — unchanged
   ============================================================ */
.tbi-funnel-frame {
    --trap-inset-1: 0%;
    --trap-inset-2: 5%;
    --trap-inset-3: 12%;
    --trap-inset-4: 21%;

    background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F7 100%);
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 32px 0 36px;
    position: relative;
    overflow: hidden;
    margin-top: 0.25rem;
}
.tbi-funnel-frame::before {
    content: '';
    position: absolute;
    top: -30%;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    height: 70%;
    background: radial-gradient(ellipse at center, rgba(37,99,235,0.05) 0%, transparent 70%);
    pointer-events: none;
}
.tbi-funnel {
    direction: rtl;
    font-family: 'Heebo', sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    position: relative;
    z-index: 1;
    padding: 0 24px;
}

.tbi-funnel-step {
    text-align: center;
    position: relative;
    width: 100%;
    opacity: 0;
    animation: tbi-fade-in 0.4s ease forwards;
}
@keyframes tbi-fade-in { to { opacity: 1; } }
.tbi-step-1 { animation-delay: 0.05s; }
.tbi-step-2 { animation-delay: 0.15s; }
.tbi-step-3 { animation-delay: 0.25s; }
.tbi-step-4 { animation-delay: 0.35s; }

.tbi-step-1 {
    clip-path: polygon(var(--trap-inset-1) 0%, calc(100% - var(--trap-inset-1)) 0%, calc(100% - var(--trap-inset-2)) 100%, var(--trap-inset-2) 100%);
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border-bottom: 1px solid rgba(15,23,42,0.04);
}
.tbi-step-2 {
    clip-path: polygon(var(--trap-inset-2) 0%, calc(100% - var(--trap-inset-2)) 0%, calc(100% - var(--trap-inset-3)) 100%, var(--trap-inset-3) 100%);
    background: linear-gradient(180deg, #FFFFFF 0%, #F1F5F9 100%);
    border-bottom: 1px solid rgba(15,23,42,0.04);
}
.tbi-step-3 {
    clip-path: polygon(var(--trap-inset-3) 0%, calc(100% - var(--trap-inset-3)) 0%, calc(100% - var(--trap-inset-4)) 100%, var(--trap-inset-4) 100%);
    background: linear-gradient(180deg, #FFFFFF 0%, #E2E8F0 100%);
    border-bottom: 1px solid rgba(15,23,42,0.04);
}
.tbi-step-4 {
    clip-path: polygon(var(--trap-inset-4) 0%, calc(100% - var(--trap-inset-4)) 0%, calc(100% - 26%) 100%, 26% 100%);
    background: linear-gradient(180deg, #FFFFFF 0%, #CBD5E1 100%);
}

.tbi-funnel-step::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: rgba(15,23,42,0.06);
    z-index: 2;
}

.tbi-step-1 .tbi-segments-row { padding-left: var(--trap-inset-2); padding-right: var(--trap-inset-2); }
.tbi-step-2 .tbi-segments-row { padding-left: var(--trap-inset-3); padding-right: var(--trap-inset-3); }
.tbi-step-3 .tbi-segments-row { padding-left: var(--trap-inset-4); padding-right: var(--trap-inset-4); }
.tbi-step-4 .tbi-segments-row { padding-left: 26%; padding-right: 26%; }

.tbi-step-1 .tbi-step-header { padding-left: calc(var(--trap-inset-1) + 12px); padding-right: calc(var(--trap-inset-1) + 12px); }
.tbi-step-2 .tbi-step-header { padding-left: calc(var(--trap-inset-2) + 12px); padding-right: calc(var(--trap-inset-2) + 12px); }
.tbi-step-3 .tbi-step-header { padding-left: calc(var(--trap-inset-3) + 12px); padding-right: calc(var(--trap-inset-3) + 12px); }
.tbi-step-4 .tbi-step-header { padding-left: calc(26% + 12px); padding-right: calc(26% + 12px); }

.tbi-step-header {
    padding: 16px 24px 10px;
    position: relative;
    z-index: 2;
    display: flex;
    align-items: baseline;
    justify-content: center;
    gap: 10px;
}
.tbi-step-number {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 40px;
    font-weight: 700;
    letter-spacing: -1.5px;
    line-height: 1.1;
    color: #0F172A;
}
.tbi-step-label {
    font-size: 14px;
    font-weight: 600;
    line-height: 1.4;
    color: #64748B;
}
.tbi-step-3 .tbi-step-header,
.tbi-step-4 .tbi-step-header { padding: 12px 16px 8px; }
.tbi-step-3 .tbi-step-number { font-size: 32px; }
.tbi-step-4 .tbi-step-number { font-size: 28px; }
.tbi-step-3 .tbi-step-label  { font-size: 12px; }
.tbi-step-4 .tbi-step-label  { font-size: 11px; }

.tbi-segments-row {
    display: flex;
    direction: ltr;
    width: 100%;
    min-height: 52px;
    position: relative;
    z-index: 1;
    overflow: hidden;
}
.tbi-segment {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 7px 10px;
    overflow: hidden;
    position: relative;
    transition: flex-basis 0.5s ease;
    min-width: 0;
    cursor: default;
}
.tbi-segment + .tbi-segment::before {
    content: '';
    position: absolute;
    left: 0;
    top: 12%;
    bottom: 12%;
    width: 0;
    border-left: 1.5px solid rgba(255, 255, 255, 0.45);
    pointer-events: none;
    z-index: 3;
}
.tbi-segment-name {
    font-family: 'Heebo', sans-serif;
    font-size: 13px;
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    line-height: 1.3;
    opacity: 0.95;
}
.tbi-segment-value {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 18px;
    font-weight: 700;
    white-space: nowrap;
    line-height: 1.3;
}
.tbi-segment-pct {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 10px;
    font-weight: 500;
    opacity: 0.75;
    white-space: nowrap;
    line-height: 1.2;
}
.tbi-segment.tbi-narrow .tbi-segment-name,
.tbi-segment.tbi-narrow .tbi-segment-pct { display: none; }
.tbi-segment.tbi-very-narrow .tbi-segment-name,
.tbi-segment.tbi-very-narrow .tbi-segment-value,
.tbi-segment.tbi-very-narrow .tbi-segment-pct { display: none; }

.tbi-segments-row.tier-md { min-height: 44px; }
.tbi-segments-row.tier-md .tbi-segment { padding: 5px 5px; }
.tbi-segments-row.tier-md .tbi-segment-name  { font-size: 12px; }
.tbi-segments-row.tier-md .tbi-segment-value { font-size: 16px; }
.tbi-segments-row.tier-md .tbi-segment-pct   { font-size: 10px; }

.tbi-segments-row.tier-sm { min-height: 40px; }
.tbi-segments-row.tier-sm .tbi-segment { padding: 4px 4px; }
.tbi-segments-row.tier-sm .tbi-segment-name  { font-size: 11px; }
.tbi-segments-row.tier-sm .tbi-segment-value { font-size: 14px; }
.tbi-segments-row.tier-sm .tbi-segment-pct   { font-size: 9px; }

.tbi-segments-row.tier-xs { min-height: 36px; }
.tbi-segments-row.tier-xs .tbi-segment { padding: 4px 3px; }
.tbi-segments-row.tier-xs .tbi-segment-name  { font-size: 10px; }
.tbi-segments-row.tier-xs .tbi-segment-value { font-size: 12px; }
.tbi-segments-row.tier-xs .tbi-segment-pct   { display: none; }

.tbi-funnel-connector {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0;
    position: relative;
    z-index: 5;
    gap: 5px;
    flex-wrap: wrap;
    direction: ltr;
    margin-top: -6px;
    margin-bottom: -6px;
    min-height: 22px;
}
.tbi-connector-badge {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 10px;
    font-weight: 600;
    color: #475569;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 100px;
    padding: 2px 9px;
    letter-spacing: 0.3px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}
.tbi-connector-badge .tbi-cb-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.tbi-connector-badge .tbi-cb-name {
    font-family: 'Heebo', sans-serif;
    font-size: 10px;
    font-weight: 500;
    color: #64748B;
}
</style>
"""


def apply_page_style() -> None:
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def _logo_data_uri(logo_path: Path) -> str | None:
    """Read the SVG and return a base64 data URI for use in an img src attribute."""
    try:
        raw = logo_path.read_bytes()
    except OSError:
        return None
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def render_sidebar_logo(logo_path: Path | None, brand_name: str) -> None:
    if logo_path and logo_path.is_file():
        uri = _logo_data_uri(logo_path)
        if uri:
            st.sidebar.markdown(
                f'<div class="tbi-sidebar-brand">'
                f'<img class="tbi-logo-img" src="{uri}" alt="{brand_name}"/>'
                f"</div>",
                unsafe_allow_html=True,
            )
            return
    st.sidebar.markdown(
        f'<div class="tbi-sidebar-brand">'
        f'<div style="font-size:1.1rem;font-weight:700;color:#0F172A;">{brand_name}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_landing_logo(logo_path: Path | None) -> None:
    if not (logo_path and logo_path.is_file()):
        return
    uri = _logo_data_uri(logo_path)
    if not uri:
        return
    st.markdown(
        f'<div class="tbi-landing-logo">'
        f'<img class="tbi-logo-img" src="{uri}" alt="OmerBI"/>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_app_header(title: str, subtitle: str | None = None) -> None:
    subtitle_html = (
        f'<div style="color:#64748B; font-size:0.85rem; margin-top:0.25rem; text-align:center;">{subtitle}</div>'
        if subtitle
        else ""
    )
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem; text-align: center;">
          <div style="
              font-size: 1.5rem;
              font-weight: 700;
              color: #0F172A;
              letter-spacing: -0.02em;
              line-height: 1.2;
          ">{title}</div>
          {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
