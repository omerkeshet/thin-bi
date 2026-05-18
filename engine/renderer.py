"""
Layout renderer + chart factory (ECharts for bars, custom HTML for funnel).
"""

from __future__ import annotations

import html
from typing import Any

import pandas as pd
import streamlit as st
from streamlit_echarts import JsCode, st_echarts

from engine.dashboard_registry import Dashboard
from engine.data_loader import load_dashboard_data
from engine.filters import render_filters
from engine.funnel import compute_shorts_funnel, FunnelStep
from theme.echarts_theme import PALETTE, apply_theme, format_number


CHART_HEIGHT_PX = 360


# ---------------------------------------------------------------------------
# Site styling
# ---------------------------------------------------------------------------

SITE_BRAND_COLORS: dict[str, str] = {
    "mako": "#f5c518",
    "n12": "#cc1234",
    "v1": "#e84b2b",
}
SITE_TEXT_COLORS: dict[str, str] = {
    "mako": "#1a1a1a",
    "n12": "#ffffff",
    "v1": "#ffffff",
}
SITE_ORDER = ["v1", "mako", "n12"]


def _site_color_for(site: str) -> str | None:
    return SITE_BRAND_COLORS.get(str(site).strip().lower())


def _site_text_color(site: str) -> str:
    return SITE_TEXT_COLORS.get(str(site).strip().lower(), "#ffffff")


