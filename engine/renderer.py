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


def _resolve_measure(
    df: pd.DataFrame,
    transform: dict[str, Any],
    title: str,
) -> tuple[pd.Series, str] | None:
    """
    Return (measure_series, measure_label) based on transform.y or transform.y_expr.

    y_expr: {"sum": ["col_a", "col_b", ...]}  → sum across columns row-wise
    y:      "col_name"                         → use that column directly
    """
    y_expr = transform.get("y_expr")
    if y_expr:
        if isinstance(y_expr, dict) and "sum" in y_expr:
            cols = y_expr["sum"]
            if not isinstance(cols, list) or not cols:
                st.warning(f"Bar viz {title!r}: `y_expr.sum` must be a non-empty list.")
                return None
            missing = [c for c in cols if c not in df.columns]
            if missing:
                st.warning(
                    f"Bar viz {title!r}: y_expr columns not found: {missing}. "
                    f"Available: {list(df.columns)}"
                )
                return None
            label = transform.get("y_label") or " + ".join(cols)
            series = df[cols].sum(axis=1)
            series.name = label
            return series, label
        st.warning(f"Bar viz {title!r}: unsupported `y_expr` shape: {y_expr}")
        return None

    y = transform.get("y")
    if not y:
        st.warning(f"Bar viz {title!r}: requires `transform.y` or `transform.y_expr`.")
        return None
    if y not in df.columns:
        st.warning(
            f"Bar viz {title!r}: column `{y}` not found. "
            f"Available: {list(df.columns)}"
        )
        return None
    label = transform.get("y_label") or y
    return df[y], label


def _render_bar(df: pd.DataFrame, viz: dict[str, Any], title: str) -> None:
    """
    Bar chart.

    transform fields:
      x:           column on the x-axis (required)
      y:           column to aggregate, OR
      y_expr:      {"sum": ["col_a", "col_b"]} for a derived measure
      y_label:     optional display name for the measure
      aggfunc:     pandas agg function name applied AFTER the y/y_expr step,
                   default "sum"
      series:      optional column to break bars by (color)
      barmode:     "group" (default) or "stack"
      stack_order: optional, "sum_desc" → series with the largest grand total
                   are placed at the bottom of each stack
    """
    transform = viz.get("transform") or {}
    x = transform.get("x")
    aggfunc = transform.get("aggfunc", "sum")
    series = transform.get("series")
    barmode = transform.get("barmode", "group")
    stack_order = transform.get("stack_order")

    if not x:
        st.warning(f"Bar viz {title!r}: requires `transform.x`.")
        return
    if x not in df.columns:
        st.warning(
            f"Bar viz {title!r}: column `{x}` not found. "
            f"Available: {list(df.columns)}"
        )
        return
    if series and series not in df.columns:
        st.warning(
            f"Bar viz {title!r}: series column `{series}` not found. "
            f"Available: {list(df.columns)}"
        )
        return

    measure = _resolve_measure(df, transform, title)
    if measure is None:
        return
    measure_series, measure_label = measure

    work = pd.DataFrame({x: df[x].values})
    if series:
        work[series] = df[series].values
    work[measure_label] = measure_series.values

    group_cols = [x] + ([series] if series else [])
    agg = (
        work.groupby(group_cols, dropna=False)[measure_label]
        .agg(aggfunc)
        .reset_index()
    )

    category_orders: dict[str, list] | None = None
    if series and stack_order == "sum_desc":
        totals = (
            agg.groupby(series, dropna=False)[measure_label]
            .sum()
            .sort_values(ascending=False)
        )
        category_orders = {series: totals.index.tolist()}

    agg = agg.sort_values(by=group_cols)

    fig = px.bar(
        agg,
        x=x,
        y=measure_label,
        color=series if series else None,
        barmode=barmode if series else "relative",
        title=title or None,
        category_orders=category_orders,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        legend_title_text=series if series else "",
    )

    st.plotly_chart(fig, use_container_width=True)
