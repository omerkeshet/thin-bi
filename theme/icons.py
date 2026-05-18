"""
Inline Lucide icons.

Returns SVG markup as a string. Color comes from CSS (`color: currentColor`),
so wrapping the icon in a styled element controls its color.

Add new icons by copying the inner <path>...</path> from lucide.dev and
keeping the same outer <svg> wrapper. Always strip xmlns, hardcoded stroke
colors, and any id attributes — Streamlit's HTML sanitizer rejects some of
those and React occasionally chokes on duplicate ids.
"""

from __future__ import annotations


_SVG_OPEN = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
    'class="tbi-icon">'
)
_SVG_CLOSE = "</svg>"


# --- Icon paths (Lucide) ---
_PATHS: dict[str, str] = {
    "dashboard": (
        '<rect width="7" height="9" x="3" y="3" rx="1"/>'
        '<rect width="7" height="5" x="14" y="3" rx="1"/>'
        '<rect width="7" height="9" x="14" y="12" rx="1"/>'
        '<rect width="7" height="5" x="3" y="16" rx="1"/>'
    ),
    "bar-chart": (
        '<line x1="12" x2="12" y1="20" y2="10"/>'
        '<line x1="18" x2="18" y1="20" y2="4"/>'
        '<line x1="6" x2="6" y1="20" y2="16"/>'
    ),
    "line-chart": (
        '<path d="M3 3v18h18"/>'
        '<path d="m19 9-5 5-4-4-3 3"/>'
    ),
    "pie-chart": (
        '<path d="M21 12A9 9 0 1 1 12 3"/>'
        '<path d="M21 12A9 9 0 0 0 12 3v9z"/>'
    ),
    "funnel": (
        '<path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/>'
    ),
    "table": (
        '<path d="M12 3v18"/>'
        '<rect width="18" height="18" x="3" y="3" rx="2"/>'
        '<path d="M3 9h18"/><path d="M3 15h18"/>'
    ),
    "database": (
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M3 5V19A9 3 0 0 0 21 19V5"/>'
        '<path d="M3 12A9 3 0 0 0 21 12"/>'
    ),
    "clock": (
        '<circle cx="12" cy="12" r="10"/>'
        '<polyline points="12 6 12 12 16 14"/>'
    ),
    "users": (
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),
    "trending-up": (
        '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
        '<polyline points="16 7 22 7 22 13"/>'
    ),
    "play": (
        '<polygon points="6 3 20 12 6 21 6 3"/>'
    ),
    "video": (
        '<path d="m22 8-6 4 6 4V8Z"/>'
        '<rect width="14" height="12" x="2" y="6" rx="2"/>'
    ),
    "dollar": (
        '<line x1="12" x2="12" y1="2" y2="22"/>'
        '<path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'
    ),
    "briefcase": (
        '<rect width="20" height="14" x="2" y="7" rx="2"/>'
        '<path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'
    ),
    "settings": (
        '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>'
        '<circle cx="12" cy="12" r="3"/>'
    ),
    "search": (
        '<circle cx="11" cy="11" r="8"/>'
        '<line x1="21" x2="16.65" y1="21" y2="16.65"/>'
    ),
    "filter": (
        '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>'
    ),
    "log-out": (
        '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>'
        '<polyline points="16 17 21 12 16 7"/>'
        '<line x1="21" x2="9" y1="12" y2="12"/>'
    ),
    "wrench": (
        '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'
    ),
    "circle": (
        '<circle cx="12" cy="12" r="10"/>'
    ),
}


def icon(name: str, *, size: int = 16) -> str:
    """
    Return inline SVG for the named icon, sized to `size` px (square).
    Falls back to a small filled circle if the name is unknown.
    """
    path = _PATHS.get(name, _PATHS["circle"])
    return (
        f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        f'class="tbi-icon" style="width:{size}px;height:{size}px;">'
        f"{path}"
        f"{_SVG_CLOSE}"
    )


def icon_names() -> list[str]:
    """For debug — list available icons."""
    return sorted(_PATHS.keys())
