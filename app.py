"""
CAI Cooperativas – Sistema de Análisis Financiero
app.py — Punto de entrada principal
"""

import streamlit as st

st.set_page_config(
    page_title="CAI Cooperativas",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS global — diseño corporativo financiero
st.markdown("""
<style>
/* --- Layout base --- */
.block-container { padding-top: 1.5rem; }

/* --- Tarjetas KPI --- */
.metric-card {
    background: #ffffff;
    border: 1px solid #dce3ef;
    border-top: 3px solid #0a2463;
    border-radius: 5px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.metric-label {
    font-size: 0.72rem;
    color: #6b7a99;
    margin-bottom: 5px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}
.metric-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #0a2463;
    line-height: 1.2;
}
.metric-sub {
    font-size: 0.72rem;
    color: #b5452a;
    margin-top: 4px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* --- Tarjetas de acciones --- */
.accion-urgente {
    background: #fff6f5;
    border-left: 3px solid #c0392b;
    padding: 0.65rem 0.9rem;
    border-radius: 4px;
    margin-bottom: 0.45rem;
}
.accion-media {
    background: #fffcf0;
    border-left: 3px solid #c89010;
    padding: 0.65rem 0.9rem;
    border-radius: 4px;
    margin-bottom: 0.45rem;
}
.accion-positiva {
    background: #f3fbf5;
    border-left: 3px solid #1e8449;
    padding: 0.65rem 0.9rem;
    border-radius: 4px;
    margin-bottom: 0.45rem;
}

/* --- Badges de prioridad --- */
.badge-urgente {
    background: #c0392b;
    color: white;
    border-radius: 3px;
    padding: 1px 6px;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
.badge-media {
    background: #c89010;
    color: white;
    border-radius: 3px;
    padding: 1px 6px;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
.badge-positiva {
    background: #1e8449;
    color: white;
    border-radius: 3px;
    padding: 1px 6px;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}

/* --- Sidebar corporativo --- */
[data-testid="stSidebar"] { background: #0a2463 !important; }
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #cdd5e8 !important; }
[data-testid="stSidebar"] strong { color: #ffffff !important; }
[data-testid="stSidebar"] hr { border-color: #1e3a70 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid #2d4e8a !important;
    color: #cdd5e8 !important;
    font-size: 0.85rem;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1a3566 !important;
    border-color: #4a6db5 !important;
}
</style>
""", unsafe_allow_html=True)

from modules.auth import check_login, logout
from modules.dashboard import render_dashboard

# ── AUTENTICACIÓN ──────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    check_login()
else:
    with st.sidebar:
        import os
        if os.path.exists("assets/logo_cai.png"):
            st.image("assets/logo_cai.png", width=130)
        else:
            st.markdown("### CAI Cooperativas")
        st.markdown(f"**{st.session_state.get('coop_nombre', 'Cooperativa')}**")
        st.caption(f"Usuario: {st.session_state.get('username', '')}")
        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            logout()

    render_dashboard()
