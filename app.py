"""
Thin BI Portal — entry point.

Renders the sidebar dashboard menu and dispatches to the layout renderer
when a dashboard is selected.
"""

from __future__ import annotations

import streamlit as st

from engine.dashboard_registry import (
    Dashboard,
    Department,
    find_dashboard,
    scan_dashboards,
)
from engine.renderer import render_dashboard
from engine.snowflake_client import test_connection


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Thin BI Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Sidebar — dashboard navigation
# ---------------------------------------------------------------------------

SELECTED_KEY = "selected_dashboard_key"


def _render_sidebar(departments: tuple[Department, ...]) -> Dashboard | None:
    st.sidebar.title("📊 Thin BI Portal")

    if not departments:
        st.sidebar.info(
            "No dashboards found yet.\n\n"
            "Add folders under `dashboards/<department>/<name>/` "
            "with a `config.json` and `query.sql`."
        )
        _render_diagnostics()
        return None

    selected_key = st.session_state.get(SELECTED_KEY)

    for department in departments:
        st.sidebar.markdown(f"**{department.title}**")
        for dashboard in department.dashboards:
            is_selected = dashboard.key == selected_key
            label = (
                f"▸ {dashboard.dashboard_title}"
                if is_selected
                else dashboard.dashboard_title
            )
            if st.sidebar.button(
                label,
                key=f"nav_{dashboard.key}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                st.session_state[SELECTED_KEY] = dashboard.key
                st.rerun()
        st.sidebar.markdown("")

    selected_key = st.session_state.get(SELECTED_KEY)
    selected: Dashboard | None = None
    if selected_key is not None:
        selected = find_dashboard(selected_key)
        if selected is None:
            del st.session_state[SELECTED_KEY]

    _render_diagnostics()
    return selected


def _render_diagnostics() -> None:
    with st.sidebar.expander("🔧 Diagnostics", expanded=False):
        if st.button("Test Snowflake connection", key="diag_test_conn"):
            with st.spinner("Connecting to Snowflake..."):
                try:
                    info = test_connection()
                except Exception as e:
                    st.error(f"Connection failed: {type(e).__name__}: {e}")
                else:
                    st.success("Connected ✅")
                    st.json(info)

        st.divider()
        st.caption("Query size probe")

        if st.button("Probe Shorts query size", key="diag_probe_shorts"):
            from engine.snowflake_client import get_connection
            try:
                conn = get_connection()
                try:
                    cur = conn.cursor()
                    try:
                        cur.execute("""
                            SELECT
                                COUNT(*) AS row_count,
                                COUNT(DISTINCT "site") AS distinct_sites,
                                MIN(CAST("date" AS DATE)) AS min_date,
                                MAX(CAST("date" AS DATE)) AS max_date
                            FROM POC_DATABASE."domo"."shorts_all_sites_agg"
                            WHERE CAST("date" AS DATE) >= DATEADD(DAY, -7, CURRENT_DATE())
                        """)
                        row = cur.fetchone()
                    finally:
                        cur.close()
                finally:
                    conn.close()
            except Exception as e:
                st.error(f"Probe failed: {type(e).__name__}: {e}")
            else:
                st.success("Probed ✅")
                st.json({
                    "row_count": row[0],
                    "distinct_sites": row[1],
                    "min_date": str(row[2]),
                    "max_date": str(row[3]),
                })


# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

def _render_main(dashboard: Dashboard | None) -> None:
    if dashboard is None:
        st.title("Thin BI Portal")
        st.caption("Select a dashboard from the sidebar to begin.")
        st.info(
            "No dashboard selected yet. The sidebar lists every dashboard "
            "discovered under the `dashboards/` directory of this repo."
        )
        return

    render_dashboard(dashboard)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    departments = scan_dashboards()
    selected = _render_sidebar(departments)
    _render_main(selected)


main()
