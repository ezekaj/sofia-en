#!/bin/bash

# Sofia Voice Agent - Production Kubernetes Deployment Script
# This script deploys the complete Sofia voice agent system to Kubernetes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="sofia-dental"
DOMAIN="sofia-dental.com"  # Change this to your domain
REGISTRY="your-registry.com"  # Change this to your container registry
TIMEOUT=600  # 10 minutes timeout for deployments

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if helm is installed (optional)
    if ! command -v helm &> /dev/null; then
        print_warning "helm is not installed. Some features may not be available."
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    # Check if NGINX ingress controller is installed
    if ! kubectl get ingressclass nginx &> /dev/null; then
        print_warning "NGINX ingress controller is not installed. Installing now..."
        install_nginx_ingress
    fi
    
    print_success "Prerequisites check completed"
}

# Function to install NGINX Ingress Controller
install_nginx_ingress() {
    print_status "Installing NGINX Ingress Controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
    
    print_status "Waiting for NGINX Ingress Controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    
    print_success "NGINX Ingress Controller installed"
}

# Function to install cert-manager for SSL certificates
install_cert_manager() {
    print_status "Installing cert-manager for SSL certificates..."
    
    # Add cert-manager Helm repository
    if command -v helm &> /dev/null; then
        helm repo add jetstack https://charts.jetstack.io
        helm repo update
        
        # Install cert-manager
        helm install cert-manager jetstack/cert-manager \
            --namespace cert-manager \
            --create-namespace \
            --version v1.13.0 \
            --set installCRDs=true
    else
        # Install via kubectl
        kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
    fi
    
    print_status "Waiting for cert-manager to be ready..."
    kubectl wait --namespace cert-manager \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/instance=cert-manager \
        --timeout=300s
    
    print_success "cert-manager installed"
}

# Function to build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."
    
    # Sofia Agent
    print_status "Building Sofia Agent image..."
    docker build -t ${REGISTRY}/sofia-agent:latest -f Dockerfile.sofia .
    docker push ${REGISTRY}/sofia-agent:latest
    
    # Dental Calendar
    print_status "Building Dental Calendar image..."
    docker build -t ${REGISTRY}/dental-calendar:latest -f dental-calendar/Dockerfile ./dental-calendar
    docker push ${REGISTRY}/dental-calendar:latest
    
    # CRM Dashboard
    print_status "Building CRM Dashboard image..."
    docker build -t ${REGISTRY}/crm-dashboard:latest -f crm/Dockerfile ./crm
    docker push ${REGISTRY}/crm-dashboard:latest
    
    # Sofia Web
    print_status "Building Sofia Web image..."
    docker build -t ${REGISTRY}/sofia-web:latest -f Dockerfile.web .
    docker push ${REGISTRY}/sofia-web:latest
    
    print_success "All images built and pushed"
}

