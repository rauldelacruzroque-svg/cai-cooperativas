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


def build_pdf(coop_nombre: str, kpis: dict, resumen, acciones: list) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer,
