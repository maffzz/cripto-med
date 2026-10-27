# Dockerfile para CriptoMed Backend (single-stage para simplicidad)
FROM python:3.12.7-slim

# Instalar dependencias de sistema para psycopg
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements.txt
COPY backend/requirements.txt .

# Instalar dependencias Python sin cache (globalmente para root y app)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de aplicación
COPY backend/app ./app
COPY backend/scripts ./scripts

# Crear usuario no root
RUN groupadd -g 10001 app && \
    useradd -r -u 10001 -g app app

# Cambiar propietario de archivos
RUN chown -R app:app /app

# Cambiar a usuario no root
USER app

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Comando de ejecución
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
