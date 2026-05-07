"""
Layout renderer + chart factory.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from engine.dashboard_registry import Dashboard
from engine.data_loader import load_dashboard_data
from theme.plotly_theme import apply_chart_polish


CHART_HEIGHT = 380


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render_dashboard(dashboard: Dashboard) -> None:
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

def _render_viz(df: pd.DataFrame, viz: dict[str, Any]) -> None:
    viz_type = (viz.get("type") or "").lower()
    title = viz.get("title", "")
    subtitle = viz.get("subtitle", "")

    try:
        if viz_type == "bar":
            _render_bar(df, viz, title=title, subtitle=subtitle)
        else:
            st.warning(f"Unknown viz type: `{viz_type}` (viz: {title!r})")
    except Exception as e:
        st.error(f"Failed to render viz {title!r}: {type(e).__name__}: {e}")


def _open_card(title: str, subtitle: str = "") -> None:
    """Render the opening card div + HTML title/subtitle."""
    parts = ['<div class="tbi-card">']
    if title:
        parts.append(f'<div class="tbi-chart-title">{title}</div>')
    if subtitle:
        parts.append(f'<div class="tbi-chart-subtitle">{subtitle}</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def _close_card() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def _resolve_measure(
    df: pd.DataFrame,
    transform: dict[str, Any],
    title: str,
) -> tuple[pd.Series, str] | None:
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


def _is_date_like(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    sample = series.dropna().head(1)
    if sample.empty:
        return False
    val = sample.iloc[0]
    return hasattr(val, "year") and hasattr(val, "month") and hasattr(val, "day")


def _render_bar(
    df: pd.DataFrame,
    viz: dict[str, Any],
    *,
    title: str,
    subtitle: str,
) -> None:
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

    x_is_date = _is_date_like(agg[x])

    fig = px.bar(
        agg,
        x=x,
        y=measure_label,
        color=series if series else None,
        barmode=barmode if series else "relative",
        title=None,  # title rendered as HTML above the chart
        category_orders=category_orders,
        height=CHART_HEIGHT,
    )

    if series:
        fig.update_traces(
            hovertemplate=(
                f"<b>%{{fullData.name}}</b><br>"
                f"{x}: %{{x}}<br>"
                f"{measure_label}: %{{y:,.0f}}"
                "<extra></extra>"
            )
        )
    else:
        fig.update_traces(
            hovertemplate=(
                f"{x}: %{{x}}<br>"
                f"{measure_label}: %{{y:,.0f}}"
                "<extra></extra>"
            )
        )

    apply_chart_polish(fig, x_is_date=x_is_date)

    _open_card(title=title, subtitle=subtitle)
    st.plotly_chart(fig, use_container_width=True)
    _close_card()
