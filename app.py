"""
Thin BI Portal — entry point.

Step 1 scope: prove that the deploy works, secrets are loaded, and key-pair
auth to Snowflake succeeds. UI is intentionally bare.
"""

import streamlit as st

from engine.snowflake_client import test_connection


st.set_page_config(
    page_title="Thin BI Portal",
    page_icon="📊",
    layout="wide",
)

st.title("Thin BI Portal")
st.caption("Step 1 — Snowflake connection test")

st.write(
    "Click the button below to verify that Streamlit Cloud can authenticate "
    "to Snowflake using the key-pair credentials stored in secrets."
)

if st.button("Test Snowflake connection", type="primary"):
    with st.spinner("Connecting to Snowflake..."):
        try:
            info = test_connection()
        except Exception as e:
            st.error(f"Connection failed: {type(e).__name__}: {e}")
            st.exception(e)
        else:
            st.success("Connected successfully ✅")
            st.write(
                {
                    "Snowflake version": info["version"],
                    "User": info["user"],
                    "Role": info["role"],
                    "Warehouse": info["warehouse"],
                    "Database": info["database"],
                    "Schema": info["schema"],
                }
            )
