"""
Per-dashboard SQL execution + caching.

Each dashboard's query.sql is read from disk and executed against
Snowflake exactly once per (dashboard key, sql contents) pair, then
the resulting pandas DataFrame is cached for the rest of the session
(or until Streamlit invalidates the cache).

Column names are lowercased at this boundary so that config.json
files can refer to columns in lowercase regardless of how Snowflake
returns them.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from engine.dashboard_registry import Dashboard
from engine.snowflake_client import get_connection


def _read_sql_file(dashboard: Dashboard) -> str:
    return dashboard.query_path.read_text(encoding="utf-8").strip()


# The cache key is (dashboard.key, sql_text). If the SQL file changes
# on disk between deploys, sql_text changes and we get a fresh fetch.
@st.cache_data(show_spinner=False, ttl=600)
def _run_query(dashboard_key: str, sql_text: str) -> pd.DataFrame:
    """Execute SQL against Snowflake and return a DataFrame."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql_text)
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
        finally:
            cur.close()
    finally:
        conn.close()

    df = pd.DataFrame(rows, columns=cols)
    df.columns = [c.lower() for c in df.columns]
    return df


def load_dashboard_data(dashboard: Dashboard) -> pd.DataFrame:
    """
    Public entry point. Returns a cached DataFrame for the given dashboard.
    """
    sql_text = _read_sql_file(dashboard)
    return _run_query(dashboard.key, sql_text)
