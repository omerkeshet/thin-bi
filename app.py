"""
Thin BI Portal — connection test.

Step 1 goal: prove we can connect to Snowflake with key-pair auth before
building any engine logic. Click the button, see the version string.
"""

import streamlit as st

from engine.snowflake_client import run_query

st.set_page_config(page_title="Thin BI — Connection Test", page_icon="❄️")

st.title("Thin BI — Connection Test")
st.caption("Step 1: verify Snowflake key-pair auth works before building the engine.")

if st.button("Test Snowflake connection", type="primary"):
    try:
        with st.spinner("Connecting to Snowflake..."):
            df = run_query("SELECT CURRENT_VERSION() AS version, CURRENT_USER() AS user, CURRENT_ROLE() AS role, CURRENT_WAREHOUSE() AS warehouse")
        st.success("Connected.")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Connection failed: {type(e).__name__}")
        st.exception(e)
