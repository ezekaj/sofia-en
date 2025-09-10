# Dockerfile for Sofia AI WebSocket Bridge Backend
# Uses Python 3.11 as base image (stable version compatible with LiveKit)
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed for audio processing and LiveKit
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first (Docker layer caching optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Create necessary directories for data persistence
RUN mkdir -p data logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port 8000 (WebSocket server port)
EXPOSE 8000

# Health check to ensure the service is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Command to run the WebSocket bridge server
CMD ["python", "scripts/utilities/sofia_websocket_bridge.py"]