# Function to update image registries in manifests
update_image_registry() {
    print_status "Updating image registry in manifests..."
    
    # Update all deployment files with correct image registry
    sed -i.bak "s|sofia-agent:latest|${REGISTRY}/sofia-agent:latest|g" k8s/*.yaml
    sed -i.bak "s|dental-calendar:latest|${REGISTRY}/dental-calendar:latest|g" k8s/*.yaml
    sed -i.bak "s|crm-dashboard:latest|${REGISTRY}/crm-dashboard:latest|g" k8s/*.yaml
    sed -i.bak "s|sofia-web:latest|${REGISTRY}/sofia-web:latest|g" k8s/*.yaml
    
    # Update domain names
    sed -i.bak "s|sofia-dental.com|${DOMAIN}|g" k8s/*.yaml
    sed -i.bak "s|api.sofia-dental.com|api.${DOMAIN}|g" k8s/*.yaml
    sed -i.bak "s|voice.sofia-dental.com|voice.${DOMAIN}|g" k8s/*.yaml
    sed -i.bak "s|monitoring.sofia-dental.com|monitoring.${DOMAIN}|g" k8s/*.yaml
    
    print_success "Image registry and domains updated"
}

# Function to create secrets
create_secrets() {
    print_status "Creating Kubernetes secrets..."
    
    # Check if secrets already exist
    if kubectl get secret sofia-secrets -n ${NAMESPACE} &> /dev/null; then
        print_warning "Sofia secrets already exist. Skipping creation."
        print_warning "To update secrets, delete them first: kubectl delete secret sofia-secrets -n ${NAMESPACE}"
        return
    fi
    
    # Prompt for sensitive values
    echo -n "Enter Google API Key: "
    read -s GOOGLE_API_KEY
    echo
    
    echo -n "Enter LiveKit API Secret (or press Enter for default): "
    read -s LIVEKIT_SECRET
    echo
    if [ -z "$LIVEKIT_SECRET" ]; then
        LIVEKIT_SECRET="secret"
    fi
    
    # Create secret
    kubectl create secret generic sofia-secrets \
        --from-literal=GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
        --from-literal=LIVEKIT_API_SECRET="${LIVEKIT_SECRET}" \
        --from-literal=DATABASE_PASSWORD="$(openssl rand -base64 32)" \
        --from-literal=JWT_SECRET="$(openssl rand -base64 32)" \
        --from-literal=ENCRYPTION_KEY="$(openssl rand -base64 32)" \
        -n ${NAMESPACE}
    
    print_success "Secrets created"
}

# Function to deploy manifests in order
deploy_manifests() {
    print_status "Deploying Kubernetes manifests..."
    
    # Deploy in correct order to handle dependencies
    local manifest_order=(
        "01-namespace.yaml"
        "02-configmaps-secrets.yaml"
        "03-storage.yaml"
        "04-livekit-deployment.yaml"
        "05-sofia-agent-deployment.yaml"
        "06-dental-calendar-deployment.yaml"
        "07-monitoring.yaml"
        "08-ingress-loadbalancer.yaml"
        "09-deployment-scripts.yaml"
    )
    
    for manifest in "${manifest_order[@]}"; do
        if [ -f "k8s/${manifest}" ]; then
            print_status "Applying ${manifest}..."
            kubectl apply -f "k8s/${manifest}"
        else
            print_warning "Manifest ${manifest} not found, skipping..."
        fi
    done
    
    print_success "All manifests applied"
}

# Function to wait for deployments
wait_for_deployments() {
    print_status "Waiting for deployments to be ready..."
    
    local deployments=(
        "livekit-server"
        "dental-calendar"
        "crm-dashboard"
        "sofia-web"
        "sofia-agent"
        "prometheus"
        "grafana"
    )
    
    for deployment in "${deployments[@]}"; do
        print_status "Waiting for ${deployment} to be ready..."
        if kubectl wait --for=condition=available --timeout=${TIMEOUT}s deployment/${deployment} -n ${NAMESPACE}; then
            print_success "${deployment} is ready"
        else
            print_error "${deployment} failed to become ready within ${TIMEOUT} seconds"
            kubectl describe deployment/${deployment} -n ${NAMESPACE}
            kubectl logs -l app=${deployment} -n ${NAMESPACE} --tail=50
        fi
    done
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Get service endpoints
    print_status "Service endpoints:"
    kubectl get svc -n ${NAMESPACE} -o wide
    
    # Check ingress
    print_status "Ingress status:"
    kubectl get ingress -n ${NAMESPACE}
    
    # Check LoadBalancer external IPs
    print_status "LoadBalancer external IPs:"
    kubectl get svc -n ${NAMESPACE} --field-selector spec.type=LoadBalancer -o wide
    
    # Run deployment validation job
    print_status "Running deployment validation..."
    kubectl delete job sofia-deployment-init -n ${NAMESPACE} --ignore-not-found=true
    kubectl apply -f k8s/09-deployment-scripts.yaml
    
    # Wait for validation job
    if kubectl wait --for=condition=complete --timeout=300s job/sofia-deployment-init -n ${NAMESPACE}; then
        print_success "Deployment validation passed"
        kubectl logs job/sofia-deployment-init -n ${NAMESPACE}
    else
        print_error "Deployment validation failed"
        kubectl logs job/sofia-deployment-init -n ${NAMESPACE}
    fi
}

# Function to display access information
display_access_info() {
    print_success "\n=== Sofia Voice Agent Deployment Complete ==="
    
    # Get LoadBalancer IP
    EXTERNAL_IP=$(kubectl get svc sofia-dental-loadbalancer -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    
    if [ "$EXTERNAL_IP" = "pending" ] || [ -z "$EXTERNAL_IP" ]; then
        EXTERNAL_IP=$(kubectl get svc sofia-dental-loadbalancer -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "pending")
    fi
    
    echo -e "\n${GREEN}Access URLs:${NC}"
    if [ "$EXTERNAL_IP" != "pending" ] && [ -n "$EXTERNAL_IP" ]; then
        echo -e "  Main Application: https://${DOMAIN} (${EXTERNAL_IP})"
        echo -e "  API Endpoints:    https://api.${DOMAIN}"
        echo -e "  Voice Interface:  wss://voice.${DOMAIN}"
        echo -e "  Monitoring:       https://monitoring.${DOMAIN}"
    else
        echo -e "  ${YELLOW}LoadBalancer IP is still pending. Check with: kubectl get svc -n ${NAMESPACE}${NC}"
    fi
    
    echo -e "\n${GREEN}Monitoring:${NC}"
    echo -e "  Grafana:     Port-forward with: kubectl port-forward svc/grafana-service 3000:3000 -n ${NAMESPACE}"
    echo -e "  Prometheus:  Port-forward with: kubectl port-forward svc/prometheus-service 9090:9090 -n ${NAMESPACE}"
    
    echo -e "\n${GREEN}Credentials:${NC}"
    echo -e "  Grafana Admin: admin / admin123 (change after first login)"
    echo -e "  Monitoring:    admin / monitoring123"
    
    echo -e "\n${GREEN}Useful Commands:${NC}"
    echo -e "  Check status:  kubectl get all -n ${NAMESPACE}"
    echo -e "  View logs:     kubectl logs -f deployment/sofia-agent -n ${NAMESPACE}"
    echo -e "  Scale:         kubectl scale deployment sofia-agent --replicas=5 -n ${NAMESPACE}"
    echo -e "  Update:        kubectl rollout restart deployment/sofia-agent -n ${NAMESPACE}"
    
    echo -e "\n${BLUE}DNS Configuration:${NC}"
    echo -e "  Add these DNS records pointing to ${EXTERNAL_IP}:"
    echo -e "    ${DOMAIN}"
    echo -e "    api.${DOMAIN}"
    echo -e "    voice.${DOMAIN}"
    echo -e "    monitoring.${DOMAIN}"
}

# Function to cleanup on failure
cleanup_on_failure() {
    print_error "Deployment failed. Cleaning up..."
    kubectl delete namespace ${NAMESPACE} --ignore-not-found=true
    print_status "Cleanup completed"
}

# Main deployment function
main() {
    echo -e "${BLUE}"
    echo "====================================================="
    echo "       Sofia Voice Agent - K8s Deployment"
    echo "====================================================="
    echo -e "${NC}"
    
    # Parse command line arguments
    SKIP_BUILD=false
    SKIP_IMAGES=false
    DRY_RUN=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-images)
                SKIP_IMAGES=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --domain=*)
                DOMAIN="${1#*=}"
                shift
                ;;
            --registry=*)
                REGISTRY="${1#*=}"
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --skip-build           Skip Docker image building"
                echo "  --skip-images          Skip image registry updates"
                echo "  --dry-run              Show what would be done without executing"
                echo "  --domain=DOMAIN        Set the domain name (default: sofia-dental.com)"
                echo "  --registry=REGISTRY    Set the container registry (default: your-registry.com)"
                echo "  --help                 Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    if [ "$DRY_RUN" = true ]; then
        print_status "DRY RUN MODE - No changes will be made"
        return 0
    fi
    
    # Set trap for cleanup on failure
    trap cleanup_on_failure ERR
    
    print_status "Starting deployment to namespace: ${NAMESPACE}"
    print_status "Domain: ${DOMAIN}"
    print_status "Registry: ${REGISTRY}"
    
    # Run deployment steps
    check_prerequisites
    
    if [ "$SKIP_BUILD" != true ]; then
        build_and_push_images
    fi
    
    if [ "$SKIP_IMAGES" != true ]; then
        update_image_registry
    fi
    
    install_cert_manager
    deploy_manifests
    create_secrets
    wait_for_deployments
    run_health_checks
    display_access_info
    
    print_success "\nDeployment completed successfully!"
    print_success "Sofia Voice Agent is now running in production mode."
}

# Run main function with all arguments
main "$@"
