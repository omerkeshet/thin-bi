"""
Plotly theme for the Thin BI Portal.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio


THEME_NAME = "thinbi"

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

_INK = "#0F172A"
_INK_SOFT = "#475569"
_GRID = "#E2E8F0"
_AXIS = "#CBD5E1"
_PAPER = "rgba(0,0,0,0)"


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
            paper_bgcolor=_PAPER,
            plot_bgcolor=_PAPER,
            # No top margin needed for a title — title is rendered as HTML
            # above the chart by the renderer. Bottom margin leaves room
            # for the horizontal legend.
            margin=dict(l=8, r=8, t=8, b=56),
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor=_AXIS,
                linewidth=1,
                ticks="outside",
                tickcolor=_AXIS,
                ticklen=4,
                tickfont=dict(color=_INK_SOFT, size=12),
                title=dict(text="", font=dict(color=_INK_SOFT, size=12)),
                zeroline=False,
                automargin=True,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=_GRID,
                gridwidth=1,
                showline=False,
                ticks="",
                tickfont=dict(color=_INK_SOFT, size=12),
                title=dict(text="", font=dict(color=_INK_SOFT, size=12)),
                zeroline=False,
                automargin=True,
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.18,
                xanchor="center",
                x=0.5,
                font=dict(size=12, color=_INK_SOFT),
                bgcolor="rgba(0,0,0,0)",
                title=dict(text=""),
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
    pio.templates[THEME_NAME] = _build_template()
    pio.templates.default = THEME_NAME


def format_number(n: float) -> str:
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
    Per-chart finishing touches. Call after constructing px.bar/etc.
    The chart title is NOT set here — the renderer draws it as HTML
    above the chart so the Plotly canvas has the full vertical space.
    """
    fig.update_yaxes(tickformat="~s")

    if x_is_date:
        fig.update_xaxes(
            tickformat="%b %d",
            ticks="outside",
            tickangle=0,
            showgrid=False,
        )
        fig.update_layout(hovermode="x unified")
    else:
        fig.update_layout(hovermode="closest")

    fig.update_layout(yaxis=dict(hoverformat=",.0f"))
