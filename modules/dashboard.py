"""
Módulo del dashboard — CAI Cooperativas
Pantalla principal después del login.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from modules.ia import analizar_pdfs
from modules.pdf_report import build_pdf


def escape_dollar(text: str) -> str:
    """Evita que Streamlit interprete '$' como delimitador de LaTeX."""
    return str(text).replace("$", "\\$")


def render_kpi(label: str, value: str, sub: str = ""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {"<div class='metric-sub'>" + sub + "</div>" if sub else ""}
    </div>
    """, unsafe_allow_html=True)


def render_accion(accion: dict):
    pri = accion.get("prioridad", "media")
    texto = escape_dollar(accion.get("texto", ""))
    badges = {
        "urgente": ("⚠ Acción urgente", "urgente"),
        "media": ("→ Recomendada", "media"),
        "positiva": ("✓ Punto positivo", "positiva"),
    }
    label, cls = badges.get(pri, ("→", "media"))
    st.markdown(f"""
    <div class="accion-{cls}">
        <span class="badge-{cls}">{label}</span>
        <div style="margin-top:5px; font-size:0.9rem; color:#1a1a2e;">{texto}</div>
    </div>
    """, unsafe_allow_html=True)


def render_graficas(graficas: dict):
    g = graficas or {}

    col1, col2 = st.columns(2)

    # 1) Préstamos por mes
    with col1:
        data = g.get("prestamos_por_mes", [])
        if data:
            df = pd.DataFrame(data)
            fig = px.bar(df, x="mes", y="monto", title="💰 Monto prestado por mes",
                         color_discrete_sequence=["#3b5bdb"])
            fig.update_layout(margin=dict(t=40, b=20), height=280)
            st.plotly_chart(fig, use_container_width=True)

    # 2) % Recuperación por mes
    with col2:
        data = g.get("recuperacion_por_mes", [])
        if data:
            df = pd.DataFrame(data)
            fig = px.line(df, x="mes", y="porcentaje", title="📈 % Recuperación mensual",
                          markers=True, color_discrete_sequence=["#2f9e44"])
            fig.update_layout(margin=dict(t=40, b=20), height=280)
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    # 3) Distribución cartera
    with col3:
        data = g.get("distribucion_cartera", [])
        if data:
            df = pd.DataFrame(data)
            fig = px.pie(df, names="categoria", values="monto", hole=0.45,
                         title="🗂 Distribución de cartera")
            fig.update_layout(margin=dict(t=40, b=20), height=280)
            st.plotly_chart(fig, use_container_width=True)

    # 4) Flujo neto
    with col4:
        data = g.get("flujo_neto", [])
        if data:
            df = pd.DataFrame(data)
            colors_bar = ["#2f9e44" if v >= 0 else "#e03131" for v in df["neto"]]
            fig = go.Figure(go.Bar(x=df["mes"], y=df["neto"],
                                   marker_color=colors_bar, name="Flujo neto"))
            fig.update_layout(title="📊 Flujo neto mensual",
                               margin=dict(t=40, b=20), height=280)
            st.plotly_chart(fig, use_container_width=True)

    # 5) Estado mora (centrado)
    data = g.get("estado_mora", [])
    if data:
        col5, col6, col7 = st.columns([1, 2, 1])
        with col6:
            df = pd.DataFrame(data)
            fig = px.pie(df, names="estado",
