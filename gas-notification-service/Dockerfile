FROM python:3.11-slim

# Install dependencies and curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set default env
ENV ENVIRONMENT=production PORT=8112

EXPOSE 8112

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Standard startup (will be overridden via compose for workers)
CMD ["python", "-m", "src.main"]
