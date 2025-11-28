# Dockerfile dla Konwertera SF
# Optymalny dla Synology NAS (ARM/x86)

FROM python:3.11-slim

# Metadane
LABEL maintainer="Konwerter SF"
LABEL description="Konwerter Sprawozdań Finansowych XML → XLSX"

# Zmienne środowiskowe
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Katalog roboczy
WORKDIR $APP_HOME

# Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj requirements i zainstaluj zależności Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod źródłowy głównego modułu (src)
COPY ../src ./src

# Skopiuj kod aplikacji webowej
COPY app ./app

# Utwórz katalogi na dane
RUN mkdir -p /app/data/uploads /app/data/outputs

# Ustaw uprawnienia
RUN chmod -R 755 /app

# Port
EXPOSE 8000

# Użytkownik nie-root (bezpieczeństwo)
RUN useradd -m -u 1000 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Uruchomienie
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
