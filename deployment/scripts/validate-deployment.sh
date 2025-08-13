#!/bin/bash

# Sofia Voice Agent - Deployment Validation Script
# Validates the production Kubernetes deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="sofia-dental"
TIMEOUT=300

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

# Validation functions
validate_namespace() {
    print_status "Validating namespace..."
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        print_success "Namespace $NAMESPACE exists"
    else
        print_error "Namespace $NAMESPACE not found"
        return 1
    fi
}

validate_deployments() {
    print_status "Validating deployments..."
    
    local deployments=("sofia-agent" "livekit-server" "dental-calendar" "crm-dashboard" "sofia-web" "prometheus" "grafana")
    local failed=0
    
    for deployment in "${deployments[@]}"; do
        if kubectl get deployment $deployment -n $NAMESPACE &> /dev/null; then
            local ready=$(kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
            local desired=$(kubectl get deployment $deployment -n $NAMESPACE -o jsonpath='{.spec.replicas}')
            
            if [ "$ready" = "$desired" ] && [ "$ready" != "" ]; then
                print_success "$deployment: $ready/$desired replicas ready"
            else
                print_error "$deployment: $ready/$desired replicas ready"
                failed=1
            fi
        else
            print_error "Deployment $deployment not found"
            failed=1
        fi
    done
    
    return $failed
}

validate_services() {
    print_status "Validating services..."
    
    local services=("sofia-agent-service" "livekit-service" "dental-calendar-service" "crm-service" "sofia-web-service")
    local failed=0
    
    for service in "${services[@]}"; do
        if kubectl get service $service -n $NAMESPACE &> /dev/null; then
            local endpoints=$(kubectl get endpoints $service -n $NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}' | wc -w)
            if [ $endpoints -gt 0 ]; then
                print_success "$service: $endpoints endpoints available"
            else
                print_error "$service: No endpoints available"
                failed=1
            fi
        else
            print_error "Service $service not found"
            failed=1
        fi
    done
    
    return $failed
}

validate_ingress() {
    print_status "Validating ingress..."
    
    if kubectl get ingress sofia-dental-ingress -n $NAMESPACE &> /dev/null; then
        local address=$(kubectl get ingress sofia-dental-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [ -n "$address" ]; then
            print_success "Ingress has external address: $address"
        else
            print_warning "Ingress external address is pending"
        fi
    else
        print_error "Ingress sofia-dental-ingress not found"
        return 1
    fi
}

validate_loadbalancer() {
    print_status "Validating LoadBalancer..."
    
    if kubectl get service sofia-dental-loadbalancer -n $NAMESPACE &> /dev/null; then
        local external_ip=$(kubectl get service sofia-dental-loadbalancer -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [ -n "$external_ip" ] && [ "$external_ip" != "<pending>" ]; then
            print_success "LoadBalancer external IP: $external_ip"
        else
            print_warning "LoadBalancer external IP is pending"
        fi
    else
        print_error "LoadBalancer service not found"
        return 1
    fi
}

validate_health_endpoints() {
    print_status "Validating health endpoints..."
    
    local failed=0
    
    # Test internal health endpoints
    local health_checks=(
        "sofia-agent-service:8080/health"
        "dental-calendar-service:3005/health"
        "crm-service:5000/health"
        "sofia-web-service:5001/health"
        "livekit-service:7880/"
        "prometheus-service:9090/-/healthy"
        "grafana-service:3000/api/health"
    )
    
    for check in "${health_checks[@]}"; do
        local service=$(echo $check | cut -d: -f1)
        local endpoint=$(echo $check | cut -d: -f2-)
        
        print_status "Testing $service health endpoint..."
        
        # Use a temporary pod to test internal connectivity
        if kubectl run health-test-$RANDOM --image=curlimages/curl --rm -i --restart=Never -n $NAMESPACE -- \
           curl -f -s --max-time 10 "http://$service.$NAMESPACE.svc.cluster.local:$endpoint" &> /dev/null; then
            print_success "$service health check passed"
        else
            print_warning "$service health check failed or timed out"
            failed=1
        fi
    done
    
    return $failed
}

validate_persistent_volumes() {
    print_status "Validating persistent volumes..."
    
    local pvcs=("calendar-data-pvc" "logs-pvc" "prometheus-data-pvc" "grafana-data-pvc")
    local failed=0
    
    for pvc in "${pvcs[@]}"; do
        if kubectl get pvc $pvc -n $NAMESPACE &> /dev/null; then
            local status=$(kubectl get pvc $pvc -n $NAMESPACE -o jsonpath='{.status.phase}')
            if [ "$status" = "Bound" ]; then
                print_success "PVC $pvc is bound"
            else
                print_error "PVC $pvc status: $status"
                failed=1
            fi
        else
            print_error "PVC $pvc not found"
            failed=1
        fi
    done
    
    return $failed
}

validate_secrets() {
    print_status "Validating secrets..."
    
    local secrets=("sofia-secrets" "grafana-secrets")
    local failed=0
    
    for secret in "${secrets[@]}"; do
        if kubectl get secret $secret -n $NAMESPACE &> /dev/null; then
            print_success "Secret $secret exists"
        else
            print_error "Secret $secret not found"
            failed=1
        fi
    done
    
    return $failed
}

validate_autoscaling() {
    print_status "Validating horizontal pod autoscalers..."
    
    local hpas=("sofia-agent-hpa" "livekit-hpa")
    local failed=0
    
    for hpa in "${hpas[@]}"; do
        if kubectl get hpa $hpa -n $NAMESPACE &> /dev/null; then
            local current=$(kubectl get hpa $hpa -n $NAMESPACE -o jsonpath='{.status.currentReplicas}')
            local desired=$(kubectl get hpa $hpa -n $NAMESPACE -o jsonpath='{.status.desiredReplicas}')
            print_success "HPA $hpa: $current/$desired replicas"
        else
            print_warning "HPA $hpa not found"
        fi
    done
    
    return $failed
}

validate_monitoring() {
    print_status "Validating monitoring stack..."
    
    # Check if Prometheus is scraping targets
    local prometheus_targets=$(kubectl run prom-test-$RANDOM --image=curlimages/curl --rm -i --restart=Never -n $NAMESPACE -- \
        curl -s "http://prometheus-service.$NAMESPACE.svc.cluster.local:9090/api/v1/targets" | grep -o '"health":"up"' | wc -l || echo "0")
    
    if [ "$prometheus_targets" -gt 0 ]; then
        print_success "Prometheus is scraping $prometheus_targets healthy targets"
    else
        print_warning "Prometheus has no healthy targets or is not accessible"
    fi
    
    # Check Grafana datasource
    print_status "Grafana datasource should be configured manually"
}

run_performance_test() {
    print_status "Running basic performance test..."
    
    # Create a simple load test pod
    kubectl run perf-test-$RANDOM --image=curlimages/curl --rm -i --restart=Never -n $NAMESPACE -- \
        sh -c "for i in \$(seq 1 10); do curl -s -w '%{time_total}\n' -o /dev/null http://sofia-web-service.$NAMESPACE.svc.cluster.local:5001/health; done" | \
        awk '{sum+=$1; count++} END {printf "Average response time: %.3f seconds\n", sum/count}' || \
        print_warning "Performance test failed"
}

generate_report() {
    print_status "Generating deployment report..."
    
    echo "=== Sofia Voice Agent Deployment Report ===" > deployment-report.txt
    echo "Generated: $(date)" >> deployment-report.txt
    echo "" >> deployment-report.txt
    
    echo "=== Cluster Information ===" >> deployment-report.txt
    kubectl cluster-info >> deployment-report.txt 2>&1
    echo "" >> deployment-report.txt
    
    echo "=== Namespace Resources ===" >> deployment-report.txt
    kubectl get all -n $NAMESPACE >> deployment-report.txt 2>&1
    echo "" >> deployment-report.txt
    
    echo "=== Resource Usage ===" >> deployment-report.txt
    kubectl top pods -n $NAMESPACE >> deployment-report.txt 2>&1
    echo "" >> deployment-report.txt
    
    echo "=== Events ===" >> deployment-report.txt
    kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -20 >> deployment-report.txt 2>&1
    
    print_success "Deployment report saved to deployment-report.txt"
}

# Main validation function
main() {
    echo -e "${BLUE}"
    echo "====================================================="
    echo "    Sofia Voice Agent - Deployment Validation"
    echo "====================================================="
    echo -e "${NC}"
    
    local total_failures=0
    
    # Run all validations
    validate_namespace || ((total_failures++))
    validate_deployments || ((total_failures++))
    validate_services || ((total_failures++))
    validate_ingress || ((total_failures++))
    validate_loadbalancer || ((total_failures++))
    validate_persistent_volumes || ((total_failures++))
    validate_secrets || ((total_failures++))
    validate_autoscaling || ((total_failures++))
    validate_monitoring || ((total_failures++))
    
    # Optional tests
    if [ "$1" = "--full" ]; then
        print_status "Running full validation including health checks..."
        validate_health_endpoints || ((total_failures++))
        run_performance_test
    fi
    
    # Generate report
    if [ "$1" = "--report" ] || [ "$2" = "--report" ]; then
        generate_report
    fi
    
    echo ""
    echo "=== Validation Summary ==="
    if [ $total_failures -eq 0 ]; then
        print_success "All validations passed! Sofia Voice Agent is ready for production."
        
        # Display access information
        local external_ip=$(kubectl get service sofia-dental-loadbalancer -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
        
        if [ "$external_ip" != "pending" ] && [ -n "$external_ip" ]; then
            echo ""
            print_success "Access URLs:"
            echo -e "  Main App: http://$external_ip"
            echo -e "  Voice:    ws://$external_ip:7880"
            echo -e "  API:      http://$external_ip/api"
        fi
        
        echo ""
        print_success "Next steps:"
        echo -e "  1. Configure DNS records for your domain"
        echo -e "  2. Test voice functionality from browsers"
        echo -e "  3. Set up monitoring alerts"
        echo -e "  4. Configure backup procedures"
        
        exit 0
    else
        print_error "$total_failures validation(s) failed. Please review the issues above."
        
        echo ""
        print_status "Troubleshooting commands:"
        echo -e "  kubectl get all -n $NAMESPACE"
        echo -e "  kubectl describe pods -n $NAMESPACE"
        echo -e "  kubectl logs -l app=sofia-agent -n $NAMESPACE"
        
        exit 1
    fi
}

# Show help
if [ "$1" = "--help" ]; then
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --full     Run full validation including health checks"
    echo "  --report   Generate detailed deployment report"
    echo "  --help     Show this help message"
    exit 0
fi

# Run main validation
main "$@"
