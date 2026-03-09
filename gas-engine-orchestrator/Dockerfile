FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies (curl required for healthcheck)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8105

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8105", "--proxy-headers"]
