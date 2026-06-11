"""
Módulo de autenticación — CAI Cooperativas
Usa Supabase como base de datos de usuarios.
"""

import streamlit as st
from supabase import create_client, Client
import hashlib
import os


def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_login():
    st.markdown("""
    <div style='max-width:420px; margin:80px auto 0 auto; padding:2.5rem;
         background:white; border-radius:16px; box-shadow:0 4px 24px rgba(0,0,0,0.10);'>
        <h2 style='text-align:center; color:#1a1a2e; margin-bottom:0.3rem;'>🏦 CAI Cooperativas</h2>
        <p style='text-align:center; color:#888; margin-bottom:1.8rem; font-size:0.9rem;'>
            Análisis ejecutivo con Inteligencia Artificial
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Iniciar sesión")
            username = st.text_input("Usuario", placeholder="usuario@cooperativa.com")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")

            if st.button("Entrar →", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("Ingresa usuario y contraseña.")
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
                        st.error("Usuario o contraseña incorrectos, o cuenta inactiva.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("¿Problemas para entrar? Contacta a tu administrador CAI.")


def logout():
    for key in ["logged_in", "username", "coop_nombre", "coop_id", "analisis_result"]:
        st.session_state.pop(key, None)
    st.rerun()
