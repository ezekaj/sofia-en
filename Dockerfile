# Production Dockerfile for Sofia AI Unified Server
FROM node:18-slim

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy package files and install Node.js dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p dental-calendar/public data logs

# Set environment variables
ENV NODE_ENV=production
ENV PORT=10000
ENV PYTHONPATH=/app
ENV PYTHON_UNBUFFERED=1

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:10000/health || exit 1

# Start the unified server
CMD ["node", "production-server.js"]