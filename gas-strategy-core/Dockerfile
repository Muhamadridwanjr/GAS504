FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirement first for layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings PyYAML "pandas>=2.0.0,<3.0.0" "numpy>=1.24.0" "redis[hiredis]>=5.0.0" openai httpx "apscheduler>=3.10.0" pytz requests && \
    pip install --no-cache-dir --no-deps ecocal tedata

# Copy everything else
COPY . .

# Install as package
RUN pip install -e .

# Expose port for FastAPI wrapper
EXPOSE 7003

# Run the API server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7003"]
