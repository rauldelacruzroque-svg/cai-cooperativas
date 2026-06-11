"""
Módulo de análisis con IA — CAI Cooperativas
Envía PDFs a Claude y obtiene análisis ejecutivo estructurado.
"""

import anthropic
import base64
import json
import streamlit as st


SYSTEM_PROMPT = """Eres un analista financiero experto en cooperativas de ahorro y crédito 
de República Dominicana y América Latina. Tu tarea es analizar los documentos financieros 
que se te proporcionen y generar un análisis ejecutivo completo.

Debes responder ÚNICAMENTE con un objeto JSON válido, sin texto adicional, sin bloques de código, 
sin comillas triples. El JSON debe tener exactamente esta estructura:

{
  "kpis": {
    "capital_total": "valor como string con moneda",
    "total_prestado": "valor como string con moneda",
    "total_cobrado": "valor como string con moneda",
    "porcentaje_recuperacion": "valor como string con %",
    "mora_estimada": "valor como string con moneda o %",
    "total_socios": "número como string"
  },
  "graficas": {
    "prestamos_por_mes": [{"mes": "Ene", "monto": 0}],
    "recuperacion_por_mes": [{"mes": "Ene", "porcentaje": 0}],
    "distribucion_cartera": [{"categoria": "nombre", "monto": 0}],
    "flujo_neto": [{"mes": "Ene", "neto": 0}],
    "estado_mora": [{"estado": "Al día", "monto": 0}, {"estado": "En mora", "monto": 0}]
  },
  "resumen": "Párrafo ejecutivo de 4-6 oraciones con análisis de la situación financiera actual, tendencias y riesgos principales.",
  "acciones": [
    {"prioridad": "urgente", "texto": "descripción de la acción"},
    {"prioridad": "media", "texto": "descripción de la acción"},
    {"prioridad": "media", "texto": "descripción de la acción"},
    {"prioridad": "positiva", "texto": "descripción de la acción"},
    {"prioridad": "positiva", "texto": "descripción de la acción"}
  ]
}

Si algún dato no está disponible en los documentos, usa "N/D" para strings o 0 para números.
Siempre devuelve exactamente 5 acciones. Los meses en graficas deben ser abreviaciones de 3 letras.
"""


def pdf_to_base64(file_bytes: bytes) -> str:
    return base64.standard_b64encode(file_bytes).decode("utf-8")


def analizar_pdfs(archivos: list) -> dict:
    """
    Recibe lista de archivos subidos por Streamlit.
    Devuelve dict con el análisis estructurado.
    """
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    client = anthropic.Anthropic(api_key=api_key)

    # Construir contenido del mensaje con todos los PDFs
    content = []

    for archivo in archivos:
        file_bytes = archivo.read()
        b64 = pdf_to_base64(file_bytes)
        content.append({
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": b64,
            },
            "title": archivo.name,
        })

    content.append({
        "type": "text",
        "text": "Analiza todos los documentos financieros adjuntos y genera el análisis ejecutivo completo en el formato JSON especificado."
    })

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}]
    )

    raw = response.content[0].text.strip()

    # Limpiar posibles bloques de código
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)
