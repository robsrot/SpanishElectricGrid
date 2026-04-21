import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import streamlit.components.v1 as components

from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="Interactive Maps | Spain EV 2027",
    page_icon="🌍",
    layout="wide",
)

render_sidebar()

STATIC_DIR = Path(__file__).parent.parent / "static" / "maps"

MAPS = {
    "map1": {
        "label": "Map 1 — Proposed Stations",
        "file": "map1.html",
        "description": (
            "Proposed interurban HPC stations (File 2), "
            "scored and filtered at 40 km AFIR spacing."
        ),
        "icon": "🗺️",
        "default": False,
    },
    "map2": {
        "label": "Map 2 — Grid Friction Points",
        "file": "map2.html",
        "description": (
            "Friction points (File 3) — locations where projected "
            "EV demand exceeds grid hosting capacity."
        ),
        "icon": "⚡",
        "default": False,
    },
    "map3": {
        "label": "Map 3 — Strategic Markets",
        "file": "map3.html",
        "description": (
            "Emerging province opportunity map — "
            "growth rate vs. fleet size quadrant view."
        ),
        "icon": "📈",
        "default": False,
    },
    "map4": {
        "label": "Map 4 — Points of Interest",
        "file": "map4_pois.html",
        "description": (
            "Service areas, rest stops, and candidate POI sites "
            "along interurban corridors."
        ),
        "icon": "📍",
        "default": False,
    },
    "bi_map": {
        "label": "BI Map — Full Network Overview",
        "file": "bi_map_optimized.html",
        "description": (
            "All layers: proposed stations, friction points, "
            "top 10 priority Congested nodes, TEN-T corridors."
        ),
        "icon": "🔍",
        "default": True,
    },
}


def _read_map(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🌍 Interactive Maps — Full Layer Explorer")
st.markdown(
    '<span style="font-size:0.8rem;color:#94A3B8;">'
    "Toggle maps on and off using the controls below."
    "</span>",
    unsafe_allow_html=True,
)

st.info(
    "**For the best experience, view one map at a time.** "
    "Multiple maps loaded simultaneously may slow down your browser.",
    icon="💡",
)
st.warning(
    "**BI Map — please be patient.** "
    "The more additional layers you enable on top, "
    "the longer it may take. Once loaded, panning and zooming "
    "will be fluid.",
    icon="⚡",
)
st.markdown("---")

# ── Layer toggles ─────────────────────────────────────────────────────────────
st.markdown(
    '<p style="color:#00B140;font-size:1.1rem;font-weight:600;'
    'margin-bottom:4px;">Layer Controls</p>',
    unsafe_allow_html=True,
)

cols = st.columns(len(MAPS))
toggles = {}
for col, (key, meta) in zip(cols, MAPS.items()):
    with col:
        available = (STATIC_DIR / meta["file"]).exists()
        short_label = meta["label"].split("—")[0].strip()
        size_mb = (
            round((STATIC_DIR / meta["file"]).stat().st_size / 1e6, 1)
            if available
            else 0
        )
        help_text = (
            f"{meta['description']} ({size_mb} MB)"
            if available
            else "File not found — re-run the notebook."
        )
        toggles[key] = st.toggle(
            f"{meta['icon']} {short_label}",
            value=meta["default"] and available,
            disabled=not available,
            help=help_text,
        )

st.markdown("---")

# ── Render active maps ────────────────────────────────────────────────────────
active = [key for key, on in toggles.items() if on]

if not active:
    st.info("No maps selected — toggle at least one layer above.")
else:
    for key in active:
        meta = MAPS[key]
        src = STATIC_DIR / meta["file"]

        st.markdown(
            f'<p style="color:#00B140;font-size:1.05rem;font-weight:600;'
            f'margin-bottom:2px;">{meta["icon"]} {meta["label"]}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<span style="font-size:0.8rem;color:#94A3B8;">'
            f'{meta["description"]}</span>',
            unsafe_allow_html=True,
        )

        size_mb = round(src.stat().st_size / 1e6, 1)
        if size_mb >= 5:
            st.warning(
                "This map contains many layers — the initial load "
                "may take a moment. Please be patient, it will be "
                "worth it.",
                icon="⏳",
            )

        components.html(_read_map(src), height=560, scrolling=False)
        st.markdown("<br>", unsafe_allow_html=True)
