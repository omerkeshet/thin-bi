"""
Page-level styling — typography, spacing, sidebar polish, funnel CSS.
"""

from __future__ import annotations

import streamlit as st


_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

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

[data-testid="stPlotlyChart"] {
    padding: 0;
}

/* ============================================================
   Funnel viz — ported from the Domo dashboard, scoped under tbi-
   ============================================================ */

.tbi-funnel-frame {
    --trap-inset-1: 0%;
    --trap-inset-2: 5%;
    --trap-inset-3: 12%;
    --trap-inset-4: 21%;

    background: #1e2233;
    border-radius: 12px;
    padding: 36px 0 40px;
    position: relative;
    overflow: hidden;
    margin-top: 0.5rem;
}
.tbi-funnel-frame::before {
    content: '';
    position: absolute;
    top: -30%;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    height: 70%;
    background: radial-gradient(ellipse at center, rgba(99,130,200,0.12) 0%, transparent 70%);
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
    background: linear-gradient(180deg, rgba(255,255,255,0.09) 0%, rgba(255,255,255,0.05) 100%);
}
.tbi-step-2 {
    clip-path: polygon(var(--trap-inset-2) 0%, calc(100% - var(--trap-inset-2)) 0%, calc(100% - var(--trap-inset-3)) 100%, var(--trap-inset-3) 100%);
    background: linear-gradient(180deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.04) 100%);
}
.tbi-step-3 {
    clip-path: polygon(var(--trap-inset-3) 0%, calc(100% - var(--trap-inset-3)) 0%, calc(100% - var(--trap-inset-4)) 100%, var(--trap-inset-4) 100%);
    background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.03) 100%);
}
.tbi-step-4 {
    clip-path: polygon(var(--trap-inset-4) 0%, calc(100% - var(--trap-inset-4)) 0%, calc(100% - 26%) 100%, 26% 100%);
    background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.02) 100%);
}

.tbi-funnel-step::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: rgba(255,255,255,0.10);
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
    padding: 18px 24px 12px;
    position: relative;
    z-index: 2;
    display: flex;
    align-items: baseline;
    justify-content: center;
    gap: 10px;
}
.tbi-step-number {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 44px;
    font-weight: 700;
    letter-spacing: -1.5px;
    line-height: 1.1;
    color: #ffffff;
}
.tbi-step-label {
    font-size: 15px;
    font-weight: 600;
    line-height: 1.4;
    color: #94a3b8;
}
.tbi-step-3 .tbi-step-header,
.tbi-step-4 .tbi-step-header { padding: 14px 16px 10px; }
.tbi-step-3 .tbi-step-number { font-size: 36px; }
.tbi-step-4 .tbi-step-number { font-size: 30px; }
.tbi-step-3 .tbi-step-label  { font-size: 13px; }
.tbi-step-4 .tbi-step-label  { font-size: 12px; }

.tbi-segments-row {
    display: flex;
    direction: ltr;
    width: 100%;
    min-height: 54px;
    position: relative;
    z-index: 1;
    overflow: hidden;
    border-radius: 0;
}
.tbi-segment {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 8px 10px;
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
    border-left: 1.5px solid rgba(255, 255, 255, 0.30);
    pointer-events: none;
    z-index: 3;
}
.tbi-segment-name {
    font-family: 'Heebo', sans-serif;
    font-size: 14px;
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
    font-size: 19px;
    font-weight: 700;
    white-space: nowrap;
    line-height: 1.3;
}
.tbi-segment-pct {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    font-weight: 500;
    opacity: 0.7;
    white-space: nowrap;
    line-height: 1.2;
}
.tbi-segment.tbi-narrow .tbi-segment-name,
.tbi-segment.tbi-narrow .tbi-segment-pct { display: none; }
.tbi-segment.tbi-very-narrow .tbi-segment-name,
.tbi-segment.tbi-very-narrow .tbi-segment-value,
.tbi-segment.tbi-very-narrow .tbi-segment-pct { display: none; }

.tbi-segments-row.tier-md { min-height: 46px; }
.tbi-segments-row.tier-md .tbi-segment { padding: 6px 5px; }
.tbi-segments-row.tier-md .tbi-segment-name  { font-size: 13px; }
.tbi-segments-row.tier-md .tbi-segment-value { font-size: 17px; }
.tbi-segments-row.tier-md .tbi-segment-pct   { font-size: 10px; }

.tbi-segments-row.tier-sm { min-height: 42px; }
.tbi-segments-row.tier-sm .tbi-segment { padding: 5px 4px; }
.tbi-segments-row.tier-sm .tbi-segment-name  { font-size: 12px; }
.tbi-segments-row.tier-sm .tbi-segment-value { font-size: 15px; }
.tbi-segments-row.tier-sm .tbi-segment-pct   { font-size: 9px; }

.tbi-segments-row.tier-xs { min-height: 38px; }
.tbi-segments-row.tier-xs .tbi-segment { padding: 4px 3px; }
.tbi-segments-row.tier-xs .tbi-segment-name  { font-size: 10px; }
.tbi-segments-row.tier-xs .tbi-segment-value { font-size: 13px; }
.tbi-segments-row.tier-xs .tbi-segment-pct   { display: none; }

/* Connector badges */
.tbi-funnel-connector {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0;
    position: relative;
    z-index: 5;
    gap: 6px;
    flex-wrap: wrap;
    direction: ltr;
    margin-top: -6px;
    margin-bottom: -6px;
    min-height: 24px;
}
.tbi-connector-badge {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
    background: rgba(30, 34, 51, 0.85);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 100px;
    padding: 3px 10px;
    letter-spacing: 0.3px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    display: inline-flex;
    align-items: center;
    gap: 5px;
    backdrop-filter: blur(4px);
}
.tbi-connector-badge .tbi-cb-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.tbi-connector-badge .tbi-cb-name {
    font-family: 'Heebo', sans-serif;
    font-size: 10px;
    font-weight: 500;
    opacity: 0.7;
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
        </d
