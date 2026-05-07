"""
Thin BI Portal — entry point.

Step 2 scope:
- Scan dashboards/ folder.
- Render a sidebar menu grouped by department.
- Show a placeholder for the selected dashboard in the main panel.
- Keep a Snowflake connection-test diagnostic available in the sidebar.
"""

from __future__ import annotations

import streamlit as st

from engine.dashboard_registry import (
    Dashboard,
    Department,
    find_dashboard,
    scan_dashboards,
)
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

    # Build (label, dashboard) pairs across all departments.
    selected: Dashboard | None = None
    selected_key = st.session_state.get(SELECTED_KEY)

    for department in departments:
        st.sidebar.markdown(f"**{department.title}**")
        for dashboard in department.dashboards:
            is_selected = dashboard.key == selected_key
            # Using buttons (rather than radio) keeps each row distinct
            # and lets us highlight the active one.
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
        st.sidebar.markdown("")  # spacer between departments

    # Resolve the active dashboard after potential rerun.
    selected_key = st.session_state.get(SELECTED_KEY)
    if selected_key is not None:
        selected = find_dashboard(selected_key)
        if selected is None:
            # Stale key (e.g. dashboard removed in a deploy). Clear it.
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
        st.caption("Schema inspection (temporary, step 3a)")

        table_fqn = st.text_input(
            "Table to inspect",
            value="PUBLIC.ANNOTATIONS",
            key="diag_table_fqn",
            help="Fully-qualified or schema-qualified table name.",
        )

        if st.button("Describe table", key="diag_describe"):
            from engine.snowflake_client import get_connection
            try:
                conn = get_connection()
                try:
                    cur = conn.cursor()
                    try:
                        cur.execute(f"DESCRIBE TABLE {table_fqn}")
                        cols = [d[0] for d in cur.description]
                        rows = cur.fetchall()
                    finally:
                        cur.close()
                finally:
                    conn.close()
            except Exception as e:
                st.error(f"DESCRIBE failed: {type(e).__name__}: {e}")
            else:
                import pandas as pd
                st.success(f"{len(rows)} columns")
                st.dataframe(
                    pd.DataFrame(rows, columns=cols),
                    use_container_width=True,
                    hide_index=True,
                )

        if st.button("Sample rows (5)", key="diag_sample"):
            from engine.snowflake_client import get_connection
            try:
                conn = get_connection()
                try:
                    cur = conn.cursor()
                    try:
                        cur.execute(f"SELECT * FROM {table_fqn} LIMIT 5")
                        cols = [d[0] for d in cur.description]
                        rows = cur.fetchall()
                    finally:
                        cur.close()
                finally:
                    conn.close()
            except Exception as e:
                st.error(f"Sample failed: {type(e).__name__}: {e}")
            else:
                import pandas as pd
                st.dataframe(
                    pd.DataFrame(rows, columns=cols),
                    use_container_width=True,
                    hide_index=True,
                )

        if st.button("Row count", key="diag_count"):
            from engine.snowflake_client import get_connection
            try:
                conn = get_connection()
                try:
                    cur = conn.cursor()
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM {table_fqn}")
                        (count,) = cur.fetchone()
                    finally:
                        cur.close()
                finally:
                    conn.close()
            except Exception as e:
                st.error(f"Count failed: {type(e).__name__}: {e}")
            else:
                st.metric("Rows", f"{count:,}")


# ---------------------------------------------------------------------------
# Main panel — dashboard placeholder (real renderer arrives in step 5)
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

    st.title(dashboard.dashboard_title)
    st.caption(f"{dashboard.department_title} · `{dashboard.key}`")

    description = dashboard.config.get("description")
    if description:
        st.write(description)

    # Step-2 placeholder: prove we resolved the right dashboard. This
    # whole block disappears in step 5 when the real renderer lands.
    with st.expander("Dashboard metadata (debug)", expanded=False):
        st.write(
            {
                "key": dashboard.key,
                "config_path": str(dashboard.config_path),
                "query_path": str(dashboard.query_path),
            }
        )
        st.markdown("**config.json**")
        st.json(dashboard.config)
        st.markdown("**query.sql**")
        try:
            sql_text = dashboard.query_path.read_text(encoding="utf-8")
        except OSError as e:
            st.error(f"Could not read query.sql: {e}")
        else:
            st.code(sql_text, language="sql")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    departments = scan_dashboards()
    selected = _render_sidebar(departments)
    _render_main(selected)


main()
