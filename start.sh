#!/bin/bash

# Sofia AI ULTRATHINK Start Script
echo "🚀 ULTRATHINK Sofia AI Starting..."
echo "📊 Node Version: $(node --version)"
echo "📊 NPM Version: $(npm --version)"
echo "📊 Directory: $(pwd)"
echo "📊 Files: $(ls -la)"

# Ensure dependencies are installed
echo "📦 Installing dependencies..."
npm install

# Verify ultrathink-server.js exists
if [ ! -f "ultrathink-server.js" ]; then
    echo "❌ ERROR: ultrathink-server.js not found!"
    exit 1
fi

echo "✅ ultrathink-server.js found"

# Start the server
echo "🎯 Starting Sofia AI ULTRATHINK Server..."
node ultrathink-server.js