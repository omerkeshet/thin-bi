"""
Layout renderer + chart factory.
"""

from __future__ import annotations

import html
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from engine.dashboard_registry import Dashboard
from engine.data_loader import load_dashboard_data
from engine.funnel import compute_shorts_funnel, FunnelStep
from theme.plotly_theme import apply_chart_polish, format_number


CHART_HEIGHT = 380


# ---------------------------------------------------------------------------
# Site styling (used by bar charts AND the funnel for visual consistency)
# ---------------------------------------------------------------------------

SITE_BRAND_COLORS: dict[str, str] = {
    "mako": "#f5c518",
    "n12": "#cc1234",
    "v1": "#e84b2b",
}
SITE_TEXT_COLORS: dict[str, str] = {
    "mako": "#1a1a1a",  # dark text on yellow
    "n12": "#ffffff",
    "v1": "#ffffff",
}
SITE_ORDER = ["v1", "mako", "n12"]


def _site_color_map(sites: list[str]) -> dict[str, str]:
    """Build a color map keyed by the actual site values present in the data."""
    out: dict[str, str] = {}
    for s in sites:
        key = str(s).strip().lower()
        if key in SITE_BRAND_COLORS:
            out[str(s)] = SITE_BRAND_COLORS[key]
    return out


def _site_text_color(site: str) -> str:
    return SITE_TEXT_COLORS.get(str(site).strip().lower(), "#ffffff")


def _site_order_for(values: list[str]) -> list[str]:
    """Return the unique site values in the canonical order, with any
    unknown sites appended at the end alphabetically."""
    by_key: dict[str, str] = {}
    for v in values:
        by_key.setdefault(str(v).strip().lower(), str(v))
    ordered: list[str] = []
    for key in SITE_ORDER:
        if key in by_key:
            ordered.append(by_key.pop(key))
    ordered.extend(sorted(by_key.values()))
    return ordered


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
# Chart dispatch
# ---------------------------------------------------------------------------

def _render_viz(df: pd.DataFrame, viz: dict[str, Any]) -> None:
    viz_type = (viz.get("type") or "").lower()
    title = viz.get("title", "")
    subtitle = viz.get("subtitle", "")

    try:
        if viz_type == "bar":
            _render_bar(df, viz, title=title, subtitle=subtitle)
        elif viz_type == "shorts_funnel":
            _render_shorts_funnel(df, viz, title=title, subtitle=subtitle)
        else:
            st.warning(f"Unknown viz type: `{viz_type}` (viz: {title!r})")
    except Exception as e:
        st.error(f"Failed to render viz {title!r}: {type(e).__name__}: {e}")


