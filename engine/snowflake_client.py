"""
Snowflake client using key-pair authentication.

Reads connection parameters from st.secrets["snowflake"], converts the
PEM-formatted private key into DER bytes, and returns a live connection.
"""

from __future__ import annotations

import streamlit as st
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import snowflake.connector


def _load_private_key_der() -> bytes:
    """
    Read the PEM private key from st.secrets and convert it to DER bytes,
    which is the format snowflake-connector-python expects for key-pair auth.
    """
    cfg = st.secrets["snowflake"]
    pem_str: str = cfg["private_key"]
    passphrase_str: str = cfg.get("private_key_passphrase", "") or ""

    # Encode the PEM text to bytes for the cryptography lib.
    pem_bytes = pem_str.encode("utf-8")
    password_bytes = passphrase_str.encode("utf-8") if passphrase_str else None

    private_key = serialization.load_pem_private_key(
        pem_bytes,
        password=password_bytes,
        backend=default_backend(),
    )

    # Snowflake wants DER-encoded PKCS8, unencrypted.
    der_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return der_bytes


def get_connection() -> snowflake.connector.SnowflakeConnection:
    """
    Open a fresh Snowflake connection using key-pair auth.
    Caller is responsible for closing it.
    """
    cfg = st.secrets["snowflake"]
    der_bytes = _load_private_key_der()

    conn = snowflake.connector.connect(
        account=cfg["account"],
        user=cfg["user"],
        private_key=der_bytes,
        warehouse=cfg["warehouse"],
        database=cfg["database"],
        schema=cfg["schema"],
        role=cfg["role"],
        client_session_keep_alive=False,
    )
    return conn


def test_connection() -> dict:
    """
    Run a trivial query to confirm auth + warehouse + role all work.
    Returns a dict with version, current user/role/warehouse/db/schema.
    Raises on failure — let the caller catch and display.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT "
                "CURRENT_VERSION(), "
                "CURRENT_USER(), "
                "CURRENT_ROLE(), "
                "CURRENT_WAREHOUSE(), "
                "CURRENT_DATABASE(), "
                "CURRENT_SCHEMA()"
            )
            row = cur.fetchone()
        finally:
            cur.close()
    finally:
        conn.close()

    return {
        "version": row[0],
        "user": row[1],
        "role": row[2],
        "warehouse": row[3],
        "database": row[4],
        "schema": row[5],
    }