def _site_order_for(values: list[str]) -> list[str]:
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
    st.markdown(
        f'<div class="tbi-page-header">'
        f'<div class="tbi-page-title">{html.escape(dashboard.dashboard_title)}</div>'
        f'<div class="tbi-page-meta">{html.escape(dashboard.department_title)}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    description = dashboard.config.get("description")
    if description:
        st.markdown(
            f'<div class="tbi-page-description">{html.escape(description)}</div>',
            unsafe_allow_html=True,
        )

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

    filter_defs = dashboard.config.get("filters") or []
    df = render_filters(df, filter_defs, dashboard_key=dashboard.key)

    if df.empty:
        st.info("No data matches the current filter selection.")
        return

    layout = dashboard.config.get("layout") or []
    if not layout:
        st.warning("No `layout` defined in config.json.")
        with st.expander("Raw data preview"):
            st.dataframe(df.head(50), use_container_width=True)
        return

    for row_idx, row in enumerate(layout):
        if not isinstance(row, list) or not row:
            st.warning(f"Layout row #{row_idx} is empty or malformed.")
            continue
        cols = st.columns(len(row), gap="small")
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


def _open_card(title: str, subtitle: str = "") -> None:
    parts = ['<div class="tbi-card">']
    if title:
        parts.append(f'<div class="tbi-chart-title">{html.escape(title)}</div>')
    if subtitle:
        parts.append(f'<div class="tbi-chart-subtitle">{html.escape(subtitle)}</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def _close_card() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Bar chart (ECharts)
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
        st.warning(f"Bar viz {title!r}: column `{y}` not found.")
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


def _format_x_value(v: Any, x_is_date: bool) -> str:
    if x_is_date:
        ts = pd.to_datetime(v, errors="coerce")
        if pd.isna(ts):
            return str(v)
        return ts.strftime("%b %d")
    return str(v)


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
    series_col = transform.get("series")
    barmode = transform.get("barmode", "group")
    stack_order = transform.get("stack_order")

    if not x:
        st.warning(f"Bar viz {title!r}: requires `transform.x`.")
        return
    if x not in df.columns:
        st.warning(f"Bar viz {title!r}: column `{x}` not found.")
        return
    if series_col and series_col not in df.columns:
        st.warning(f"Bar viz {title!r}: series column `{series_col}` not found.")
        return

    measure = _resolve_measure(df, transform, title)
    if measure is None:
        return
    measure_series, measure_label = measure

    work = pd.DataFrame({x: df[x].values})
    if series_col:
        work[series_col] = df[series_col].values
    work[measure_label] = measure_series.values

    group_cols = [x] + ([series_col] if series_col else [])
    agg = (
        work.groupby(group_cols, dropna=False)[measure_label]
        .agg(aggfunc)
        .reset_index()
    )
    agg = agg.sort_values(by=group_cols)

    x_is_date = _is_date_like(agg[x])
    x_values_raw = list(agg[x].drop_duplicates().tolist())
    x_categories = [_format_x_value(v, x_is_date) for v in x_values_raw]

    # Build series list.
    series_list: list[dict[str, Any]] = []
    if series_col:
        unique_series = agg[series_col].astype(str).unique().tolist()
        if series_col == "site":
            ordered_series = _site_order_for(unique_series)
        elif stack_order == "sum_desc":
            totals = (
                agg.groupby(series_col, dropna=False)[measure_label]
                .sum()
                .sort_values(ascending=False)
            )
            ordered_series = totals.index.astype(str).tolist()
        else:
            ordered_series = sorted(unique_series)

        # Plot order for stacks: ECharts stacks bottom-to-top in the order
        # series are added. Largest goes first (bottom).
        for series_name in ordered_series:
            sub = agg[agg[series_col].astype(str) == str(series_name)]
            value_lookup = dict(zip(sub[x].tolist(), sub[measure_label].tolist()))
            data = [
                float(value_lookup.get(xv, 0) or 0) for xv in x_values_raw
            ]
            color = _site_color_for(series_name) if series_col == "site" else None
            entry = {
                "name": str(series_name),
                "type": "bar",
                "data": data,
                "barMaxWidth": 40,
                "emphasis": {"focus": "series"},
                "itemStyle": {"borderRadius": [2, 2, 0, 0]},
            }
            if barmode == "stack":
                entry["stack"] = "total"
            if color:
                entry["itemStyle"]["color"] = color
            series_list.append(entry)
    else:
        data = [float(v or 0) for v in agg[measure_label].tolist()]
        series_list.append({
            "name": measure_label,
            "type": "bar",
            "data": data,
            "barMaxWidth": 40,
            "itemStyle": {
                "color": PALETTE[0],
                "borderRadius": [2, 2, 0, 0],
            },
            "emphasis": {"focus": "series"},
        })

    # Tooltip formatter: branded, with K/M/B formatting on numeric values.
    tooltip_formatter = JsCode("""
        function (params) {
            if (!params || !params.length) return '';
            var fmt = function (n) {
                var a = Math.abs(n);
                if (a >= 1e9) return (n/1e9).toFixed(2)+'B';
                if (a >= 1e6) return (n/1e6).toFixed(2)+'M';
                if (a >= 1e3) return (n/1e3).toFixed(2)+'K';
                return Number(n).toLocaleString();
            };
            var header = '<div style="font-weight:600;color:#0F172A;margin-bottom:4px;">'
                       + params[0].axisValueLabel + '</div>';
            var rows = params.map(function (p) {
                return '<div style="display:flex;align-items:center;gap:6px;'
                     + 'font-size:12px;color:#475569;line-height:1.6;">'
                     + '<span style="width:8px;height:8px;border-radius:50%;'
                     + 'background:' + p.color + ';display:inline-block;"></span>'
                     + '<span style="flex:1;">' + p.seriesName + '</span>'
                     + '<span style="font-weight:600;color:#0F172A;">'
                     + fmt(p.value) + '</span></div>';
            }).join('');
            return header + rows;
        }
    """).js_code

    options: dict[str, Any] = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "formatter": {"_js": tooltip_formatter},
        },
        "legend": {"show": bool(series_col)},
        "xAxis": {"type": "category", "data": x_categories},
        "yAxis": {"type": "value"},
        "series": series_list,
    }

    options = apply_theme(options)

    _open_card(title=title, subtitle=subtitle)
    st_echarts(
        options=options,
        height=f"{CHART_HEIGHT_PX}px",
        key=f"echart::{title}::{x}::{series_col or ''}",
    )
    _close_card()


# ---------------------------------------------------------------------------
# Shorts funnel (unchanged HTML)
# ---------------------------------------------------------------------------

def _format_pct(current: float, previous: float) -> str:
    if previous <= 0:
        return "—"
    return f"{(current / previous) * 100:.1f}%"


def _render_step_segments(step: FunnelStep) -> str:
    if step.total <= 0 or not step.by_site:
        return ""

    if step.width_pct <= 40:
        tier_cls = "tier-xs"
    elif step.width_pct <= 55:
        tier_cls = "tier-sm"
    elif step.width_pct <= 80:
        tier_cls = "tier-md"
    else:
        tier_cls = ""

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
