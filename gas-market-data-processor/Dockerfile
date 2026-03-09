FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install project
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install as local package
COPY . .
RUN pip install -e .

# Expose port for healthcheck and gateway validation
EXPOSE 8010

# Healthcheck to verify the FastAPI wrapper is running and returning 200 OK
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://127.0.0.1:8010/health || exit 1

# Run the FastAPI server which holds our application healthcheck
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8010"]
