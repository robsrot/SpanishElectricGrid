import streamlit as st

SHARED_CSS = """
<style>
[data-testid="stSidebarNav"] { display: none; }

.abbr-tooltip {
    border-bottom: 1px dotted #94A3B8;
    cursor: help;
    position: relative;
    display: inline-block;
}
.abbr-tooltip::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 130%;
    left: 50%;
    transform: translateX(-50%);
    background: #1E293B;
    color: #F1F5F9;
    padding: 7px 12px;
    border-radius: 6px;
    font-size: 0.75rem;
    white-space: normal;
    width: 230px;
    text-align: center;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.15s;
    z-index: 9999;
    border: 1px solid #334155;
    line-height: 1.4;
}
.abbr-tooltip:hover::after {
    opacity: 1;
}

.kpi-card {
    background: #1E293B;
    border-radius: 12px;
    padding: 20px 24px;
    border-left: 4px solid #00B140;
    margin-bottom: 8px;
}
.kpi-value { font-size: 2.2rem; font-weight: 700; color: #F1F5F9; margin: 0; }
.kpi-label { font-size: 0.85rem; color: #94A3B8; margin: 0; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-delta { font-size: 0.8rem; color: #00B140; margin-top: 4px; }
.section-header { color: #00B140; font-size: 1.1rem; font-weight: 600; margin-bottom: 0; }
.badge-green  { background:#166534; color:#86EFAC; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-yellow { background:#713F12; color:#FDE68A; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-red    { background:#7F1D1D; color:#FCA5A5; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.logo-text { font-size: 1.6rem; font-weight: 800; color: #00B140; letter-spacing: -0.02em; }
.logo-sub  { font-size: 0.72rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.1em; }
.phase-card {
    background: #1E293B;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    border-left: 4px solid;
}
.phase-1 { border-color: #00A9CE; }
.phase-2 { border-color: #F5A623; }
.phase-3 { border-color: #7DC855; }
.phase-title { font-weight: 700; font-size: 0.95rem; color: #F1F5F9; }
.phase-body  { font-size: 0.85rem; color: #94A3B8; margin-top: 6px; }
</style>
"""


def render_sidebar() -> None:
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown(
            '<p class="logo-text">⚡ Iberdrola</p>'
            '<p class="logo-sub">IE Sustainability Datathon · March 2026</p>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("**Navigation**")
        st.page_link("app.py",                        label="Home — Executive Overview", icon="🏠")
        st.page_link("pages/1_Charging_Network.py",   label="Charging Network (Obj. 1)", icon="🗺️")
        st.page_link("pages/2_Grid_Viability.py",     label="Grid Viability (Obj. 2)",   icon="⚡")
        st.page_link("pages/3_Strategic_Markets.py",  label="Strategic Markets (Obj. 3)",icon="📈")
        st.page_link("pages/4_Interactive_Maps.py",    label="Interactive Maps",           icon="🌍")
        st.markdown("---")
        st.markdown(
            '<span style="font-size:0.75rem;color:#64748B;">'
            'Model: <span class="abbr-tooltip" data-tooltip="Seasonal AutoRegressive Integrated Moving Average — statistical time series forecasting model">SARIMA</span>(1,1,1)×(1,0,1,12)'
            '</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span style="font-size:0.75rem;color:#64748B;">'
            'Source: datos.gob.es · '
            '<span class="abbr-tooltip" data-tooltip="Dirección General de Tráfico — Spain\'s traffic authority and charger registry">DGT</span> · '
            '<span class="abbr-tooltip" data-tooltip="Iberdrola Distribución Eléctrica — Iberdrola\'s regulated grid subsidiary">i-DE</span> · '
            'Endesa · Viesgo'
            '</span>',
            unsafe_allow_html=True,
        )
