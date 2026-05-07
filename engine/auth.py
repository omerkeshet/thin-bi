"""
Simple shared-credential auth gate.

Reads expected username/password from st.secrets["app_auth"]. Sets
st.session_state["auth_ok"] = True on a successful login. The gate
short-circuits the rest of the app on failure.

This is intentionally minimal — single shared credential, no users table,
no password hashing. Suitable for a hackathon demo behind a private link.
Do NOT use this pattern for anything that needs real security.
"""

from __future__ import annotations

import hmac
import time

import streamlit as st


_SESSION_KEY = "auth_ok"
_ATTEMPT_KEY = "auth_attempts"
_LAST_FAIL_KEY = "auth_last_fail_ts"
_LOCKOUT_SECONDS = 5  # tiny throttle to discourage idle bruteforcing


def _get_expected_credentials() -> tuple[str, str] | None:
    """Pull (username, password) from secrets. Returns None if unconfigured."""
    try:
        section = st.secrets["app_auth"]
    except (KeyError, FileNotFoundError):
        return None
    username = section.get("username")
    password = section.get("password")
    if not username or not password:
        return None
    return str(username), str(password)


def _constant_time_match(a: str, b: str) -> bool:
    """Compare two strings without leaking length/content via timing."""
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def _render_login_form() -> None:
    """Render the centered login card. Sets session state on success."""
    # Three columns to center the form on wide screens.
    left, center, right = st.columns([1, 1.2, 1])
    with center:
        st.markdown(
            """
            <div class="tbi-auth-card">
              <div class="tbi-auth-title">OmerBI</div>
              <div class="tbi-auth-subtitle">Sign in to continue</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("auth_form", clear_on_submit=False):
            username = st.text_input("Username", autocomplete="username")
            password = st.text_input(
                "Password", type="password", autocomplete="current-password"
            )
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)

        if submitted:
            _handle_submit(username, password)


def _handle_submit(username: str, password: str) -> None:
    expected = _get_expected_credentials()
    if expected is None:
        st.error(
            "Authentication is not configured. Add an [app_auth] section "
            "with `username` and `password` to Streamlit secrets."
        )
        return

    # Soft throttle: if there have been recent failures, make the user wait.
    last_fail = st.session_state.get(_LAST_FAIL_KEY, 0.0)
    if time.time() - last_fail < _LOCKOUT_SECONDS:
        wait = _LOCKOUT_SECONDS - int(time.time() - last_fail)
        st.warning(f"Please wait {wait}s before trying again.")
        return

    expected_user, expected_pw = expected
    user_ok = _constant_time_match(username or "", expected_user)
    pw_ok = _constant_time_match(password or "", expected_pw)

    if user_ok and pw_ok:
        st.session_state[_SESSION_KEY] = True
        st.session_state.pop(_ATTEMPT_KEY, None)
        st.session_state.pop(_LAST_FAIL_KEY, None)
        st.rerun()
    else:
        st.session_state[_ATTEMPT_KEY] = st.session_state.get(_ATTEMPT_KEY, 0) + 1
        st.session_state[_LAST_FAIL_KEY] = time.time()
        st.error("Incorrect username or password.")


def require_auth() -> bool:
    """
    Gate function. Call early in app.py. Returns True if the user is
    authenticated; False if the login form was rendered instead. The
    caller should `return` (or otherwise short-circuit) on False.
    """
    if st.session_state.get(_SESSION_KEY) is True:
        return True
    _render_login_form()
    return False


def render_logout_button(location="sidebar") -> None:
    """A small 'Sign out' control. Use in the sidebar."""
    target = st.sidebar if location == "sidebar" else st
    if target.button("Sign out", key="auth_signout", use_container_width=True):
        for key in (_SESSION_KEY, _ATTEMPT_KEY, _LAST_FAIL_KEY):
            st.session_state.pop(key, None)
        st.rerun()
