FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl for healthcheck, libpq for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8400

# Start up command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8400"]
