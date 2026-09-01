"""
Módulo de reporte PDF — CAI Cooperativas
Genera informe ejecutivo financiero descargable con ReportLab.
"""

import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas


BRAND_NAME   = "CAI Cooperativas"
BRAND_SUB    = "Informe Ejecutivo Financiero"
LOGO_PATH    = "assets/logo_cai.png"

COLOR_PRIMARY  = colors.HexColor("#0a2463")
COLOR_URGENTE  = colors.HexColor("#c0392b")
COLOR_MEDIA    = colors.HexColor("#c89010")
COLOR_POSITIVA = colors.HexColor("#1e8449")
COLOR_RULE     = colors.HexColor("#dce3ef")
COLOR_LABEL    = colors.HexColor("#6b7a99")


def wrap_text(text: str, max_chars: int) -> list:
    words = str(text).split()
    lines, cur = [], []
    for w in words:
        if sum(len(x) for x in cur) + len(cur) + len(w) <= max_chars:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def build_pdf(coop_nombre: str, kpis: dict, resumen, acciones: list) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin_l = 0.85 * inch
    margin_r = width - 0.85 * inch
    y = height - 0.80 * inch

    # Número de referencia y fecha de emisión
    ref_num  = datetime.now().strftime("CAI-%Y%m%d-%H%M")
    fecha_emision = datetime.now().strftime("%d de %B de %Y").upper()

    # ── ENCABEZADO ──────────────────────────────────────────
    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, margin_l, y - 0.85 * inch,
                    width=0.85 * inch, height=0.85 * inch, mask="auto")
        tx = margin_l + 1.05 * inch
    else:
        tx = margin_l

    # Nombre de la organización
    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(tx, y, BRAND_NAME)

    c.setFont("Helvetica", 9)
    c.setFillColor(COLOR_LABEL)
    c.drawString(tx, y - 0.20 * inch, BRAND_SUB)
    c.drawString(tx, y - 0.36 * inch, f"Cooperativa:  {coop_nombre}")
    c.drawString(tx, y - 0.50 * inch, f"Fecha de emisión:  {fecha_emision}")

    # Referencia alineada a la derecha
    c.setFont("Helvetica", 8)
    ref_label = f"Ref. {ref_num}"
    c.drawRightString(margin_r, y, ref_label)

    # Línea separadora doble
    c.setStrokeColor(COLOR_PRIMARY)
    c.setLineWidth(2)
    c.line(margin_l, y - 0.68 * inch, margin_r, y - 0.68 * inch)
    c.setStrokeColor(COLOR_RULE)
    c.setLineWidth(0.5)
    c.line(margin_l, y - 0.71 * inch, margin_r, y - 0.71 * inch)

    y -= 0.95 * inch

    # ── SECCIÓN: INDICADORES FINANCIEROS CLAVE ───────────────
    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_l, y, "I.   INDICADORES FINANCIEROS CLAVE")
    y -= 0.06 * inch
    c.setStrokeColor(COLOR_RULE)
    c.setLineWidth(0.5)
    c.line(margin_l, y, margin_r, y)
    y -= 0.22 * inch

    kpi_labels = {
        "capital_total":            "Capital total",
        "total_prestado":           "Total desembolsado",
        "total_cobrado":            "Total cobrado",
        "porcentaje_recuperacion":  "Porcentaje de recuperación",
        "mora_estimada":            "Mora estimada",
        "total_socios":             "Total de socios / asociados",
    }

    c.setFont("Helvetica", 9.5)
    for key, label in kpi_labels.items():
        val = kpis.get(key, "N/D")
        c.setFillColor(COLOR_LABEL)
        c.drawString(margin_l + 0.15 * inch, y, label)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(margin_l + 2.7 * inch, y, str(val))
        c.setFont("Helvetica", 9.5)
        y -= 0.21 * inch
        if y < 1.5 * inch:
            _new_page(c, width, height, margin_l, margin_r)
            y = height - 0.85 * inch

    y -= 0.14 * inch

    # ── SECCIÓN: RESUMEN EJECUTIVO ────────────────────────────
    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_l, y, "II.  RESUMEN EJECUTIVO")
    y -= 0.06 * inch
    c.setStrokeColor(COLOR_RULE)
    c.setLineWidth(0.5)
    c.line(margin_l, y, margin_r, y)
    y -= 0.22 * inch

    highlights = resumen if isinstance(resumen, list) else [resumen]
    c.setFont("Helvetica", 9.5)
    for idx, punto in enumerate(highlights, start=1):
        if not str(punto).strip():
            continue
        lineas = wrap_text(str(punto), 92)
        for i, line in enumerate(lineas):
            prefix = f"{idx}.  " if i == 0 else "     "
            c.setFillColor(colors.black if i == 0 else COLOR_LABEL)
            c.drawString(margin_l + 0.15 * inch, y, f"{prefix}{line}")
            y -= 0.19 * inch
            if y < 1.5 * inch:
                _new_page(c, width, height, margin_l, margin_r)
                y = height - 0.85 * inch
                c.setFont("Helvetica", 9.5)
        y -= 0.06 * inch

    y -= 0.14 * inch

    # ── SECCIÓN: ACCIONES Y RECOMENDACIONES ──────────────────
    if y < 2.5 * inch:
        _new_page(c, width, height, margin_l, margin_r)
        y = height - 0.85 * inch

    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_l, y, "III. ACCIONES Y RECOMENDACIONES")
    y -= 0.06 * inch
    c.setStrokeColor(COLOR_RULE)
    c.setLineWidth(0.5)
    c.line(margin_l, y, margin_r, y)
    y -= 0.22 * inch

    prioridad_map = {
        "urgente":  ("PRIORIDAD ALTA",     COLOR_URGENTE),
        "media":    ("RECOMENDADA",         COLOR_MEDIA),
        "positiva": ("RESULTADO POSITIVO",  COLOR_POSITIVA),
    }

    for acc in acciones:
        pri = acc.get("prioridad", "media")
        label, color = prioridad_map.get(pri, ("RECOMENDADA", COLOR_MEDIA))

        # Badge de prioridad
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(color)
        c.drawString(margin_l + 0.15 * inch, y, label)
        y -= 0.17 * inch

        # Texto de la acción
        c.setFont("Helvetica", 9.5)
        for i, line in enumerate(wrap_text(acc.get("texto", ""), 90)):
            c.setFillColor(colors.black)
            c.drawString(margin_l + 0.30 * inch, y, line)
            y -= 0.19 * inch

        y -= 0.09 * inch

        if y < 1.5 * inch:
            _new_page(c, width, height, margin_l, margin_r)
            y = height - 0.85 * inch

    # ── PIE DE PÁGINA ──────────────────────────────────────
    _draw_footer(c, width, ref_num)

    c.save()
    buffer.seek(0)
    return buffer.read()


def _new_page(c, width, height, margin_l, margin_r):
    """Abre nueva página y dibuja encabezado reducido."""
    c.showPage()
    # Línea superior mínima
    c.setStrokeColor(COLOR_PRIMARY)
    c.setLineWidth(1.5)
    c.line(margin_l, height - 0.45 * inch, margin_r, height - 0.45 * inch)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(COLOR_PRIMARY)
    c.drawString(margin_l, height - 0.36 * inch, f"{BRAND_NAME}  ·  {BRAND_SUB}")
    _draw_footer(c, width, "")


def _draw_footer(c, width, ref_num: str):
    """Dibuja pie de página en la página actual."""
    margin_l = 0.85 * inch
    margin_r = width - 0.85 * inch
    c.setStrokeColor(COLOR_RULE)
    c.setLineWidth(0.5)
    c.line(margin_l, 0.70 * inch, margin_r, 0.70 * inch)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(COLOR_LABEL)
    c.drawString(margin_l, 0.52 * inch, f"{BRAND_NAME}  ·  Informe Confidencial")
    if ref_num:
        c.drawRightString(margin_r, 0.52 * inch, f"Ref. {ref_num}")
