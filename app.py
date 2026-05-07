"""
OmerBI — entry point.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from engine.auth import render_logout_button, require_auth
from engine.dashboard_registry import (
    Dashboard,
    Department,
    find_dashboard,
    scan_dashboards,
)
from engine.renderer import render_dashboard
from engine.snowflake_client import test_connection
from theme.page_style import (
    apply_page_style,
    render_app_header,
    render_landing_logo,
    render_sidebar_logo,
)
from theme.plotly_theme import register_theme


# ---------------------------------------------------------------------------
# Logo
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent
_LOGO_PATH = _REPO_ROOT / "assets" / "logo.svg"


# ---------------------------------------------------------------------------
# Page config + global styling
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="OmerBI",
    page_icon=str(_LOGO_PATH) if _LOGO_PATH.is_file() else "📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_page_style()
register_theme()


# ---------------------------------------------------------------------------
# Auth gate — runs before anything else
# ---------------------------------------------------------------------------

if not require_auth():
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar — dashboard navigation
# ---------------------------------------------------------------------------

SELECTED_KEY = "selected_dashboard_key"


def _render_sidebar(departments: tuple[Department, ...]) -> Dashboard | None:
    render_sidebar_logo(_LOGO_PATH, brand_name="OmerBI")

    if not departments:
        st.sidebar.info(
            "No dashboards found yet.\n\n"
            "Add folders under `dashboards/<department>/<name>/` "
            "with a `config.json` and `query.sql`."
        )
        _render_sidebar_footer()
        return None

    selected_key = st.session_state.get(SELECTED_KEY)

    for department in departments:
        st.sidebar.markdown(f"**{department.title}**")
        for dashboard in department.dashboards:
            is_selected = dashboard.key == selected_key
            if st.sidebar.button(
                dashboard.dashboard_title,
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

    _render_sidebar_footer()
    return selected


def _render_sidebar_footer() -> None:
    """Diagnostics + sign out, anchored at the bottom of the sidebar."""
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

    st.sidebar.markdown("---")
    render_logout_button()


# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------

def _render_main(dashboard: Dashboard | None) -> None:
    if dashboard is None:
        render_landing_logo(_LOGO_PATH)
        render_app_header(
            "Welcome",
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
