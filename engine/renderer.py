"""
Layout renderer + chart factory.

Reads `dashboard.config["layout"]` — a list of rows, each row a list
of viz definitions — and renders each viz into the appropriate
st.columns slot.

Currently supports: bar.
Coming in later steps: line, kpi, table, filters.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from engine.dashboard_registry import Dashboard
from engine.data_loader import load_dashboard_data
from theme.plotly_theme import apply_chart_polish


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render_dashboard(dashboard: Dashboard) -> None:
    """Top-level dashboard renderer."""
    st.title(dashboard.dashboard_title)
    st.caption(f"{dashboard.department_title} · `{dashboard.key}`")

    description = dashboard.config.get("description")
    if description:
        st.write(description)

    with st.spinner("Loading data..."):
        try:
            df = load_dashboard_data(dashboard)
        except Exception as e:
            st.error(f"Failed to run dashboard query: {type(e).__name__}: {e}")
            with st.expander("Query"):
                st.code(dashboard.query_path.read_text(encoding="utf-8"), language="sql")
            return

    if df.empty:
        st.info("Query returned no rows.")
        return

    # Subtle row-count caption (smaller visual weight than before).
    st.caption(f"{len(df):,} rows loaded")

    layout = dashboard.config.get("layout") or []
    if not layout:
        st.warning("No `layout` defined in config.json. Add a `layout` array of viz rows.")
        with st.expander("Raw data preview"):
            st.dataframe(df.head(50), use_container_width=True)
        return

    for row_idx, row in enumerate(layout):
        if not isinstance(row, list) or not row:
            st.warning(f"Layout row #{row_idx} is empty or malformed.")
            continue
        cols = st.columns(len(row), gap="medium")
        for col, viz in zip(cols, row):
            with col:
                _render_viz(df, viz)


# ---------------------------------------------------------------------------
# Chart factory
# ---------------------------------------------------------------------------

def _render_viz(d
