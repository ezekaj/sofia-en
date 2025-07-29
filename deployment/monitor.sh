#!/bin/bash

# Sofia AI Monitoring Script
# Quick health checks and monitoring for all services

echo "🔍 Sofia AI Service Monitor"
echo "=========================="
echo ""

# Function to check service health
check_health() {
    local service_name=$1
    local health_url=$2
    
    echo -n "Checking $service_name... "
    
    if curl -s -f -o /dev/null "$health_url"; then
        echo "✅ Healthy"
        return 0
    else
        echo "❌ Unhealthy or unreachable"
        return 1
    fi
}

# Get service URLs from environment or use defaults
SOFIA_URL=${SOFIA_URL:-"https://sofia-agent.railway.app"}
CALENDAR_URL=${CALENDAR_URL:-"https://dental-calendar.railway.app"}
TOKEN_URL=${TOKEN_URL:-"https://sofia-token-server.railway.app"}

echo "📊 Service Health Checks"
echo "----------------------"
check_health "Sofia Agent" "$SOFIA_URL/health"
check_health "Calendar Backend" "$CALENDAR_URL/health"
check_health "Token Server" "$TOKEN_URL/health"

echo ""
echo "📈 LiveKit Status"
echo "----------------"
# You can add LiveKit API calls here to check room status

echo ""
echo "🔧 Quick Actions"
echo "---------------"
echo "1. View Sofia logs:      railway logs --service sofia-agent"
echo "2. View Calendar logs:   railway logs --service dental-calendar"
echo "3. Restart Sofia:        railway restart --service sofia-agent"
echo "4. Scale Sofia:          railway scale --service sofia-agent --min=2"
echo "5. Update environment:   railway variables --service sofia-agent"

echo ""
echo "📱 Test the System"
echo "-----------------"
echo "Open deployment/demo-frontend.html in your browser to test Sofia"