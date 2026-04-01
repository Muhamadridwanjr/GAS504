FROM python:3.11-slim
WORKDIR /app

# Install Firefox ESR + geckodriver for tedata (Selenium-based Trading Economics scraper)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl wget bzip2 ca-certificates \
        firefox-esr \
        libgtk-3-0 libdbus-glib-1-2 libxt6 libx11-xcb1 \
    && GECKO_VER="0.36.0" \
    && wget -q "https://github.com/mozilla/geckodriver/releases/download/v${GECKO_VER}/geckodriver-v${GECKO_VER}-linux64.tar.gz" -O geckodriver.tar.gz \
    && tar -xzf geckodriver.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && rm geckodriver.tar.gz \
    && rm -rf /var/lib/apt/lists/*

# Set display for headless Firefox
ENV DISPLAY=:99
ENV MOZ_HEADLESS=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && mkdir -p /usr/local/lib/python3.11/site-packages/tedata/logs \
    && chmod -R 777 /usr/local/lib/python3.11/site-packages/tedata/

ENV TEDATA_DISABLE_LOGGING=true

COPY . .
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 9603
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:9603/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "9603", "--workers", "1"]
