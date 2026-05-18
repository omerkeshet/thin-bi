"""
ECharts theme for the OmerBI portal.

Exposes:
- PALETTE: ordered list of categorical colors.
- THEME: a dict of ECharts options to merge into every chart.
- apply_theme(opt): merge THEME into a chart-specific options dict.
- format_number(n): "1234567" -> "1.23M".
"""

from __future__ import annotations

from typing import Any


PALETTE: list[str] = [
    "#2563EB",  # blue-600
    "#10B981",  # emerald-500
    "#F59E0B",  # amber-500
    "#8B5CF6",  # violet-500
    "#EC4899",  # pink-500
    "#14B8A6",  # teal-500
    "#EF4444",  # red-500
    "#64748B",  # slate-500
]

_TEXT = "#0F172A"
_TEXT_SOFT = "#64748B"
_BORDER = "#E2E8F0"
_GRID = "#F1F5F9"

_FONT = (
    "Inter, -apple-system, BlinkMacSystemFont, "
    "'Segoe UI', Roboto, sans-serif"
)


THEME: dict[str, Any] = {
    "color": PALETTE,
    "textStyle": {"fontFamily": _FONT, "color": _TEXT, "fontSize": 12},
    "grid": {
        "left": 8,
        "right": 16,
        "top": 16,
        "bottom": 8,
        "containLabel": True,
    },
    "xAxis": {
        "axisLine": {"show": True, "lineStyle": {"color": _BORDER}},
        "axisTick": {"show": True, "lineStyle": {"color": _BORDER}},
        "axisLabel": {"color": _TEXT_SOFT, "fontSize": 11},
        "splitLine": {"show": False},
    },
    "yAxis": {
        "axisLine": {"show": False},
        "axisTick": {"show": False},
        "axisLabel": {
            "color": _TEXT_SOFT,
            "fontSize": 11,
            # ECharts has no native ~s SI formatter; we feed JS for K/M/B.
            "formatter": {"_js": (
                "function (v) {"
                "  var a = Math.abs(v);"
                "  if (a >= 1e9) return (v/1e9).toFixed(2)+'B';"
                "  if (a >= 1e6) return (v/1e6).toFixed(2)+'M';"
                "  if (a >= 1e3) return (v/1e3).toFixed(1)+'K';"
                "  return v;"
                "}"
            )},
        },
        "splitLine": {"show": True, "lineStyle": {"color": _GRID}},
    },
    "legend": {
        "type": "scroll",
        "bottom": 0,
        "left": "center",
        "icon": "circle",
        "itemWidth": 8,
        "itemHeight": 8,
        "itemGap": 14,
        "textStyle": {"color": _TEXT_SOFT, "fontSize": 11},
    },
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "shadow"},
        "backgroundColor": "#FFFFFF",
        "borderColor": _BORDER,
        "borderWidth": 1,
        "padding": [8, 12],
        "textStyle": {"color": _TEXT, "fontSize": 12, "fontFamily": _FONT},
        "extraCssText": "box-shadow: 0 2px 8px rgba(15,23,42,0.10);",
    },
}


def apply_theme(opt: dict[str, Any]) -> dict[str, Any]:
    """
    Merge the theme into a chart-specific options dict. Chart options
    take precedence on a per-key basis; nested dicts are shallow-merged.
    """
    merged: dict[str, Any] = {}
    for key, value in THEME.items():
        if key in opt and isinstance(value, dict) and isinstance(opt[key], dict):
            merged[key] = {**value, **opt[key]}
        else:
            merged[key] = value
    for key, value in opt.items():
        if key not in merged:
            merged[key] = value
    return merged


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
