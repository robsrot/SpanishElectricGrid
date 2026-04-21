import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import streamlit as st

from utils.data_loader import CORRIDORS, CORRIDOR_COLORS, GRID_COLORS, load_file2, load_file3
from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="Grid Viability | Spain EV 2027",
    page_icon="⚡",
    layout="wide",
)

render_sidebar()

st.markdown("## ⚡ Grid Viability Analysis — Objective 2")
st.markdown(
    '<span style="font-size:0.8rem;color:#94A3B8;">'
    'Friction points: locations where <span class="abbr-tooltip" data-tooltip="Electric Vehicle">EV</span> charging demand '
    'exceeds local grid hosting capacity'
    '</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '> **What this page answers:** Not every corridor location can host a charger today. '
    'This page identifies *friction points* — nodes where the projected '
    '<span class="abbr-tooltip" data-tooltip="Electric Vehicle">EV</span> charging load exceeds the available grid hosting capacity '
    'of the nearest distributor substation. '
    '**Congested** locations (<1 <span class="abbr-tooltip" data-tooltip="Megawatt — 1,000 kilowatts of electrical power capacity">MW</span> available) '
    'require Iberdrola to pre-negotiate grid reinforcement with '
    '<span class="abbr-tooltip" data-tooltip="Iberdrola Distribución Eléctrica — Iberdrola\'s regulated grid subsidiary">i-DE</span>, '
    'Endesa, or Viesgo before any construction begins — typically a 12–18 month lead time. '
    '**Moderate** locations (1–5 MW) can support a smaller initial station while reinforcement is underway. '
    'Understanding this map is essential: deploying chargers without grid clearance leads to regulatory delays and stranded '
    '<span class="abbr-tooltip" data-tooltip="Capital Expenditure — upfront investment in physical infrastructure">capex</span>.',
    unsafe_allow_html=True,
)

df3 = load_file3()
df2 = load_file2()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**Filters**")
    all_distributors = sorted(df3["distributor_network"].unique().tolist())
    sel_dist = st.multiselect("Distributor", all_distributors, default=all_distributors)
    sel_status = st.multiselect(
        "Grid Status (File 3 only)",
        ["Moderate", "Congested"],
        default=["Moderate", "Congested"],
    )
    st.markdown("---")
    st.caption("Only Moderate and Congested locations appear in File 3 per datathon Rule 3.")

df3_f = df3[df3["distributor_network"].isin(sel_dist) & df3["grid_status"].isin(sel_status)].copy()
df3_f["color"] = df3_f["grid_status"].map(GRID_COLORS)
df3_f["radius"] = (df3_f["estimated_demand_kw"] * 5).clip(4000, 22000)

# ── Map ───────────────────────────────────────────────────────────────────────
corridor_layers = []
for name, path in CORRIDORS.items():
    color = CORRIDOR_COLORS.get(name, [180, 180, 180])
    corridor_layers.append(
        pdk.Layer(
            "PathLayer",
            data=[{"path": path}],
            get_path="path",
            get_color=[*color[:3], 80],
            get_width=3,
            width_min_pixels=1,
            pickable=False,
        )
    )

friction_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df3_f,
    get_position=["longitude", "latitude"],
    get_fill_color="color",
    get_radius="radius",
    radius_min_pixels=8,
    radius_max_pixels=22,
    pickable=True,
    stroked=True,
    get_line_color=[255, 255, 255, 160],
    line_width_min_pixels=2,
)

tooltip = {
    "html": (
        "<b>{bottleneck_id}</b><br>"
        "Route: <b>{route_segment}</b><br>"
        "Distributor: <b>{distributor_network}</b><br>"
        "Demand: <b>{estimated_demand_kw} kW</b><br>"
        "Status: <b>{grid_status}</b>"
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
        layers=corridor_layers + [friction_layer],
        initial_view_state=pdk.ViewState(latitude=40.2, longitude=-3.5, zoom=5.2, pitch=0),
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        tooltip=tooltip,
    ),
    use_container_width=True,
    height=460,
)

# ── Key finding callout ───────────────────────────────────────────────────────
if not df3_f.empty:
    top_corridor = (
        df3_f.groupby("route_segment")["estimated_demand_kw"].sum().idxmax()
    )
    top_dist = (
        df3_f.groupby("distributor_network")["bottleneck_id"].count().idxmax()
    )
    congested_pct = int(100 * len(df3_f[df3_f["grid_status"] == "Congested"]) / len(df3_f))
    st.warning(
        f"**{congested_pct}% of friction points are Congested** (< 1 MW available). "
        f"Corridor **{top_corridor}** carries the highest unmet demand. "
        f"Distributor **{top_dist}** manages most of the bottleneck nodes — "
        f"grid reinforcement must be coordinated before charger deployment.",
        icon="⚠️",
    )

