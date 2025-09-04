# Multi-stage Dockerfile optimized for Render deployment
FROM node:18-bullseye as base

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    portaudio19-dev \
    espeak \
    espeak-data \
    libespeak-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Node.js dependencies
RUN npm ci --only=production && npm cache clean --force

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash sofia && \
    chown -R sofia:sofia /app

# Switch to non-root user
USER sofia

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Start command that runs both Node.js server and keeps Sofia agent ready
CMD ["node", "server.js"]