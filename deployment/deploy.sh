#!/bin/bash

# Sofia AI Quick Deployment Script
# This script helps deploy Sofia to Railway in minutes

set -e

echo "🚀 Sofia AI Quick Deployment Script"
echo "=================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "📝 Please log in to Railway:"
    railway login
fi

echo ""
echo "📦 Step 1: Deploy Sofia Agent"
echo "----------------------------"
cd ..
echo "Current directory: $(pwd)"

# Initialize Railway project for Sofia
echo "Creating Railway project for Sofia Agent..."
railway init --name "sofia-agent"

# Set environment variables
echo "Setting environment variables..."
railway variables set LIVEKIT_URL="$LIVEKIT_URL"
railway variables set LIVEKIT_API_KEY="$LIVEKIT_API_KEY"
railway variables set LIVEKIT_API_SECRET="$LIVEKIT_API_SECRET"
railway variables set GOOGLE_API_KEY="$GOOGLE_API_KEY"
railway variables set CALENDAR_URL="pending"
railway variables set LOG_LEVEL="INFO"
railway variables set PYTHON_ENV="production"

# Deploy Sofia
echo "Deploying Sofia Agent..."
railway up

# Get Sofia URL
SOFIA_URL=$(railway domain)
echo "✅ Sofia Agent deployed at: $SOFIA_URL"

echo ""
echo "📦 Step 2: Deploy Calendar Backend"
echo "---------------------------------"
cd dental-calendar

# Initialize Railway project for Calendar
echo "Creating Railway project for Calendar Backend..."
railway init --name "dental-calendar"

# Set environment variables
echo "Setting environment variables..."
railway variables set PORT="3005"
railway variables set NODE_ENV="production"
railway variables set JWT_SECRET=$(openssl rand -hex 32)
railway variables set DATABASE_URL="file:./data/dental.db"

# Deploy Calendar
echo "Deploying Calendar Backend..."
railway up --dockerfile Dockerfile.simple

# Get Calendar URL
CALENDAR_URL=$(railway domain)
echo "✅ Calendar Backend deployed at: $CALENDAR_URL"

# Update Sofia with Calendar URL
echo ""
echo "🔗 Updating Sofia with Calendar URL..."
cd ..
railway link sofia-agent
railway variables set CALENDAR_URL="https://$CALENDAR_URL"
railway redeploy

echo ""
echo "📦 Step 3: Deploy Token Server (Optional)"
echo "---------------------------------------"
cd deployment

# Initialize Railway project for Token Server
echo "Creating Railway project for Token Server..."
railway init --name "sofia-token-server"

# Set environment variables
echo "Setting environment variables..."
railway variables set LIVEKIT_API_KEY="$LIVEKIT_API_KEY"
railway variables set LIVEKIT_API_SECRET="$LIVEKIT_API_SECRET"
railway variables set PORT="3006"

# Deploy Token Server
echo "Deploying Token Server..."
railway up

# Get Token Server URL
TOKEN_URL=$(railway domain)
echo "✅ Token Server deployed at: $TOKEN_URL"

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "📋 Service URLs:"
echo "- Sofia Agent: https://$SOFIA_URL"
echo "- Calendar Backend: https://$CALENDAR_URL"
echo "- Token Server: https://$TOKEN_URL"
echo ""
echo "📝 Next Steps:"
echo "1. Update demo-frontend.html with your URLs:"
echo "   - LIVEKIT_URL: Your LiveKit Cloud URL"
echo "   - TOKEN_ENDPOINT: https://$TOKEN_URL/api/livekit-token"
echo ""
echo "2. Test the deployment:"
echo "   - Open demo-frontend.html in a browser"
echo "   - Click 'Mit Sofia sprechen'"
echo "   - Say 'Hallo' to start"
echo ""
echo "3. Monitor logs:"
echo "   railway logs --service sofia-agent"
echo "   railway logs --service dental-calendar"
echo ""
echo "🔧 Useful Commands:"
echo "- View logs: railway logs"
echo "- Restart service: railway restart"
echo "- Update env vars: railway variables set KEY=value"
echo "- Scale service: railway scale --min=1 --max=3"