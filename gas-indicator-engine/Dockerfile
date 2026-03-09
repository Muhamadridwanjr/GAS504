FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib-0.4.0-src.tar.gz ta-lib/

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
ENV CFLAGS="-Wno-error=incompatible-pointer-types -Wno-incompatible-pointer-types"
RUN pip install --no-cache-dir numpy==1.26.4
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

# Copy source code
COPY . .

# Generate gRPC classes (if there is a grpc file)
# If proto generation is needed at build time, do it here

# Expose ports (8203 for REST, 8204 for gRPC)
EXPOSE 8203 8204

COPY ./scripts/start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
