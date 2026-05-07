"""
Plotly theme for the Thin BI Portal.

Exposes:
- THEME_NAME: the registered Plotly template name to set as default.
- PALETTE: ordered list of categorical colors for series (sites, etc.).
- format_number(n): "1234567" → "1.23M".
- apply_chart_polish(fig, *, x_is_date=False): per-chart finishing touches
  (number-formatted axis ticks, unified hover, legend placement, margins).
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio


THEME_NAME = "thinbi"

# A deliberate palette — deeper, more saturated than Plotly defaults,
# designed to read well on both light and dark backgrounds and to
# remain distinguishable up to ~10 series.
PALETTE: list[str] = [
    "#2E5BFF",  # blue
    "#00C2A8",  # teal
    "#FF8C42",  # orange
    "#8B5CF6",  # violet
    "#F4B400",  # amber
    "#EA4C89",  # pink
    "#22C55E",  # green
    "#0EA5E9",  # sky
    "#EF4444",  # red
    "#64748B",  # slate
]

# Neutral grays for axes, gridlines, text. Tuned for a light page.
_INK = "#0F172A"          # primary text (slate-900)
_INK_SOFT = "#475569"     # secondary text (slate-600)
_GRID = "#E2E8F0"         # gridline (slate-200)
_AXIS = "#CBD5E1"         # axis line (slate-300)
_PAPER = "rgba(0,0,0,0)"  # transparent so Streamlit's bg shows through


def _build_template() -> go.layout.Template:
    return go.layout.Template(
        layout=go.Layout(
            colorway=PALETTE,
            font=dict(
                family=(
                    "Inter, -apple-system, BlinkMacSystemFont, "
                    "'Segoe UI', Roboto, sans-serif"
                ),
                size=13,
                color=_INK,
            ),
            title=dict(
                font=dict(size=15, color=_INK, family="Inter, sans-serif"),
                x=0.0,
                xanchor="left",
                pad=dict(t=4, b=8),
            ),
            paper_bgcolor=_PAPER,
            plot_bgcolor=_PAPER,
            margin=dict(l=12, r=12, t=44, b=12),
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor=_AXIS,
                linewidth=1,
                ticks="outside",
                tickcolor=_AXIS,
                ticklen=4,
                tickfont=dict(color=_INK_SOFT, size=12),
                title=dict(font=dict(color=_INK_SOFT, size=12)),
                zeroline=False,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=_GRID,
                gridwidth=1,
                showline=False,
                ticks="",
                tickfont=dict(color=_INK_SOFT, size=12),
                title=dict(font=dict(color=_INK_SOFT, size=12)),
                zeroline=False,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0.0,
                font=dict(size=12, color=_INK_SOFT),
                bgcolor="rgba(0,0,0,0)",
                title=dict(text=""),  # legend title repeats the color column;
                                       # we suppress it for a cleaner look.
            ),
            hoverlabel=dict(
                bgcolor="white",
                bordercolor=_AXIS,
                font=dict(size=12, color=_INK, family="Inter, sans-serif"),
            ),
            bargap=0.25,
            bargroupgap=0.05,
        )
    )


def register_theme() -> None:
    """Register and activate the theme as Plotly's default template."""
    pio.templates[THEME_NAME] = _build_template()
    pio.templates.default = THEME_NAME


def format_number(n: float) -> str:
    """
    Compact human-readable number: 1234 → '1.23K', 1_234_567 → '1.23M'.
    Used in hover tooltips and KPI tiles.
    """
    try:
        n = float(n)
    except (TypeError, ValueError):
        return str(n)
    abs_n = abs(n)
    if abs_n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    if abs_n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if abs_n >= 1_000:
        return f"{n / 1_000:.2f}K"
    if abs_n >= 1 or n == 0:
        return f"{n:,.0f}"
    return f"{n:.2f}"


def apply_chart_polish(fig, *, x_is_date: bool = False) -> None:
    """
    Per-chart finishing: numeric ticks formatted as K/M/B, unified hover
    for time-series, smart x-axis ticks for dates, tight category gaps.
    Call after constructing a px.bar / px.line / etc.
    """
    # Tickformat 's' uses SI prefixes (k, M, G). Plotly's `~s` strips
    # trailing zeros, e.g. 1.0M → 1M.
    fig.update_yaxes(tickformat="~s")

    if x_is_date:
        fig.update_xaxes(
            tickformat="%b %d",       # e.g. "May 07"
            ticks="outside",
            tickangle=0,
            showgrid=False,
        )
        fig.update_layout(hovermode="x unified")
    else:
        fig.update_layout(hovermode="closest")

    # Hover formatting: thousand separators on the y value.
    # Most px.* charts already wire hovertemplate; we override yaxis hoverformat
    # for cases that fall back to defaults.
    fig.update_layout(yaxis=dict(hoverformat=",.0f"))
