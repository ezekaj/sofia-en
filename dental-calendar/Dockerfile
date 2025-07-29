# Dental Calendar with Voice Integration Dockerfile
FROM node:18-alpine

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    build-base \
    python3-dev

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies and rebuild native modules
RUN npm ci --only=production && \
    npm rebuild sqlite3 --build-from-source && \
    npm cache clean --force

# Copy application code
COPY . .

# Install Python dependencies for Sofia integration
RUN pip3 install --no-cache-dir --break-system-packages httpx python-dotenv

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 && \
    chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3005/health || exit 1

# Start the calendar server
CMD ["node", "server.js"]
