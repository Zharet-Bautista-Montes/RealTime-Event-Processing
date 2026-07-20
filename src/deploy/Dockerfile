# ==============================================================================
# STAGE 1: Builder (Compilación y Descarga de Dependencias)
# ==============================================================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Evitamos que Python escriba archivos .pyc y forzamos la salida de log en vivo
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalamos herramientas mínimas necesarias para compilar ruedas C si es necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos e instalamos dependencias en la carpeta del usuario
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==============================================================================
# STAGE 2: Runner (Imagen Final Ligera para Producción)
# ==============================================================================
FROM python:3.10-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH" \
    PYTHONPATH="/app"

# Copiamos las dependencias instaladas desde el Builder
COPY --from=builder /root/.local /root/.local

# Copiamos todo el código fuente del proyecto
COPY . /app

# Creamos un usuario no-root por seguridad
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Exponemos por defecto los puertos de nuestros servicios
EXPOSE 8000 8001 8080

# El comando por defecto se sobreescribe en el docker-compose.yml para cada rol
CMD ["python"]