def _open_card(title: str, subtitle: str = "", *, dark: bool = False) -> None:
    cls = "tbi-card tbi-card-dark" if dark else "tbi-card"
    parts = [f'<div class="{cls}">']
    if title:
        parts.append(f'<div class="tbi-chart-title">{html.escape(title)}</div>')
    if subtitle:
        parts.append(f'<div class="tbi-chart-subtitle">{html.escape(subtitle)}</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def _close_card() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Bar chart
# ---------------------------------------------------------------------------

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
        st.warning(f"Bar viz {title!r}: column `{x}` not found. Available: {list(df.columns)}")
        return
    if series and series not in df.columns:
        st.warning(f"Bar viz {title!r}: series column `{series}` not found.")
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

    # Series ordering — site override beats sum_desc for the canonical
    # site palette we use across the whole dashboard.
    category_orders: dict[str, list] | None = None
    color_map: dict[str, str] | None = None

    if series:
        unique_series = agg[series].astype(str).unique().tolist()
        if series == "site":
            category_orders = {series: _site_order_for(unique_series)}
            color_map = _site_color_map(unique_series)
        elif stack_order == "sum_desc":
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
        title=None,
        category_orders=category_orders,
        color_discrete_map=color_map,
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


# ---------------------------------------------------------------------------
# Shorts funnel
# ---------------------------------------------------------------------------

def _format_pct(current: float, previous: float) -> str:
    if previous <= 0:
        return "—"
    return f"{(current / previous) * 100:.1f}%"


def _render_step_segments(step: FunnelStep) -> str:
    """Build the inner segmented bar for a single funnel step."""
    if step.total <= 0 or not step.by_site:
        return ""

    # Decide tier class based on width — matches your original logic.
    if step.width_pct <= 40:
        tier_cls = "tier-xs"
    elif step.width_pct <= 55:
        tier_cls = "tier-sm"
    elif step.width_pct <= 80:
        tier_cls = "tier-md"
    else:
        tier_cls = ""

    # Order sites canonically.
    ordered_sites = _site_order_for(list(step.by_site.keys()))

    parts: list[str] = [f'<div class="tbi-segments-row {tier_cls}">']
    for site_name in ordered_sites:
        value = step.by_site.get(site_name, 0)
        if value <= 0:
            continue

        pct = (value / step.total) * 100
        effective_pct = (pct * step.width_pct) / 100
        narrow_cls = ""
        if effective_pct < 4:
            narrow_cls = " tbi-very-narrow"
        elif effective_pct < 10:
            narrow_cls = " tbi-narrow"

        site_key = site_name.strip().lower()
        bg = SITE_BRAND_COLORS.get(site_key, "#1b6ca8")
        text_color = _site_text_color(site_name)

        style = (
            f"flex-basis:{pct}%;flex-grow:0;flex-shrink:0;"
            f"background:{bg};color:{text_color};"
        )

        parts.append(
            f'<div class="tbi-segment{narrow_cls}" style="{style}" '
            f'data-tip-site="{html.escape(site_name)}" '
            f'data-tip-value="{format_number(value)}" '
            f'data-tip-pct="{pct:.1f}%">'
            f'<span class="tbi-segment-name">{html.escape(site_name)}</span>'
            f'<span class="tbi-segment-value">{format_number(value)}</span>'
            f'<span class="tbi-segment-pct">{pct:.1f}%</span>'
            f"</div>"
        )

    parts.append("</div>")
    return "".join(parts)


def _render_step_html(step: FunnelStep, idx: int) -> str:
    cls = f"tbi-funnel-step tbi-step-{idx + 1}"
    return (
        f'<div class="{cls}">'
        f'<div class="tbi-step-header">'
        f'<div class="tbi-step-number">{format_number(step.total)}</div>'
        f'<div class="tbi-step-label">{html.escape(step.label)}</div>'
        f"</div>"
        f"{_render_step_segments(step)}"
        f"</div>"
    )


def _render_connector_html(prev_step: FunnelStep, curr_step: FunnelStep) -> str:
    """Per-site percentage badges between two steps."""
    sites = _site_order_for(list(set(prev_step.by_site) | set(curr_step.by_site)))
    parts: list[str] = ['<div class="tbi-funnel-connector">']
    any_emitted = False
    for site_name in sites:
        prev_v = prev_step.by_site.get(site_name, 0)
        curr_v = curr_step.by_site.get(site_name, 0)
        pct_text = _format_pct(curr_v, prev_v)
        if pct_text == "—":
            continue
        site_key = site_name.strip().lower()
        dot_color = SITE_BRAND_COLORS.get(site_key, "#888")
        parts.append(
            f'<span class="tbi-connector-badge">'
            f'<span class="tbi-cb-dot" style="background:{dot_color};"></span>'
            f'<span class="tbi-cb-name">{html.escape(site_name)}</span> {pct_text}'
            f"</span>"
        )
        any_emitted = True
    parts.append("</div>")
    return "".join(parts) if any_emitted else '<div class="tbi-funnel-connector"></div>'


def _render_shorts_funnel(
    df: pd.DataFrame,
    viz: dict[str, Any],
    *,
    title: str,
    subtitle: str,
) -> None:
    try:
        funnel = compute_shorts_funnel(df)
    except ValueError as e:
        st.warning(f"Funnel viz {title!r}: {e}")
        return

    steps: list[FunnelStep] = funnel["steps"]

    body_parts: list[str] = ['<div class="tbi-funnel-frame"><div class="tbi-funnel">']
    for idx, step in enumerate(steps):
        body_parts.append(_render_step_html(step, idx))
        if idx < len(steps) - 1:
            body_parts.append(_render_connector_html(step, steps[idx + 1]))
    body_parts.append("</div></div>")

    _open_card(title=title, subtitle=subtitle)
    st.markdown("".join(body_parts), unsafe_allow_html=True)
    _close_card()
