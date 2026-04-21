import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import SAMPLE_NOTICE, load_emerging, load_file1, load_forecast
from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="Spain EV Network 2027 | Iberdrola",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_sidebar()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("## ⚡ Spain EV Charging Network — 2027 Strategic Plan")
st.markdown(
    "**Iberdrola** · Intelligent Electric Mobility · IE Datathon March 2026  \n"
    "Designing tomorrow's interurban charging infrastructure across Spain's TEN-T corridors."
)
st.markdown(
    '> Spain\'s <span class="abbr-tooltip" data-tooltip="Trans-European Transport Network — the EU\'s strategic road, rail and waterway corridors">TEN-T</span> '
    'interurban corridors carry over 80% of long-distance road traffic, '
    'yet only **424 ultra-fast <span class="abbr-tooltip" data-tooltip="High Power Charging — DC fast charging ≥150 kW, enabling a meaningful charge in 20–30 min">HPC</span> chargers (>150 kW)** '
    'exist today against a projected fleet of **1.4 million <span class="abbr-tooltip" data-tooltip="Electric Vehicle">EV</span>s by 2027**. '
    'This dashboard defines *where* Iberdrola should build, *why* certain locations are critical, '
    'and *which markets* to enter first — before Repsol and Endesa X do.',
    unsafe_allow_html=True,
)
st.info(SAMPLE_NOTICE, icon="ℹ️")
st.markdown("---")

# ── KPI Cards ────────────────────────────────────────────────────────────────
kpi = load_file1().iloc[0]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">Proposed HPC Stations</p>'
        f'<p class="kpi-value">{int(kpi["total_proposed_stations"]):,}</p>'
        f'<p class="kpi-delta">↑ New on TEN-T corridors</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">EV Fleet Projected 2027</p>'
        f'<p class="kpi-value">{int(kpi["total_ev_projected_2027"]):,}</p>'
        f'<p class="kpi-delta">SARIMA(1,1,1)×(1,0,1,12)</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">Grid Friction Points</p>'
        f'<p class="kpi-value">{int(kpi["total_friction_points"]):,}</p>'
        f'<p class="kpi-delta">⚠ Require grid reinforcement</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        f'<div class="kpi-card">'
        f'<p class="kpi-label">Existing HPC Baseline</p>'
        f'<p class="kpi-value">{int(kpi["total_existing_stations_baseline"]):,}</p>'
        f'<p class="kpi-delta">Interurban corridors (DGT)</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── EV Fleet Forecast Chart ───────────────────────────────────────────────────
st.markdown('<p class="section-header">EV Fleet Forecast — Spain 2021–2027</p>', unsafe_allow_html=True)
st.markdown(
    '<span style="font-size:0.8rem;color:#94A3B8;">'
    'Quarterly data · '
    '<span class="abbr-tooltip" data-tooltip="Battery Electric Vehicle — runs entirely on electricity">BEV</span> + '
    '<span class="abbr-tooltip" data-tooltip="Plug-in Hybrid Electric Vehicle — electric + combustion engine, can charge from a socket">PHEV</span> + '
    '<span class="abbr-tooltip" data-tooltip="Range Extended Electric Vehicle — electric drive with a small combustion range extender">REEV</span> + '
    '<span class="abbr-tooltip" data-tooltip="Fuel Cell Electric Vehicle — generates electricity from hydrogen">FCEV</span> · '
    'Source: datos.gob.es fork (mandatory) · '
    'Model: <span class="abbr-tooltip" data-tooltip="Seasonal AutoRegressive Integrated Moving Average — statistical time series forecasting model">SARIMA</span>(1,1,1)×(1,0,1,12)'
    '</span>',
    unsafe_allow_html=True,
)

df_fc = load_forecast()
actual = df_fc[df_fc["type"] == "actual"]
forecast = df_fc[df_fc["type"] == "forecast"]

# Connect the two lines at the boundary
boundary_row = actual.iloc[[-1]]
forecast_line = pd.concat([boundary_row, forecast], ignore_index=True)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=actual["date"], y=actual["ev_registrations"],
    name="Actual registrations",
    line=dict(color="#00B140", width=2.5),
    mode="lines+markers",
    marker=dict(size=5),
))

fig.add_trace(go.Scatter(
    x=forecast_line["date"], y=forecast_line["ev_registrations"],
    name="SARIMA forecast",
    line=dict(color="#00A9CE", width=2.5, dash="dash"),
    mode="lines+markers",
    marker=dict(size=5, symbol="diamond"),
))

# 2027 annotation
last = forecast.iloc[-1]
fig.add_annotation(
    x=last["date"], y=last["ev_registrations"],
    text=f"<b>{last['ev_registrations']:,} EVs/qtr</b>",
    showarrow=True, arrowhead=2, arrowcolor="#00A9CE",
    font=dict(color="#00A9CE", size=12),
    bgcolor="#1E293B", bordercolor="#00A9CE", borderwidth=1,
    ax=40, ay=-40,
)

