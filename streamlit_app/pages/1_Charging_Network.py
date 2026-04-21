import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from utils.data_loader import (
    CORRIDORS,
    CORRIDOR_COLORS,
    GRID_COLORS,
    load_file2,
    load_file3,
)
from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="Charging Network | Spain EV 2027",
    page_icon="🗺️",
    layout="wide",
)

render_sidebar()

st.markdown("## 🗺️ Charging Network Optimization — Objective 1")
st.caption("Proposed HPC charging stations on TEN-T interurban corridors · AFIR 2023/1804 compliant")

# ── Sidebar filters ───────────────────────────────────────────────────────────
df2 = load_file2()
df3 = load_file3()

with st.sidebar:
    st.markdown("**Filters**")
    all_corridors = sorted(CORRIDORS.keys())
    sel_corridors = st.multiselect("Corridor", all_corridors, default=all_corridors)
    sel_status = st.multiselect(
        "Grid Status",
        ["Sufficient", "Moderate", "Congested"],
        default=["Sufficient", "Moderate", "Congested"],
    )
    show_friction = st.checkbox("Show friction points", value=True)
    show_corridors = st.checkbox("Show TEN-T corridor lines", value=True)
    st.markdown("---")
    st.markdown(
        '<span class="badge-green">● Sufficient</span><br>'
        '<span class="badge-yellow">● Moderate</span><br>'
        '<span class="badge-red">● Congested</span>',
        unsafe_allow_html=True,
    )
    st.caption("Green ≥5 MW · Yellow 1–5 MW · Red <1 MW")

# ── Filter data ───────────────────────────────────────────────────────────────
mask = df2["route_segment"].isin(sel_corridors) & df2["grid_status"].isin(sel_status)
df2_f = df2[mask].copy()

df2_f["color"] = df2_f["grid_status"].map(GRID_COLORS)
df2_f["radius"] = (df2_f["n_chargers_proposed"] * 4000).clip(8000, 28000)

df3_f = df3[df3["route_segment"].isin(sel_corridors)].copy()
df3_f["color"] = df3_f["grid_status"].map(GRID_COLORS)
df3_f["radius"] = 6000

# ── pydeck layers ─────────────────────────────────────────────────────────────
layers = []

if show_corridors:
    for name, path in CORRIDORS.items():
        if name in sel_corridors or not sel_corridors:
            color = CORRIDOR_COLORS.get(name, [180, 180, 180])
            layers.append(
                pdk.Layer(
                    "PathLayer",
                    data=[{"path": path, "name": name}],
                    get_path="path",
                    get_color=color,
                    get_width=4,
                    width_min_pixels=2,
                    pickable=False,
                )
            )

if not df2_f.empty:
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df2_f,
            get_position=["longitude", "latitude"],
            get_fill_color="color",
            get_radius="radius",
            radius_min_pixels=6,
            radius_max_pixels=20,
            pickable=True,
            stroked=True,
            get_line_color=[255, 255, 255, 80],
            line_width_min_pixels=1,
        )
    )

if show_friction and not df3_f.empty:
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df3_f,
            get_position=["longitude", "latitude"],
            get_fill_color=[239, 68, 68, 180],
            get_radius=5000,
            radius_min_pixels=8,
            radius_max_pixels=14,
            pickable=True,
            stroked=True,
            get_line_color=[255, 255, 255, 200],
            line_width_min_pixels=2,
        )
    )

# Arc layer: proposed station → nearest friction point (if both datasets populated)
if not df2_f.empty and not df3_f.empty:
    arcs = []
    for _, row in df2_f[df2_f["grid_status"] != "Sufficient"].iterrows():
        if df3_f.empty:
            break
        dists = np.sqrt(
            (df3_f["latitude"] - row["latitude"]) ** 2
            + (df3_f["longitude"] - row["longitude"]) ** 2
        )
        nearest = df3_f.iloc[dists.idxmin()]
        arcs.append({
            "source": [row["longitude"], row["latitude"]],
            "target": [nearest["longitude"], nearest["latitude"]],
        })
    if arcs:
        layers.append(
            pdk.Layer(
                "ArcLayer",
                data=arcs,
                get_source_position="source",
                get_target_position="target",
                get_source_color=[239, 68, 68, 120],
                get_target_color=[234, 179, 8, 120],
                get_width=2,
                width_min_pixels=1,
                pickable=False,
            )
        )

view = pdk.ViewState(latitude=40.2, longitude=-3.5, zoom=5.2, pitch=0)

tooltip = {
    "html": (
        "<b>{location_id}</b><br>"
        "Route: <b>{route_segment}</b><br>"
        "Chargers: <b>{n_chargers_proposed}</b><br>"
        "Demand: <b>{estimated_demand_kw} kW</b><br>"
        "Grid: <b>{grid_status}</b>"
    ),
    "style": {
        "backgroundColor": "#1E293B",
        "color": "#F1F5F9",
        "fontSize": "13px",
        "padding": "10px",
        "borderRadius": "8px",
    },
}

st.pydeck_chart(
    pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        tooltip=tooltip,
    ),
    use_container_width=True,
    height=520,
)

# ── AFIR compliance notice ───────────────────────────────────────────────────
st.info(
    "**AFIR 2023/1804 Compliance:** Stations are sampled at ≤60 km intervals along TEN-T Core corridors "
    "and ≤100 km on Comprehensive corridors. Grid status is derived from the nearest distributor "
    "substation (i-DE, Endesa, or Viesgo) using KD-tree spatial matching in EPSG:25830.",
    icon="📋",
)

# ── Summary metrics ───────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Stations shown", len(df2_f))
col2.metric("Total chargers", int(df2_f["n_chargers_proposed"].sum()))
col3.metric("Total demand (MW)", f"{df2_f['estimated_demand_kw'].sum() / 1000:.1f}")
col4.metric("Friction points", len(df3_f) if show_friction else "hidden")

st.markdown("---")
st.markdown('<p class="section-header">Proposed Station Details</p>', unsafe_allow_html=True)

# Colour the grid_status column
def _color_status(val: str) -> str:
    return {
        "Sufficient": "background-color:#166534; color:#86EFAC",
        "Moderate":   "background-color:#713F12; color:#FDE68A",
        "Congested":  "background-color:#7F1D1D; color:#FCA5A5",
    }.get(val, "")

display_cols = ["location_id", "route_segment", "n_chargers_proposed", "estimated_demand_kw", "grid_status"]
st.dataframe(
    df2_f[display_cols].style.map(_color_status, subset=["grid_status"]),
    use_container_width=True,
    hide_index=True,
)
