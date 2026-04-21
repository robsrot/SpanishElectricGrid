import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_emerging, load_provinces_geojson_str
from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="Strategic Markets | Spain EV 2027",
    page_icon="📈",
    layout="wide",
)

render_sidebar()

st.markdown("## 📈 Strategic Market Analysis — Objective 3")
st.caption("Province-level EV growth analysis · Opportunity scoring · Iberdrola deployment strategy")

df_em = load_emerging()
geojson_str = load_provinces_geojson_str()

QUADRANT_COLORS = {
    "Leader":   "#3B82F6",
    "Mature":   "#10B981",
    "Emerging": "#F59E0B",
    "Lagging":  "#64748B",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**Map Colour Variable**")
    color_var = st.radio(
        "",
        ["opportunity_score", "cagr_pct", "ev_fleet_2027"],
        format_func=lambda x: {
            "opportunity_score": "Opportunity Score (0–100)",
            "cagr_pct": "CAGR 2021–2023 (%)",
            "ev_fleet_2027": "EV Fleet 2027",
        }[x],
    )
    st.markdown("---")
    st.markdown("**Quadrant filter**")
    sel_quad = st.multiselect(
        "Show quadrants",
        ["Leader", "Mature", "Emerging", "Lagging"],
        default=["Leader", "Mature", "Emerging", "Lagging"],
    )

df_filtered = df_em[df_em["quadrant"].isin(sel_quad)].copy()

color_labels = {
    "opportunity_score": "Opp. Score",
    "cagr_pct": "CAGR (%)",
    "ev_fleet_2027": "Fleet 2027",
}

# ── Province Opportunity Map (full width) ─────────────────────────────────────
st.markdown('<p class="section-header">Province Opportunity Map</p>', unsafe_allow_html=True)

fig_choro = px.choropleth_mapbox(
    df_filtered,
    geojson=json.loads(geojson_str),
    locations="province_code",
    featureidkey="properties.cod_prov",
    color=color_var,
    color_continuous_scale="YlOrRd",
    mapbox_style="carto-darkmatter",
    zoom=4.8,
    center={"lat": 40.2, "lon": -3.5},
    opacity=0.75,
    hover_name="province_name",
    hover_data={
        "province_code": False,
        "auto_community": True,
        "quadrant": True,
        "cagr_pct": ":.1f",
        "ev_fleet_2027": ":,",
        "opportunity_score": ":.1f",
    },
    labels={
        "cagr_pct": "CAGR (%)",
        "ev_fleet_2027": "Fleet 2027",
        "opportunity_score": "Opp. Score",
        "auto_community": "Region",
        "quadrant": "Quadrant",
    },
)
fig_choro.update_layout(
    paper_bgcolor="#0F172A",
    margin=dict(t=0, b=0, l=0, r=0),
    height=500,
    coloraxis_colorbar=dict(
        title=dict(text=color_labels[color_var], font=dict(color="#94A3B8")),
        tickfont=dict(color="#94A3B8"),
    ),
)
st.plotly_chart(fig_choro, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Growth vs Fleet Quadrant Scatter (full width) ────────────────────────────
st.markdown('<p class="section-header">Growth vs Fleet Quadrant View</p>', unsafe_allow_html=True)

national_cagr = df_em["cagr_pct"].mean()
median_fleet = df_em["ev_fleet_2027"].median()

top12 = df_filtered.nlargest(12, "opportunity_score")["province_name"].tolist()
df_filtered["label"] = df_filtered.apply(
    lambda r: r["province_name"] if r["province_name"] in top12 else "", axis=1
)

fig_scatter = px.scatter(
    df_filtered,
    x="cagr_pct",
    y="ev_fleet_2027",
    size="opportunity_score",
    color="quadrant",
    color_discrete_map=QUADRANT_COLORS,
    text="label",
    hover_name="province_name",
    hover_data={
        "cagr_pct": ":.1f",
        "ev_fleet_2027": ":,",
        "opportunity_score": ":.1f",
        "quadrant": True,
        "label": False,
    },
    labels={
        "cagr_pct": "CAGR 2021–23 (%)",
        "ev_fleet_2027": "EV Fleet 2027",
        "opportunity_score": "Opp. Score",
    },
    template="plotly_dark",
    size_max=50,
)
fig_scatter.update_traces(textposition="top center", textfont=dict(size=10, color="#CBD5E1"))
fig_scatter.add_vline(x=national_cagr, line_dash="dash", line_color="#94A3B8", opacity=0.6,
                      annotation_text=f"Avg CAGR {national_cagr:.1f}%", annotation_font_color="#94A3B8")
fig_scatter.add_hline(y=median_fleet, line_dash="dash", line_color="#94A3B8", opacity=0.6,
                      annotation_text="Median fleet", annotation_font_color="#94A3B8")

fig_scatter.update_layout(
    paper_bgcolor="#0F172A", plot_bgcolor="#0F172A",
    height=480, margin=dict(t=20, b=20, l=0, r=0),
    yaxis=dict(gridcolor="#1E293B", type="log", title="EV Fleet 2027 (log scale)"),
    xaxis=dict(gridcolor="#1E293B"),
    legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center"),
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ── Top 10 Emerging bar chart ─────────────────────────────────────────────────
col_bar, col_strategy = st.columns([1, 1.1])

with col_bar:
    st.markdown('<p class="section-header">Top 10 Emerging Provinces — Opportunity Ranking</p>', unsafe_allow_html=True)
    top10 = (
        df_em[df_em["quadrant"] == "Emerging"]
        .nlargest(10, "opportunity_score")
        .sort_values("opportunity_score")
    )
    fig_bar = px.bar(
        top10,
        x="opportunity_score",
        y="province_name",
        orientation="h",
        color="opportunity_score",
        color_continuous_scale=["#F59E0B", "#EF4444"],
        text=top10["cagr_pct"].map(lambda v: f"CAGR {v:.1f}%"),
        template="plotly_dark",
        labels={"opportunity_score": "Opportunity Score", "province_name": "Province"},
    )
    fig_bar.update_traces(textposition="inside", textfont=dict(color="#1E293B", size=10))
    fig_bar.update_layout(
        paper_bgcolor="#0F172A", plot_bgcolor="#0F172A",
        height=340, margin=dict(t=10, b=10, l=0, r=0),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#1E293B", range=[0, 110]),
        yaxis=dict(gridcolor="#1E293B"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_strategy:
    st.markdown('<p class="section-header">Deployment Strategy</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Balanced Strategy", "Emerging-First"])

    with tab1:
        st.markdown(
            '<div class="phase-card phase-1">'
            '<p class="phase-title">Phase 1 — Defend Leaders (2025–2026)</p>'
            '<p class="phase-body">Prioritise Madrid (635K EVs), Barcelona (184K), Valencia (56K) and País Vasco. '
            'These provinces generate 60%+ of national charging demand. '
            'Lock in Iberdrola market share before Repsol and Endesa X scale up.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="phase-card phase-2">'
            '<p class="phase-title">Phase 2 — Capture Emerging (2026–2027)</p>'
            '<p class="phase-body">Deploy on A-66 (Ruta de la Plata) and A-4 corridors crossing '
            'Badajoz (CAGR 49.8%), Cáceres, Zamora, Salamanca. '
            'Iberdrola controls i-DE grid in Extremadura and Castilla y León — '
            'vertical integration advantage is unique to Iberdrola here.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="phase-card phase-3">'
            '<p class="phase-title">Phase 3 — Optimise Mature (2027)</p>'
            '<p class="phase-body">Fill gaps in Zaragoza, Murcia, Alicante, Tarragona, Girona. '
            'These provinces show stable growth (CAGR 14–18%) but require fewer new stations '
            'as existing HPC coverage is denser. Focus on utilisation rate maximisation.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    with tab2:
        emerging_top = df_em[df_em["quadrant"] == "Emerging"].nlargest(10, "opportunity_score")
        st.markdown(
            "**First-mover strategy:** Deploy immediately in the top 10 Emerging provinces "
            "before competitors (Repsol, Endesa X, Tesla) establish dominance in high-CAGR markets."
        )
        st.dataframe(
            emerging_top[["province_name", "auto_community", "cagr_pct", "ev_fleet_2027", "opportunity_score"]]
            .rename(columns={
                "province_name": "Province",
                "auto_community": "Region",
                "cagr_pct": "CAGR (%)",
                "ev_fleet_2027": "Fleet 2027",
                "opportunity_score": "Score",
            }),
            hide_index=True,
            use_container_width=True,
        )
        st.info(
            "A-66 (Ruta de la Plata) passes through 6 of the top 10 emerging provinces. "
            "Iberdrola's i-DE manages the grid along this corridor — a unique competitive advantage.",
            icon="⚡",
        )

st.markdown("---")
st.markdown('<p class="section-header">All Provinces — Full Opportunity Ranking</p>', unsafe_allow_html=True)

def _color_quad(val: str) -> str:
    return {
        "Leader":   "background-color:#1E3A5F; color:#93C5FD",
        "Mature":   "background-color:#064E3B; color:#6EE7B7",
        "Emerging": "background-color:#78350F; color:#FCD34D",
        "Lagging":  "background-color:#1E293B; color:#94A3B8",
    }.get(val, "")

st.dataframe(
    df_em.sort_values("opportunity_score", ascending=False)[
        ["province_name", "auto_community", "quadrant", "cagr_pct", "ev_fleet_2027", "opportunity_score"]
    ].rename(columns={
        "province_name": "Province", "auto_community": "Region",
        "quadrant": "Quadrant", "cagr_pct": "CAGR (%)",
        "ev_fleet_2027": "Fleet 2027", "opportunity_score": "Opp. Score",
    })
    .style.map(_color_quad, subset=["Quadrant"]),
    use_container_width=True,
    hide_index=True,
    height=400,
)
