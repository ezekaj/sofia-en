#!/bin/bash

# Sofia Dental Voice Agent - Kubernetes Deployment Script

set -e

echo "🚀 Deploying Sofia Dental Voice Agent to Kubernetes..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if docker is available
if ! command -v docker &> /dev/null; then
    print_error "docker is not installed or not in PATH"
    exit 1
fi

print_status "Building Docker images..."

# Build Sofia Agent image
print_status "Building Sofia Agent image..."
docker build -t sofia-agent:latest -f Dockerfile.sofia .

# Build Dental Calendar image
print_status "Building Dental Calendar image..."
docker build -t dental-calendar:latest -f dental-calendar/Dockerfile ./dental-calendar

# Build CRM image (if Dockerfile exists)
if [ -f "crm/Dockerfile" ]; then
    print_status "Building CRM image..."
    docker build -t crm-dashboard:latest -f crm/Dockerfile ./crm
fi

print_success "Docker images built successfully!"

# Deploy to Kubernetes
print_status "Deploying to Kubernetes..."

# Create namespace
print_status "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Apply ConfigMaps and Secrets
print_status "Applying configuration..."
kubectl apply -f k8s/configmap.yaml

# Deploy LiveKit Server
print_status "Deploying LiveKit Server..."
kubectl apply -f k8s/livekit-deployment.yaml

# Wait for LiveKit to be ready
print_status "Waiting for LiveKit to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/livekit-server -n sofia-dental

# Deploy Dental Calendar
print_status "Deploying Dental Calendar..."
kubectl apply -f k8s/dental-calendar-deployment.yaml

# Deploy Sofia Agent
print_status "Deploying Sofia Agent..."
kubectl apply -f k8s/sofia-agent-deployment.yaml

# Deploy Ingress
print_status "Deploying Ingress..."
kubectl apply -f k8s/ingress.yaml

# Wait for deployments
print_status "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/dental-calendar -n sofia-dental
kubectl wait --for=condition=available --timeout=300s deployment/sofia-agent -n sofia-dental

print_success "Deployment completed!"

# Show status
print_status "Deployment Status:"
kubectl get pods -n sofia-dental
kubectl get services -n sofia-dental

# Get external IP
print_status "Getting external access information..."
EXTERNAL_IP=$(kubectl get service sofia-dental-loadbalancer -n sofia-dental -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

if [ "$EXTERNAL_IP" = "pending" ] || [ -z "$EXTERNAL_IP" ]; then
    print_warning "External IP is still pending. Use port-forward for local access:"
    echo "kubectl port-forward service/dental-calendar-service 3005:3005 -n sofia-dental"
    echo "kubectl port-forward service/livekit-service 7880:7880 -n sofia-dental"
else
    print_success "Sofia Dental is accessible at: http://$EXTERNAL_IP"
fi

print_success "🎉 Sofia Dental Voice Agent deployment completed!"
print_status "Voice features are now integrated into the calendar system."
print_status "Access the calendar at: http://localhost:3005 (via port-forward)"
print_status "LiveKit voice server: ws://localhost:7880 (via port-forward)"

echo ""
echo "📋 Next Steps:"
echo "1. Configure your Google AI API key in the secret"
echo "2. Set up external LoadBalancer or Ingress"
echo "3. Test voice functionality through the calendar interface"
echo "4. Monitor logs: kubectl logs -f deployment/sofia-agent -n sofia-dental"
