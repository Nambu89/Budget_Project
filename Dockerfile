FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema para ReportLab/Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python (cacheadas si requirements.txt no cambia)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo
COPY . .

# Railway inyecta $PORT automaticamente
EXPOSE 8000

CMD ["python", "main.py"]
