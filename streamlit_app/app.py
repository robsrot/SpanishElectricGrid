import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import SAMPLE_NOTICE, load_file1, load_forecast
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
st.caption("Quarterly data · BEV + PHEV + REEV + FCEV · Source: datos.gob.es fork (mandatory)")

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
    line=dict(color="#60A5FA", width=2.5, dash="dash"),
    mode="lines+markers",
    marker=dict(size=5, symbol="diamond"),
))

# 2027 annotation
last = forecast.iloc[-1]
fig.add_annotation(
    x=last["date"], y=last["ev_registrations"],
    text=f"<b>{last['ev_registrations']:,} EVs/qtr</b>",
    showarrow=True, arrowhead=2, arrowcolor="#60A5FA",
    font=dict(color="#60A5FA", size=12),
    bgcolor="#1E293B", bordercolor="#60A5FA", borderwidth=1,
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
