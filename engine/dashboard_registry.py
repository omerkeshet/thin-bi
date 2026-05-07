"""
Dashboard registry — scans the `dashboards/` directory and produces a
structured catalog of available dashboards, grouped by department.

A dashboard is a folder at `dashboards/<department>/<name>/` containing
both `config.json` and `query.sql`. Anything else is ignored.

Scan results are cached for the lifetime of the Streamlit process via
@st.cache_resource so the filesystem isn't re-walked on every rerun.
Bumping the cache requires a server restart (or pushing a new commit,
which Streamlit Cloud restarts automatically).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import streamlit as st


# Repo root — this file lives at <root>/engine/dashboard_registry.py
_REPO_ROOT = Path(__file__).resolve().parent.parent
_DASHBOARDS_DIR = _REPO_ROOT / "dashboards"


@dataclass(frozen=True)
class Dashboard:
    """A single dashboard discovered on disk."""

    # Stable identifier: "<department_slug>/<dashboard_slug>", used as
    # the session-state key and as the menu option value.
    key: str

    department_slug: str  # folder name under dashboards/
    dashboard_slug: str   # folder name under dashboards/<department>/

    # Display names from config.json, falling back to slug-based titles.
    department_title: str
    dashboard_title: str

    # Absolute paths to the two files.
    config_path: Path
    query_path: Path

    # Full parsed config.json — handed to later steps as-is.
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Department:
    """A department grouping in the sidebar menu."""

    slug: str
    title: str
    dashboards: tuple[Dashboard, ...]


def _slug_to_title(slug: str) -> str:
    """Fallback display name when config.json doesn't supply one."""
    return slug.replace("_", " ").replace("-", " ").strip().title()


def _load_dashboard(
    department_slug: str,
    dashboard_dir: Path,
) -> Dashboard | None:
    """Try to build a Dashboard from a folder. Returns None if invalid."""
    config_path = dashboard_dir / "config.json"
    query_path = dashboard_dir / "query.sql"

    if not config_path.is_file() or not query_path.is_file():
        return None

    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        # Surface the bad config in the UI later via the registry's errors,
        # but don't crash the whole menu.
        st.warning(
            f"Skipping dashboard `{department_slug}/{dashboard_dir.name}`: "
            f"could not parse config.json ({e})"
        )
        return None

    if not isinstance(config, dict):
        st.warning(
            f"Skipping dashboard `{department_slug}/{dashboard_dir.name}`: "
            f"config.json must be a JSON object."
        )
        return None

    dashboard_slug = dashboard_dir.name
    dashboard_title = config.get("title") or _slug_to_title(dashboard_slug)
    department_title = (
        config.get("department_title") or _slug_to_title(department_slug)
    )

    return Dashboard(
        key=f"{department_slug}/{dashboard_slug}",
        department_slug=department_slug,
        dashboard_slug=dashboard_slug,
        department_title=department_title,
        dashboard_title=dashboard_title,
        config_path=config_path,
        query_path=query_path,
        config=config,
    )


@st.cache_resource(show_spinner=False)
def scan_dashboards() -> tuple[Department, ...]:
    """
    Walk the dashboards/ directory and return a tuple of Department
    objects, each containing the dashboards found under it.

    Departments and dashboards are sorted alphabetically by their
    display title for a stable menu order.
    """
    if not _DASHBOARDS_DIR.is_dir():
        return ()

    departments: list[Department] = []

    for dept_dir in sorted(_DASHBOARDS_DIR.iterdir()):
        if not dept_dir.is_dir():
            continue
        if dept_dir.name.startswith((".", "_")):
            continue

        dashboards: list[Dashboard] = []
        for dash_dir in sorted(dept_dir.iterdir()):
            if not dash_dir.is_dir():
                continue
            if dash_dir.name.startswith((".", "_")):
                continue

            dashboard = _load_dashboard(dept_dir.name, dash_dir)
            if dashboard is not None:
                dashboards.append(dashboard)

        if not dashboards:
            continue

        # First-found dashboard's department_title wins — they should
        # all agree, but if they don't, this is a deterministic rule.
        department_title = dashboards[0].department_title

        # Stable display order within a department.
        dashboards.sort(key=lambda d: d.dashboard_title.lower())

        departments.append(
            Department(
                slug=dept_dir.name,
                title=department_title,
                dashboards=tuple(dashboards),
            )
        )

    departments.sort(key=lambda d: d.title.lower())
    return tuple(departments)


def find_dashboard(key: str) -> Dashboard | None:
    """Look up a dashboard by its `key` ('<dept>/<dash>')."""
    for department in scan_dashboards():
        for dashboard in department.dashboards:
            if dashboard.key == key:
                return dashboard
    return None