fig.add_vrect(
    x0="2025-01-01", x1=forecast["date"].max().strftime("%Y-%m-%d"),
    fillcolor="#1E3A5F", opacity=0.3,
    annotation_text="Forecast horizon", annotation_position="top left",
    annotation_font=dict(color="#94A3B8", size=11),
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0F172A",
    plot_bgcolor="#0F172A",
    height=360,
    margin=dict(t=20, b=20, l=0, r=0),
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    xaxis=dict(gridcolor="#1E293B", title=""),
    yaxis=dict(gridcolor="#1E293B", title="Quarterly registrations", tickformat=","),
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Demand concentration + Charger tier ──────────────────────────────────────
col_demand, col_tier = st.columns(2)

with col_demand:
    st.markdown('<p class="section-header">EV Fleet 2027 — Top 10 Provinces</p>', unsafe_allow_html=True)
    st.markdown(
        '<span style="font-size:0.8rem;color:#94A3B8;">'
        'Demand is highly concentrated: Madrid and Barcelona alone account for ~58% of the national '
        '<span class="abbr-tooltip" data-tooltip="Electric Vehicle">EV</span> fleet. '
        'Iberdrola\'s charging rollout must prioritise these two markets first to capture '
        'the majority of interurban charging revenue.'
        '</span>',
        unsafe_allow_html=True,
    )
    df_em = load_emerging()
    top10_prov = df_em.nlargest(10, "ev_fleet_2027").sort_values("ev_fleet_2027")
    fig_prov = px.bar(
        top10_prov,
        x="ev_fleet_2027", y="province_name",
        orientation="h",
        color="ev_fleet_2027",
        color_continuous_scale=["#0A2E1A", "#00B140"],
        text=top10_prov["ev_fleet_2027"].map(lambda v: f"{v:,}"),
        template="plotly_dark",
        labels={"ev_fleet_2027": "EV Fleet 2027", "province_name": "Province"},
    )
    fig_prov.update_traces(textposition="outside", textfont=dict(color="#94A3B8", size=10))
    fig_prov.update_layout(
        paper_bgcolor="#0F172A", plot_bgcolor="#0F172A",
        height=340, margin=dict(t=10, b=10, l=0, r=10),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#1E293B"),
        yaxis=dict(gridcolor="#1E293B"),
    )
    st.plotly_chart(fig_prov, use_container_width=True)

with col_tier:
    st.markdown('<p class="section-header">Current HPC Infrastructure Gap</p>', unsafe_allow_html=True)
    st.markdown(
        '<span style="font-size:0.8rem;color:#94A3B8;">'
        'Today, 98% of Spain\'s public chargers are slow or standard '
        '<span class="abbr-tooltip" data-tooltip="Alternating Current — the standard electricity type used for slow home/destination charging">AC</span> '
        '— unusable for interurban drivers who need a fast top-up and continue. '
        'Only 424 ultra-fast (>150 kW) '
        '<span class="abbr-tooltip" data-tooltip="High Power Charging — DC fast charging ≥150 kW, enabling a meaningful charge in 20–30 min">HPC</span> '
        'units exist nationally. This structural gap is the core opportunity Iberdrola is addressing.'
        '</span>',
        unsafe_allow_html=True,
    )
    tier_labels = ["Slow\n(<22 kW)", "Fast\n(22–50 kW)", "DC Fast\n(50–150 kW)", "Ultra HPC\n(>150 kW)"]
    tier_values = [5951, 3500, 2200, 424]
    tier_colors = ["#334155", "#00A9CE", "#F5A623", "#00B140"]
    fig_tier = go.Figure(go.Pie(
        labels=tier_labels,
        values=tier_values,
        hole=0.55,
        marker=dict(colors=tier_colors, line=dict(color="#0F172A", width=2)),
        textinfo="label+percent",
        textfont=dict(color="#F1F5F9", size=11),
        hovertemplate="%{label}<br>%{value:,} units<br>%{percent}<extra></extra>",
    ))
    fig_tier.add_annotation(
        text="12,075<br><span style='font-size:11px;color:#94A3B8'>total chargers</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="#F1F5F9"),
    )
    fig_tier.update_layout(
        paper_bgcolor="#0F172A",
        height=340, margin=dict(t=10, b=10, l=0, r=0),
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center", font=dict(color="#94A3B8")),
        showlegend=False,
    )
    st.plotly_chart(fig_tier, use_container_width=True)

st.markdown("---")

# ── Scope & Methodology ───────────────────────────────────────────────────────
col_l, col_r = st.columns([1, 1])

with col_l:
    st.markdown('<p class="section-header">Scope of Analysis</p>', unsafe_allow_html=True)
    st.markdown(
        """
        - **Geography:** Interurban Spain — autopistas, autovías, carreteras nacionales
        - **Corridors:** 12 TEN-T strategic axes (A-1, A-2, A-3, A-4, A-5, A-6, AP-7, A-8, A-66, A-23, A-45, A-92)
        - **Target horizon:** 2027 operational scenario
        - **AFIR compliance:** HPC station every ≤ 60 km on TEN-T Core corridors (Regulation EU 2023/1804)
        - **Grid sources:** i-DE (Iberdrola), Endesa, Viesgo substation capacity
        - **Charger standard:** 150 kW per charger (fixed per datathon Rule 2)
        """
    )

with col_r:
    st.markdown('<p class="section-header">Grid Status Legend</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <span class="badge-green">● Sufficient</span>&nbsp; Available capacity ≥ 5 MW
        <br><br>
        <span class="badge-yellow">● Moderate</span>&nbsp; Available capacity 1–5 MW
        <br><br>
        <span class="badge-red">● Congested</span>&nbsp; Available capacity < 1 MW
        <br><br>
        Grid status assigned from nearest distributor substation using KD-tree spatial matching (EPSG:25830).
        """,
        unsafe_allow_html=True,
    )
