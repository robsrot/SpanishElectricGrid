import streamlit as st

SHARED_CSS = """
<style>
[data-testid="stSidebarNav"] { display: none; }

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
.phase-1 { border-color: #3B82F6; }
.phase-2 { border-color: #F59E0B; }
.phase-3 { border-color: #10B981; }
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
        st.markdown("---")
        st.caption("Model: SARIMA(1,1,1)×(1,0,1,12)")
        st.caption("Source: datos.gob.es · DGT · i-DE · Endesa · Viesgo")
