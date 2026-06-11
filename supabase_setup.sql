-- ============================================================
-- Ejecuta este SQL en Supabase > SQL Editor
-- ============================================================

CREATE TABLE IF NOT EXISTS cooperativas_usuarios (
    id              SERIAL PRIMARY KEY,
    username        TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    nombre_cooperativa TEXT NOT NULL,
    activo          BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Ejemplo: insertar una cooperativa de prueba
-- Contraseña: "coop2024" (SHA-256 hash)
INSERT INTO cooperativas_usuarios (username, password_hash, nombre_cooperativa, activo)
VALUES (
    'coopanela',
    '7c44bf9d4e39e97b36bc7e11c1a59cd07c46a67c5a56c14c96a45c46cb86c95d',
    'COOPANELA',
    TRUE
);

-- Para generar el hash de una contraseña nueva en Python:
-- import hashlib
-- print(hashlib.sha256("tu_contraseña".encode()).hexdigest())
