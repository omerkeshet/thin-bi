"""
Snowflake connection helper using key-pair authentication.

Reads credentials from st.secrets (which loads from .streamlit/secrets.toml
locally and from the Streamlit Cloud Secrets UI in production).

Usage:
    from engine.snowflake_client import get_connection, run_query

    df = run_query("SELECT CURRENT_VERSION()")
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def _load_private_key_bytes() -> bytes:
    """
    Load the PEM-formatted private key from st.secrets and convert it to
    the DER-encoded bytes that snowflake-connector-python expects.
    """
    pem_str: str = st.secrets["snowflake"]["private_key"]
    passphrase: str = st.secrets["snowflake"].get("private_key_passphrase", "")

    # The connector wants DER bytes, not a PEM string. Convert.
    password_bytes = passphrase.encode() if passphrase else None

    private_key = serialization.load_pem_private_key(
        pem_str.encode(),
        password=password_bytes,
        backend=default_backend(),
    )

    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def get_connection() -> snowflake.connector.SnowflakeConnection:
    """
    Open a new Snowflake connection. Caller is responsible for closing it,
    or use run_query() which handles that automatically.
    """
    cfg = st.secrets["snowflake"]
    return snowflake.connector.connect(
        account=cfg["account"],
        user=cfg["user"],
        private_key=_load_private_key_bytes(),
        warehouse=cfg["warehouse"],
        database=cfg["database"],
        schema=cfg["schema"],
        role=cfg["role"],
    )


def run_query(sql: str) -> pd.DataFrame:
    """
    Execute a SQL statement and return the results as a pandas DataFrame.
    Opens and closes a connection per call. Use this for one-off queries
    (like the connection test). Dashboard data loading will get its own
    cached function in a later step.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql)
            df = cur.fetch_pandas_all()
            return df
        finally:
            cur.close()
    finally:
        conn.close()
