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
        "urgente": ("Atención urgente", "urgente"),
        "media": ("Recomendada", "media"),
        "positiva": ("Resultado positivo", "positiva"),
    }
    label, cls = badges.get(pri, ("Recomendada", "media"))
    st.markdown(f"""
    <div class="accion-{cls}">
        <span class="badge-{cls}">{label}</span>
        <div style="margin-top:6px; font-size:0.88rem; color:#1a1a2e; line-height:1.45;">{texto}</div>
    </div>
    """, unsafe_allow_html=True)


def _tiene_datos_reales(data: list, campos_numericos: list) -> bool:
    """Devuelve False si la lista está vacía o si todos los campos numéricos son 0."""
    if not data:
        return False
    for fila in data:
        for campo in campos_numericos:
            valor = fila.get(campo, 0)
            try:
                if float(valor) != 0:
                    return True
            except (TypeError, ValueError):
                continue
    return False


def render_graficas(graficas: dict, meta_mora_pct: float = 5.0):
    g = graficas or {}

    col1, col2 = st.columns(2)

    # 1) Desembolsos vs Cobros por mes
    with col1:
        data = g.get("desembolsos_vs_cobros", [])
        if _tiene_datos_reales(data, ["desembolsado", "cobrado"]):
            df = pd.DataFrame(data)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df["mes"], y=df["desembolsado"],
                                  name="Desembolsado", marker_color="#0a2463"))
            fig.add_trace(go.Bar(x=df["mes"], y=df["cobrado"],
                                  name="Cobrado", marker_color="#1e8449"))
            fig.update_layout(
                title="Desembolsos vs. Cobros por mes",
                barmode="group",
                margin=dict(t=45, b=60),
                height=330,
                font=dict(family="Arial, sans-serif", size=12),
                title_font=dict(size=13, color="#0a2463"),
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
                legend=dict(orientation="h", yanchor="top", y=-0.18, x=0.5, xanchor="center")
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#eef1f7")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Desembolsos vs. Cobros: información no disponible en los documentos.")

    # 2) Tendencia de mora con línea de meta
    with col2:
        data = g.get("tendencia_mora", [])
        if _tiene_datos_reales(data, ["porcentaje_mora"]):
            df = pd.DataFrame(data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["mes"], y=df["porcentaje_mora"],
                mode="lines+markers", name="% Mora",
                line=dict(color="#c0392b", width=2.5),
                marker=dict(size=6)
            ))
            fig.add_hline(
                y=meta_mora_pct, line_dash="dash", line_color="#c89010",
                annotation_text=f"Meta: {meta_mora_pct}%",
                annotation_position="top left",
                annotation_font_color="#c89010"
            )
            fig.update_layout(
                title="Tendencia de mora vs. meta prudencial",
                margin=dict(t=45, b=20),
                height=300,
                font=dict(family="Arial, sans-serif", size=12),
                title_font=dict(size=13, color="#0a2463"),
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#eef1f7")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Tendencia de mora: información no disponible en los documentos.")

    col3, col4 = st.columns(2)

    # 3) Distribución de cartera
    with col3:
        data = g.get("distribucion_cartera", [])
        if _tiene_datos_reales(data, ["monto"]):
            df = pd.DataFrame(data).sort_values("monto", ascending=True)
            fig = px.bar(
                df, x="monto", y="categoria", orientation="h",
                title="Distribución de cartera por categoría",
                color_discrete_sequence=["#0a2463"]
            )
            fig.update_layout(
                margin=dict(t=45, b=20),
                height=300,
                yaxis_title="",
                xaxis_title="",
                font=dict(family="Arial, sans-serif", size=12),
                title_font=dict(size=13, color="#0a2463"),
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
            )
            fig.update_xaxes(showgrid=True, gridcolor="#eef1f7")
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Distribución de cartera: información no disponible en los documentos.")

    # 4) Flujo neto mensual + acumulado
    with col4:
        data = g.get("flujo_neto", [])
        if _tiene_datos_reales(data, ["neto"]):
            df = pd.DataFrame(data)
            df["acumulado"] = df["neto"].cumsum()
            colors_bar = ["#1e8449" if v >= 0 else "#c0392b" for v in df["neto"]]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df["mes"], y=df["neto"],
                name="Flujo neto mensual",
                marker_color=colors_bar
            ))
            fig.add_trace(go.Scatter(
                x=df["mes"], y=df["acumulado"],
                name="Acumulado",
                mode="lines+markers",
                line=dict(color="#0a2463", width=2),
                marker=dict(size=5),
                yaxis="y2"
            ))
            fig.update_layout(
                title="Flujo neto mensual y acumulado",
                margin=dict(t=45, b=60),
                height=330,
                font=dict(family="Arial, sans-serif", size=12),
                title_font=dict(size=13, color="#0a2463"),
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
                yaxis=dict(title="Mensual", gridcolor="#eef1f7"),
                yaxis2=dict(title="Acumulado", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", yanchor="top", y=-0.18, x=0.5, xanchor="center")
            )
            fig.update_xaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Flujo neto: información no disponible en los documentos.")

    # 5) Mora por antigüedad (centrado)
    data = g.get("mora_por_antiguedad", [])
    if _tiene_datos_reales(data, ["monto"]):
        col5, col6, col7 = st.columns([1, 2, 1])
        with col6:
            df = pd.DataFrame(data)
            colors_aging = ["#c89010", "#d4730a", "#c0550a", "#c0392b"]
            fig = px.bar(
                df, x="rango", y="monto",
                title="Cartera en mora por antigüedad",
                color="rango",
                color_discrete_sequence=colors_aging
            )
            fig.update_layout(
                margin=dict(t=45, b=20),
                height=320,
                showlegend=False,
                xaxis_title="",
                yaxis_title="",
                font=dict(family="Arial, sans-serif", size=12),
                title_font=dict(size=13, color="#0a2463"),
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#eef1f7")
            st.plotly_chart(fig, use_container_width=True)


def render_highlights(resumen):
    """Muestra el resumen como puntos clave del informe."""
    if isinstance(resumen, str):
        items = [s.strip() for s in resumen.replace("\n", " ").split(". ") if s.strip()]
    else:
        items = [str(item).strip() for item in (resumen or []) if str(item).strip()]

    if not items:
        st.info("No hay resumen disponible.")
        return

    for item in items:
        texto = escape_dollar(item)
        st.markdown(f"""
        <div style="background:#f5f8ff; border-left:3px solid #0a2463; border-radius:4px;
             padding:0.65rem 1rem; margin-bottom:0.5rem; color:#1a1a2e; font-size:0.88rem;
             line-height:1.5;">
            {texto}
        </div>
        """, unsafe_allow_html=True)


def render_dashboard():
    coop = st.session_state.get("coop_nombre", "Cooperativa")

    st.markdown(f"## {coop}")
    st.markdown(
        "<p style='color:#6b7a99; font-size:0.9rem; margin-top:-0.5rem;'>"
        "Cargue los estados financieros para generar el informe ejecutivo."
        "</p>",
        unsafe_allow_html=True
    )
    st.divider()

    # ── CARGA DE ARCHIVOS ──────────────────────────────────
    archivos = st.file_uploader(
        "Carga de estados financieros (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Puede subir varios PDFs: balance general, cartera de créditos, estados de resultados, etc."
    )

    if archivos:
        st.success(f"{len(archivos)} archivo(s) cargado(s): {', '.join([a.name for a in archivos])}")

    col_btn1, col_btn2, _ = st.columns([1, 1, 2])
    with col_btn1:
        generar = st.button(
            "Generar informe",
            type="primary",
            disabled=not archivos,
            use_container_width=True
        )
    with col_btn2:
        if st.button("Nueva consulta", use_container_width=True):
            st.session_state.pop("analisis_result", None)
            st.rerun()

    # ── PROCESAMIENTO ──────────────────────────────────────
    if generar and archivos:
        with st.spinner("Procesando documentos. Esto puede tomar un momento..."):
            try:
                result = analizar_pdfs(archivos)
                st.session_state.analisis_result = result
            except Exception as e:
                st.error(f"Error en el procesamiento: {e}")
                return

    result = st.session_state.get("analisis_result")

    if not result:
        st.info("Cargue los estados financieros y presione **Generar informe** para visualizar los resultados.")
        return

    st.divider()
    st.markdown("## Resultados del informe")

    # ── INDICADORES FINANCIEROS ────────────────────────────
    kpis = result.get("kpis", {})
    k1, k2, k3 = st.columns(3)
    k4, k5, k6 = st.columns(3)

    kpi_items = [
        ("Capital total",          kpis.get("capital_total", "N/D"),            ""),
        ("Total prestado",         kpis.get("total_prestado", "N/D"),           ""),
        ("Total cobrado",          kpis.get("total_cobrado", "N/D"),            ""),
        ("Porcentaje de recuperación", kpis.get("porcentaje_recuperacion", "N/D"), ""),
        ("Mora estimada",          kpis.get("mora_estimada", "N/D"),            "Requiere seguimiento"),
        ("Total de socios",        kpis.get("total_socios", "N/D"),             ""),
    ]

    for col, (label, val, sub) in zip([k1, k2, k3, k4, k5, k6], kpi_items):
        with col:
            render_kpi(label, val, sub)

    st.divider()

    # ── GRÁFICAS ───────────────────────────────────────────
    st.markdown("### Indicadores gráficos")
    meta_mora = result.get("meta_mora_pct", 5)
    try:
        meta_mora = float(meta_mora)
    except (TypeError, ValueError):
        meta_mora = 5.0
    render_graficas(result.get("graficas", {}), meta_mora_pct=meta_mora)

    st.divider()

    # ── RESUMEN + ACCIONES ─────────────────────────────────
    left, right = st.columns([1.6, 1])

    with left:
        st.markdown("### Resumen ejecutivo")
        render_highlights(result.get("resumen", []))

    with right:
        st.markdown("### Acciones recomendadas")
        for acc in result.get("acciones", []):
            render_accion(acc)

    st.divider()

    # ── DESCARGA PDF ───────────────────────────────────────
    try:
        pdf_bytes = build_pdf(
            coop_nombre=coop,
            kpis=kpis,
            resumen=result.get("resumen", ""),
            acciones=result.get("acciones", [])
        )
        st.download_button(
            "Descargar informe ejecutivo (PDF)",
            data=pdf_bytes,
            file_name=f"CAI_Informe_{coop.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=False,
        )
    except Exception as e:
        st.warning(f"No se pudo generar el PDF: {e}")
