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
    texto = accion.get("texto", "")
    badges = {
        "urgente": ("⚠ Acción urgente", "urgente"),
        "media": ("→ Recomendada", "media"),
        "positiva": ("✓ Punto positivo", "positiva"),
    }
    label, cls = badges.get(pri, ("→", "media"))
    st.markdown(f"""
    <div class="accion-{cls}">
        <span class="badge-{cls}">{label}</span>
        <div style="margin-top:5px; font-size:0.9rem;">{texto}</div>
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
            fig = px.pie(df, names="estado", values="monto",
                         title="🔴 Estado de mora vs al día",
                         color="estado",
                         color_discrete_map={"Al día": "#2f9e44", "En mora": "#e03131"})
            fig.update_layout(margin=dict(t=40, b=20), height=300)
            st.plotly_chart(fig, use_container_width=True)


def render_dashboard():
    coop = st.session_state.get("coop_nombre", "Cooperativa")

    st.markdown(f"## 🏦 {coop}")
    st.markdown("Sube los estados financieros para generar tu análisis ejecutivo.")
    st.divider()

    # ── SUBIDA DE ARCHIVOS ──────────────────────────────
    archivos = st.file_uploader(
        "📎 Sube tus reportes financieros (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Puedes subir varios PDFs a la vez: balance, cartera, resultados, etc."
    )

    if archivos:
        st.success(f"✅ {len(archivos)} archivo(s) listo(s): {', '.join([a.name for a in archivos])}")

    col_btn1, col_btn2, _ = st.columns([1, 1, 2])
    with col_btn1:
        generar = st.button("🤖 Generar análisis", type="primary",
                            disabled=not archivos, use_container_width=True)
    with col_btn2:
        if st.button("🗑 Limpiar", use_container_width=True):
            st.session_state.pop("analisis_result", None)
            st.rerun()

    # ── ANÁLISIS ────────────────────────────────────────
    if generar and archivos:
        with st.spinner("La IA está analizando tus documentos... esto toma unos segundos."):
            try:
                result = analizar_pdfs(archivos)
                st.session_state.analisis_result = result
            except Exception as e:
                st.error(f"Error al analizar: {e}")
                return

    result = st.session_state.get("analisis_result")

    if not result:
        st.info("Sube tus PDFs y presiona **Generar análisis** para ver los resultados.")
        return

    st.divider()
    st.markdown("## 📊 Resultados del análisis")

    # ── KPIs ────────────────────────────────────────────
    kpis = result.get("kpis", {})
    k1, k2, k3 = st.columns(3)
    k4, k5, k6 = st.columns(3)

    kpi_items = [
        ("Capital total", kpis.get("capital_total", "N/D"), ""),
        ("Total prestado", kpis.get("total_prestado", "N/D"), ""),
        ("Total cobrado", kpis.get("total_cobrado", "N/D"), ""),
        ("% Recuperación", kpis.get("porcentaje_recuperacion", "N/D"), ""),
        ("Mora estimada", kpis.get("mora_estimada", "N/D"), "⚠ Monitorear"),
        ("Total socios", kpis.get("total_socios", "N/D"), ""),
    ]

    for col, (label, val, sub) in zip([k1, k2, k3, k4, k5, k6], kpi_items):
        with col:
            render_kpi(label, val, sub)

    st.divider()

    # ── GRÁFICAS ────────────────────────────────────────
    st.markdown("### 📈 Gráficas")
    render_graficas(result.get("graficas", {}))

    st.divider()

    # ── RESUMEN + ACCIONES ──────────────────────────────
    left, right = st.columns([1.6, 1])

    with left:
        st.markdown("### 📝 Resumen ejecutivo")
        st.write(result.get("resumen", ""))

    with right:
        st.markdown("### ✅ Acciones recomendadas")
        for acc in result.get("acciones", []):
            render_accion(acc)

    st.divider()

    # ── DESCARGA PDF ────────────────────────────────────
    try:
        pdf_bytes = build_pdf(
            coop_nombre=coop,
            kpis=kpis,
            resumen=result.get("resumen", ""),
            acciones=result.get("acciones", [])
        )
        st.download_button(
            "📄 Descargar reporte ejecutivo PDF",
            data=pdf_bytes,
            file_name=f"CAI_Reporte_{coop.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=False,
        )
    except Exception as e:
        st.warning(f"No se pudo generar el PDF: {e}")
