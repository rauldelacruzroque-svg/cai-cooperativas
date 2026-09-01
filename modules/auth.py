"""
Módulo de autenticación — CAI Cooperativas
Usa Supabase como base de datos de usuarios.
"""

import streamlit as st
from supabase import create_client, Client
import hashlib


def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_login():
    st.markdown("""
    <style>
    .stApp { background: #eef1f7 !important; }
    .block-container {
        max-width: 440px !important;
        margin: 0 auto !important;
        padding-top: 5rem !important;
    }
    .login-logo {
        text-align: center;
        margin-bottom: 1.8rem;
    }
    .login-org {
        font-size: 1.55rem;
        font-weight: 800;
        color: #0a2463;
        letter-spacing: -0.3px;
        margin-bottom: 0.2rem;
    }
    .login-system {
        font-size: 0.75rem;
        color: #8a96b4;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 500;
    }
    .login-card {
        background: #ffffff;
        border-radius: 6px;
        padding: 2.5rem 2.2rem 2rem 2.2rem;
        box-shadow: 0 2px 8px rgba(10,36,99,0.08), 0 1px 2px rgba(10,36,99,0.04);
        border: 1px solid #dce3ef;
    }
    .login-footer {
        text-align: center;
        margin-top: 1.8rem;
        font-size: 0.75rem;
        color: #9aa5c0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-logo">
        <div class="login-org">CAI Cooperativas</div>
        <div class="login-system">Sistema de Análisis Financiero</div>
    </div>
    <div class="login-card">
    """, unsafe_allow_html=True)

    username = st.text_input(
        "Usuario",
        placeholder="usuario@cooperativa.com",
        label_visibility="visible"
    )
    password = st.text_input(
        "Contraseña",
        type="password",
        placeholder="Ingrese su contraseña",
        label_visibility="visible"
    )

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    if st.button("Acceder", use_container_width=True, type="primary"):
        if not username or not password:
            st.error("Ingrese su usuario y contraseña.")
            return
        try:
            supabase = get_supabase()
            hashed = hash_password(password)
            res = supabase.table("cooperativas_usuarios") \
                .select("*") \
                .eq("username", username.strip().lower()) \
                .eq("password_hash", hashed) \
                .eq("activo", True) \
                .execute()

            if res.data and len(res.data) > 0:
                user = res.data[0]
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.coop_nombre = user.get("nombre_cooperativa", "Cooperativa")
                st.session_state.coop_id = user.get("id")
                st.rerun()
            else:
                st.error("Credenciales incorrectas o cuenta inactiva.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="login-footer">
        ¿Problemas para acceder? Contacte a su administrador CAI.
    </div>
    """, unsafe_allow_html=True)


def logout():
    for key in ["logged_in", "username", "coop_nombre", "coop_id", "analisis_result"]:
        st.session_state.pop(key, None)
    st.rerun()
