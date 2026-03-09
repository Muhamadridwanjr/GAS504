# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set environment variables
ENV MODE=socket
ENV SOCKET_PORT=8110
ENV REDIS_URL=redis://redis:6379/0
ENV PYTHONPATH=/app

# Expose the websocket port
EXPOSE 8110

# Healthcheck to verify the container is healthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8110/health || exit 1 

# Run the application
CMD ["python", "src/main.py"]