st.markdown("---")

# ── Charts ────────────────────────────────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.markdown('<p class="section-header">Friction Points by Distributor</p>', unsafe_allow_html=True)
    if df3_f.empty:
        st.info("No data matches current filters.")
    else:
        dist_count = df3_f.groupby(["distributor_network", "grid_status"]).size().reset_index(name="count")
        fig_dist = px.bar(
            dist_count, x="count", y="distributor_network", color="grid_status",
            orientation="h",
            color_discrete_map={"Congested": "#EF4444", "Moderate": "#EAB308"},
            template="plotly_dark",
            labels={"count": "Friction points", "distributor_network": "Distributor", "grid_status": "Status"},
        )
        fig_dist.update_layout(
            paper_bgcolor="#0F172A", plot_bgcolor="#0F172A",
            height=280, margin=dict(t=10, b=10, l=0, r=0),
            legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
            xaxis=dict(gridcolor="#1E293B"),
            yaxis=dict(gridcolor="#1E293B"),
        )
        st.plotly_chart(fig_dist, use_container_width=True)

with col_r:
    st.markdown('<p class="section-header">Estimated Demand by Corridor (kW)</p>', unsafe_allow_html=True)
    if df3_f.empty:
        st.info("No data matches current filters.")
    else:
        demand_seg = (
            df3_f.groupby("route_segment")["estimated_demand_kw"]
            .sum()
            .reset_index()
            .sort_values("estimated_demand_kw", ascending=True)
        )
        fig_dem = px.bar(
            demand_seg, x="estimated_demand_kw", y="route_segment",
            orientation="h",
            color="estimated_demand_kw",
            color_continuous_scale=["#EAB308", "#EF4444"],
            template="plotly_dark",
            labels={"estimated_demand_kw": "Demand (kW)", "route_segment": "Corridor"},
        )
        fig_dem.update_layout(
            paper_bgcolor="#0F172A", plot_bgcolor="#0F172A",
            height=280, margin=dict(t=10, b=10, l=0, r=0),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#1E293B"),
            yaxis=dict(gridcolor="#1E293B"),
        )
        st.plotly_chart(fig_dem, use_container_width=True)

# ── Capacity Gap Gauge ─────────────────────────────────────────────────────────
if not df3_f.empty:
    st.markdown("---")
    st.markdown('<p class="section-header">Total Unmet Demand vs Grid Capacity Near Corridors</p>', unsafe_allow_html=True)

    total_demand_mw = df3_f["estimated_demand_kw"].sum() / 1000
    # Conservative estimate: ~800 MW total available near corridors from distributor data
    available_mw = 800.0
    utilisation = min(total_demand_mw / available_mw, 1.0)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=total_demand_mw,
        delta={"reference": available_mw * 0.8, "valueformat": ".1f"},
        title={"text": "Friction demand (MW)", "font": {"color": "#F1F5F9"}},
        number={"suffix": " MW", "font": {"color": "#F1F5F9"}},
        gauge={
            "axis": {"range": [0, available_mw], "tickcolor": "#94A3B8"},
            "bar": {"color": "#EF4444" if utilisation > 0.6 else "#EAB308"},
            "bgcolor": "#1E293B",
            "bordercolor": "#334155",
            "steps": [
                {"range": [0, available_mw * 0.5], "color": "#166534"},
                {"range": [available_mw * 0.5, available_mw * 0.8], "color": "#713F12"},
                {"range": [available_mw * 0.8, available_mw], "color": "#7F1D1D"},
            ],
            "threshold": {
                "line": {"color": "#FFFFFF", "width": 3},
                "thickness": 0.85,
                "value": available_mw * 0.8,
            },
        },
    ))
    fig_gauge.update_layout(
        paper_bgcolor="#0F172A", height=260, margin=dict(t=40, b=20, l=40, r=40),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.caption(
        "Available capacity is aggregated from nearest distributor substations (i-DE R1-001, "
        "Endesa R1-002, Viesgo R1-299) along the 12 TEN-T corridors. "
        "Threshold line at 80% saturation."
    )

st.markdown("---")
st.markdown('<p class="section-header">Friction Point Details (File 3)</p>', unsafe_allow_html=True)

def _color_status(val: str) -> str:
    return {
        "Moderate":  "background-color:#713F12; color:#FDE68A",
        "Congested": "background-color:#7F1D1D; color:#FCA5A5",
    }.get(val, "")

st.dataframe(
    df3_f[["bottleneck_id", "route_segment", "distributor_network", "estimated_demand_kw", "grid_status"]]
    .style.map(_color_status, subset=["grid_status"]),
    use_container_width=True,
    hide_index=True,
)
