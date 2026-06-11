"""
CAI Cooperativas – Análisis Ejecutivo con IA
app.py — Punto de entrada principal
"""

import streamlit as st

st.set_page_config(
    page_title="CAI Cooperativas",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS global
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
.metric-card {
    background: #f0f4ff;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    border-left: 4px solid #3b5bdb;
}
.metric-label { font-size: 0.82rem; color: #555; margin-bottom: 2px; }
.metric-value { font-size: 1.45rem; font-weight: 700; color: #1a1a2e; }
.metric-sub { font-size: 0.78rem; color: #888; }
.accion-urgente { background:#fff1f0; border-left:4px solid #e03131; padding:0.7rem 1rem; border-radius:8px; margin-bottom:0.4rem; }
.accion-media   { background:#fff9db; border-left:4px solid #f59f00; padding:0.7rem 1rem; border-radius:8px; margin-bottom:0.4rem; }
.accion-positiva{ background:#ebfbee; border-left:4px solid #2f9e44; padding:0.7rem 1rem; border-radius:8px; margin-bottom:0.4rem; }
.badge-urgente  { background:#e03131; color:white; border-radius:4px; padding:1px 7px; font-size:0.72rem; font-weight:700; }
.badge-media    { background:#f59f00; color:white; border-radius:4px; padding:1px 7px; font-size:0.72rem; font-weight:700; }
.badge-positiva { background:#2f9e44; color:white; border-radius:4px; padding:1px 7px; font-size:0.72rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# Importar módulos
from modules.auth import check_login, logout
from modules.dashboard import render_dashboard

# ── AUTENTICACIÓN ──────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    check_login()
else:
    # Sidebar
    with st.sidebar:
        st.image("assets/logo_cai.png", width=140) if __import__("os").path.exists("assets/logo_cai.png") else st.markdown("## 🏦 CAI Cooperativas")
        st.markdown(f"**{st.session_state.get('coop_nombre', 'Cooperativa')}**")
        st.caption(f"Usuario: {st.session_state.get('username', '')}")
        st.divider()
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            logout()

    render_dashboard()
