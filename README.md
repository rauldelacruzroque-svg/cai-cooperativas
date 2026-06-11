# CAI Cooperativas – Análisis Ejecutivo con IA

App web para análisis financiero de cooperativas con Inteligencia Artificial.

---

## Estructura del proyecto

```
coop_app/
├── app.py                  ← Punto de entrada principal
├── requirements.txt        ← Dependencias
├── supabase_setup.sql      ← SQL para crear usuarios en Supabase
├── .gitignore
├── .streamlit/
│   └── secrets.toml        ← Claves privadas (NO subir a GitHub)
├── assets/
│   └── logo_cai.png        ← Logo de la app
└── modules/
    ├── auth.py             ← Login con Supabase
    ├── ia.py               ← Análisis con Claude IA
    ├── dashboard.py        ← Dashboard principal
    └── pdf_report.py       ← Generación de PDF
```

---

## Pasos para publicar

### 1. Crear cuenta en Supabase (gratis)
1. Ve a https://supabase.com y crea una cuenta
2. Crea un nuevo proyecto
3. Ve a **SQL Editor** y ejecuta el contenido de `supabase_setup.sql`
4. Copia tu **Project URL** y **anon public key** desde Project Settings > API

### 2. Crear API Key de Anthropic
1. Ve a https://console.anthropic.com
2. Crea una cuenta o inicia sesión
3. Ve a **API Keys** y genera una nueva clave
4. Guárdala, la necesitas en el siguiente paso

### 3. Subir a GitHub
1. Crea un repositorio nuevo en https://github.com (privado recomendado)
2. Sube todos los archivos EXCEPTO `.streamlit/secrets.toml`
3. El `.gitignore` ya está configurado para ignorarlo

### 4. Publicar en Streamlit Cloud (gratis)
1. Ve a https://share.streamlit.io
2. Conecta tu cuenta de GitHub
3. Selecciona tu repositorio y pon `app.py` como archivo principal
4. Ve a **Advanced settings > Secrets** y pega:

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-tu-clave-aqui"
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_KEY = "eyJ..."
```

5. Haz clic en **Deploy** — en 2 minutos tienes tu URL lista

---

## Agregar una cooperativa nueva

1. Ve a Supabase > Table Editor > `cooperativas_usuarios`
2. Agrega una fila nueva con:
   - `username`: el correo o usuario de la cooperativa
   - `password_hash`: el SHA-256 de la contraseña (ver abajo)
   - `nombre_cooperativa`: nombre completo
   - `activo`: TRUE

### Generar hash de contraseña (Python)
```python
import hashlib
print(hashlib.sha256("la_contraseña".encode()).hexdigest())
```

---

## Desactivar una cooperativa
En Supabase, cambia `activo = FALSE` en la fila correspondiente. 
Esa cooperativa ya no podrá entrar hasta que la reactives.
