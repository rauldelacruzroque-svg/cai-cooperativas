"""
Módulo de reporte PDF — CAI Cooperativas
Genera reporte ejecutivo descargable con ReportLab.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas


BRAND = "CAI Cooperativas – Análisis Ejecutivo"
LOGO_PATH = "assets/logo_cai.png"
COLOR_PRIMARY = colors.HexColor("#3b5bdb")
COLOR_URGENTE = colors.HexColor("#e03131")
COLOR_MEDIA = colors.HexColor("#f59f00")
COLOR_POSITIVA = colors.HexColor("#2f9e44")


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


def build_pdf(coop_nombre: str, kpis: dict, resumen: str, acciones: list) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    x = 0.75 * inch
    y = height - 0.85 * inch

    # ── HEADER ──────────────────────────────────────────
    import os
    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, x, y - 0.9 * inch, width=0.9 * inch, height=0.9 * inch, mask="auto")
        tx = x + 1.1 * inch
    else:
        tx = x

    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(tx, y, BRAND)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(tx, y - 0.22 * inch, f"Cooperativa: {coop_nombre}")
    c.drawString(tx, y - 0.40 * inch, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Línea separadora
    c.setStrokeColor(COLOR_PRIMARY)
    c.setLineWidth(1.5)
    c.line(x, y - 0.58 * inch, width - 0.75 * inch, y - 0.58 * inch)
    y = y - 0.85 * inch

    # ── KPIs ────────────────────────────────────────────
    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x, y, "Indicadores Clave (KPIs)")
    c.setFillColor(colors.black)
    y -= 0.28 * inch

    kpi_labels = {
        "capital_total": "Capital total",
        "total_prestado": "Total prestado",
        "total_cobrado": "Total cobrado",
        "porcentaje_recuperacion": "% Recuperación",
        "mora_estimada": "Mora estimada",
        "total_socios": "Total socios",
    }

    c.setFont("Helvetica", 10)
    for key, label in kpi_labels.items():
        val = kpis.get(key, "N/D")
        c.drawString(x + 0.2 * inch, y, f"• {label}:  {val}")
        y -= 0.20 * inch
        if y < 1.5 * inch:
            c.showPage(); y = height - 0.85 * inch; c.setFont("Helvetica", 10)

    y -= 0.12 * inch

    # ── RESUMEN EJECUTIVO ────────────────────────────────
    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x, y, "Resumen Ejecutivo")
    c.setFillColor(colors.black)
    y -= 0.25 * inch

    c.setFont("Helvetica", 10)
    for line in wrap_text(resumen, 95):
        c.drawString(x + 0.2 * inch, y, line)
        y -= 0.18 * inch
        if y < 1.5 * inch:
            c.showPage(); y = height - 0.85 * inch; c.setFont("Helvetica", 10)

    y -= 0.15 * inch

    # ── ACCIONES ─────────────────────────────────────────
    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x, y, "Acciones Recomendadas")
    c.setFillColor(colors.black)
    y -= 0.25 * inch

    prioridad_map = {
        "urgente": ("⚠ URGENTE", COLOR_URGENTE),
        "media": ("→ RECOMENDADA", COLOR_MEDIA),
        "positiva": ("✓ POSITIVO", COLOR_POSITIVA),
    }

    for acc in acciones:
        pri = acc.get("prioridad", "media")
        label, color = prioridad_map.get(pri, ("→", COLOR_MEDIA))
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(color)
        c.drawString(x + 0.2 * inch, y, label)
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        for i, line in enumerate(wrap_text(acc.get("texto", ""), 88)):
            c.drawString(x + 0.2 * inch if i == 0 else x + 0.5 * inch, y - 0.18 * inch if i > 0 else y - 0.16 * inch, line if i > 0 else f"    {line}")
            y -= 0.18 * inch
        y -= 0.10 * inch
        if y < 1.5 * inch:
            c.showPage(); y = height - 0.85 * inch

    # ── FOOTER ──────────────────────────────────────────
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(x, 0.55 * inch, "Generado automáticamente por CAI Cooperativas · Confidencial")

    c.save()
    buffer.seek(0)
    return buffer.read()
