"""
Layout renderer + chart factory.

Reads `dashboard.config["layout"]` — a list of rows, each row a list
of viz definitions — and renders each viz into the appropriate
st.columns slot.

Currently supports: bar.
Coming in later steps: line, kpi, table, themes, filters.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from engine.dashboard_registry import Dashboard
from engine.data_loader import load_dashboard_data


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

    # Load data (cached).
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

    st.caption(f"Loaded {len(df):,} rows · columns: {', '.join(df.columns)}")

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
        cols = st.columns(len(row))
        for col, viz in zip(cols, row):
            with col:
                _render_viz(df, viz)


# ---------------------------------------------------------------------------
# Chart factory
# ---------------------------------------------------------------------------

def _render_viz(df: pd.DataFrame, viz: dict[str, Any]) -> None:
    """Dispatch a single viz definition to the right chart renderer."""
    viz_type = (viz.get("type") or "").lower()
    title = viz.get("title", "")

    try:
        if viz_type == "bar":
            _render_bar(df, viz, title)
        else:
            st.warning(f"Unknown viz type: `{viz_type}` (viz: {title!r})")
    except Exception as e:
        st.error(f"Failed to render viz {title!r}: {type(e).__name__}: {e}")


def _render_bar(df: pd.DataFrame, viz: dict[str, Any], title: str) -> None:
    """
    Bar chart.

    transform fields:
      x:        column on the x-axis (required)
      y:        column to aggregate (required)
      aggfunc:  pandas agg function name, default "sum"
      series:   optional column to break bars by (color)
      barmode:  "group" (default) or "stack"
    """
    transform = viz.get("transform") or {}
    x = transform.get("x")
    y = transform.get("y")
    aggfunc = transform.get("aggfunc", "sum")
    series = transform.get("series")
    barmode = transform.get("barmode", "group")

    if not x or not y:
        st.warning(f"Bar viz {title!r} requires `transform.x` and `transform.y`.")
        return

    missing = [c for c in [x, y, series] if c and c not in df.columns]
    if missing:
        st.warning(
            f"Bar viz {title!r}: column(s) not found in data: {missing}. "
            f"Available: {list(df.columns)}"
        )
        return

    group_cols = [x] + ([series] if series else [])
    agg = (
        df.groupby(group_cols, dropna=False)[y]
        .agg(aggfunc)
        .reset_index()
    )

    # Ensure x is sorted naturally — important for date axes.
    agg = agg.sort_values(by=group_cols)

    fig = px.bar(
        agg,
        x=x,
        y=y,
        color=series if series else None,
        barmode=barmode if series else "relative",
        title=title or None,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        legend_title_text=series if series else "",
    )

    st.plotly_chart(fig, use_container_width=True)
