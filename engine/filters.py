"""
Filter widgets — render filter UI from config and apply to the DataFrame.

Filters operate purely in-memory on the already-cached dashboard DataFrame.
They never trigger a re-query.

Schema (in config.json under top-level "filters"):
    "filters": [
        { "type": "date_range", "column": "date", "label": "Date range" },
        { "type": "multiselect", "column": "site", "label": "Site" }
    ]
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd
import streamlit as st


def _state_key(dashboard_key: str, column: str, suffix: str) -> str:
    return f"filter::{dashboard_key}::{column}::{suffix}"


def render_filters(
    df: pd.DataFrame,
    filter_defs: list[dict[str, Any]],
    dashboard_key: str,
) -> pd.DataFrame:
    """
    Render filter widgets in a horizontal row at the top of the page.
    Returns the filtered DataFrame.
    """
    if not filter_defs:
        return df

    # Wrap in a styled container so the filter row reads as a unit.
    st.markdown('<div class="tbi-filter-bar">', unsafe_allow_html=True)
    cols = st.columns(len(filter_defs), gap="medium")
    filtered = df

    for col_widget, fdef in zip(cols, filter_defs):
        with col_widget:
            ftype = (fdef.get("type") or "").lower()
            column = fdef.get("column")
            label = fdef.get("label") or column or "Filter"

            if not column:
                st.warning(f"Filter {label!r}: `column` is required.")
                continue
            if column not in df.columns:
                st.warning(
                    f"Filter {label!r}: column `{column}` not in data. "
                    f"Available: {list(df.columns)}"
                )
                continue

            if ftype == "date_range":
                filtered = _apply_date_range(
                    filtered, df, column, label, dashboard_key
                )
            elif ftype == "multiselect":
                filtered = _apply_multiselect(
                    filtered, df, column, label, dashboard_key, fdef
                )
            else:
                st.warning(f"Unknown filter type: `{ftype}` (filter: {label!r})")

    st.markdown("</div>", unsafe_allow_html=True)

    # Visual feedback on what was filtered out.
    if len(filtered) != len(df):
        st.caption(
            f"Showing {len(filtered):,} of {len(df):,} rows after filters."
        )

    return filtered


# ---------------------------------------------------------------------------
# Filter implementations
# ---------------------------------------------------------------------------

def _to_date(val: Any) -> date | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    try:
        return pd.to_datetime(val).date()
    except (ValueError, TypeError):
        return None


def _apply_date_range(
    df: pd.DataFrame,
    full_df: pd.DataFrame,
    column: str,
    label: str,
    dashboard_key: str,
) -> pd.DataFrame:
    series = pd.to_datetime(full_df[column], errors="coerce")
    valid = series.dropna()
    if valid.empty:
        st.warning(f"Filter {label!r}: column `{column}` has no parseable dates.")
        return df

    data_min = valid.min().date()
    data_max = valid.max().date()

    state_key = _state_key(dashboard_key, column, "range")
    default = st.session_state.get(state_key, (data_min, data_max))

    selection = st.date_input(
        label,
        value=default,
        min_value=data_min,
        max_value=data_max,
        key=state_key,
    )

    # Streamlit returns a tuple (start, end) for ranges, or a single date
    # if the user has only picked one endpoint so far.
    if isinstance(selection, tuple):
        start = _to_date(selection[0]) if len(selection) > 0 else data_min
        end = _to_date(selection[1]) if len(selection) > 1 else start
    else:
        start = _to_date(selection)
        end = start

    if start is None or end is None:
        return df

    df_dates = pd.to_datetime(df[column], errors="coerce").dt.date
    mask = (df_dates >= start) & (df_dates <= end)
    return df[mask]


def _apply_multiselect(
    df: pd.DataFrame,
    full_df: pd.DataFrame,
    column: str,
    label: str,
    dashboard_key: str,
    fdef: dict[str, Any],
) -> pd.DataFrame:
    options = sorted(
        v for v in full_df[column].dropna().astype(str).unique().tolist()
    )

    # Optional canonical ordering, e.g. for sites.
    order_hint = fdef.get("order")
    if isinstance(order_hint, list):
        ordered = [o for o in order_hint if o in options]
        ordered.extend(o for o in options if o not in ordered)
        options = ordered

    state_key = _state_key(dashboard_key, column, "selected")
    default = st.session_state.get(state_key, options)

    # Validate stale state values that no longer exist in data.
    default = [d for d in default if d in options] or options

    selection = st.multiselect(
        label,
        options=options,
        default=default,
        key=state_key,
    )

    if not selection:
        # Empty selection = no filter applied (otherwise the page goes blank
        # and the user has to remember the column name to recover).
        return df

    return df[df[column].astype(str).isin(selection)]
