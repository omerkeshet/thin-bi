"""
Compute the Shorts funnel from the cached DataFrame.

Pure data shaping — returns a dict of step totals + per-site breakdowns.
No Streamlit, no HTML.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


# Hebrew label for the auto-played source value, matching the Domo dashboard.
AUTO_PLAY_SOURCE = "ניגון אוטומטי"
LOOP_PLAY_SOURCE = "loop"


@dataclass(frozen=True)
class FunnelStep:
    key: str
    label: str
    total: float
    by_site: dict[str, float]  # site_name -> measure value
    width_pct: int  # visual width tier; matches the original CSS clip-paths


def compute_shorts_funnel(df: pd.DataFrame) -> dict[str, Any]:
    """
    Compute the four funnel steps from a DataFrame containing at minimum:
      - plays (numeric)
      - play_source (string)
      - natives (numeric)
      - bumpers (numeric)
      - site (string)
    """
    required = {"plays", "play_source", "natives", "bumpers", "site"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Funnel requires columns {sorted(required)}, missing: {sorted(missing)}. "
            f"Available: {list(df.columns)}"
        )

    # Coerce to numeric defensively.
    plays = pd.to_numeric(df["plays"], errors="coerce").fillna(0)
    natives = pd.to_numeric(df["natives"], errors="coerce").fillna(0)
    bumpers = pd.to_numeric(df["bumpers"], errors="coerce").fillna(0)
    play_source = df["play_source"].fillna("")
    site = df["site"].fillna("unknown")

    # Per-row contributions to each step.
    step1_contrib = plays
    step2_contrib = plays.where(play_source != AUTO_PLAY_SOURCE, 0)
    step3_contrib = plays.where(
        (play_source != AUTO_PLAY_SOURCE) & (play_source != LOOP_PLAY_SOURCE),
        0,
    )
    step4_contrib = natives + bumpers

    work = pd.DataFrame({
        "site": site,
        "all_plays": step1_contrib,
        "plays_without_auto": step2_contrib,
        "plays_without_auto_and_loop": step3_contrib,
        "total_impressions_sum": step4_contrib,
    })

    by_site_df = work.groupby("site", dropna=False).sum()

    def _by_site(col: str) -> dict[str, float]:
        # Keep zero entries out — empty segments add no info and clutter the UI.
        return {
            str(s): float(v)
            for s, v in by_site_df[col].items()
            if float(v) > 0
        }

    steps = [
        FunnelStep(
            key="all_plays",
            label="כל ניגוני השורטס",
            total=float(work["all_plays"].sum()),
            by_site=_by_site("all_plays"),
            width_pct=100,
        ),
        FunnelStep(
            key="plays_without_auto",
            label="ללא ניגונים אוטומטיים",
            total=float(work["plays_without_auto"].sum()),
            by_site=_by_site("plays_without_auto"),
            width_pct=76,
        ),
        FunnelStep(
            key="plays_without_auto_and_loop",
            label="ללא אוטומטיים וללא לופ",
            total=float(work["plays_without_auto_and_loop"].sum()),
            by_site=_by_site("plays_without_auto_and_loop"),
            width_pct=52,
        ),
        FunnelStep(
            key="total_impressions_sum",
            label='סה"כ חשיפות',
            total=float(work["total_impressions_sum"].sum()),
            by_site=_by_site("total_impressions_sum"),
            width_pct=34,
        ),
    ]

    return {"steps": steps}
