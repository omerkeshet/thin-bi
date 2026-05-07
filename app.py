"""
Thin BI Portal — entry point.
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
from theme.page_style import apply_page_style, render_app_header
from theme.plotly_theme import register_theme


# ---------------------------------------------------------------------------
# Page config + global styling
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Thin BI Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_page_style()
register_theme()


# ---------------------------------------------------------------------------
# Sidebar — dashboard navigation
# ---------------------------------------------------------------------------

SELECTED_KEY = "selected_dashboard_key"


def _render_sidebar(departments: tuple[Department, ...]) -> Dashboard | None:
    st.sidebar.markdown(
        """
        <div style="
            font-size: 1.25rem;
            font-weight: 700;
            color: #0F172A;
            letter-spacing: -0.01em;
            margin-bottom: 1.5rem;
        ">📊 Thin BI Portal</div>
        """,
        unsafe_allow_html=True,
    )

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
            label = dashboard.dashboard_title
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
            with st.spinner("Connecting..."):
                try:
                    info = test_connection()
                except Exception as e:
                    st.error(f"Connection failed: {type(e).__name__}: {e}")
                else:
                    st.success("Connected ✅")
                    st.json(info)


# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

def _render_main(dashboard: Dashboard | None) -> None:
    if dashboard is None:
        render_app_header(
            "Thin BI Portal",
            "Select a dashboard from the sidebar to begin.",
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
