"""
Dashboard registry — scans the `dashboards/` directory and produces a
structured catalog of available dashboards, grouped by department.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import streamlit as st


_REPO_ROOT = Path(__file__).resolve().parent.parent
_DASHBOARDS_DIR = _REPO_ROOT / "dashboards"


@dataclass(frozen=True)
class Dashboard:
    key: str
    department_slug: str
    dashboard_slug: str
    department_title: str
    dashboard_title: str
    config_path: Path
    query_path: Path
    icon: str = "dashboard"
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Department:
    slug: str
    title: str
    dashboards: tuple[Dashboard, ...]
    icon: str = "briefcase"


def _slug_to_title(slug: str) -> str:
    return slug.replace("_", " ").replace("-", " ").strip().title()


def _load_dashboard(
    department_slug: str,
    dashboard_dir: Path,
) -> Dashboard | None:
    config_path = dashboard_dir / "config.json"
    query_path = dashboard_dir / "query.sql"

    if not config_path.is_file() or not query_path.is_file():
        return None

    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
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
    icon = config.get("icon") or "dashboard"

    return Dashboard(
        key=f"{department_slug}/{dashboard_slug}",
        department_slug=department_slug,
        dashboard_slug=dashboard_slug,
        department_title=department_title,
        dashboard_title=dashboard_title,
        config_path=config_path,
        query_path=query_path,
        icon=icon,
        config=config,
    )


@st.cache_resource(show_spinner=False)
def scan_dashboards() -> tuple[Department, ...]:
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

        department_title = dashboards[0].department_title
        # Department icon: take the first dashboard's `department_icon` from
        # config if present, otherwise a sensible default.
        dept_icon: str = "briefcase"
        for d in dashboards:
            di = d.config.get("department_icon")
            if di:
                dept_icon = di
                break

        dashboards.sort(key=lambda d: d.dashboard_title.lower())

        departments.append(
            Department(
                slug=dept_dir.name,
                title=department_title,
                dashboards=tuple(dashboards),
                icon=dept_icon,
            )
        )

    departments.sort(key=lambda d: d.title.lower())
    return tuple(departments)


def find_dashboard(key: str) -> Dashboard | None:
    for department in scan_dashboards():
        for dashboard in department.dashboards:
            if dashboard.key == key:
                return dashboard
    return None
