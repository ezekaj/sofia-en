# Sofia Voice Agent - Production Kubernetes Deployment

This directory contains production-ready Kubernetes manifests for deploying the Sofia Voice Agent system with high availability, comprehensive monitoring, and reliable browser connectivity.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer / Ingress                  │
│              (sofia-dental.com, voice.sofia-dental.com)     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┼───────────────────────────────────────┐
│                     │           Sofia Namespace             │
│  ┌──────────────────▼─────────────────┐                     │
│  │            Sofia Web               │                     │
│  │         (React Frontend)           │                     │
│  │            2 replicas              │                     │
│  └────────────┬───────────────────────┘                     │
│               │                                             │
│  ┌────────────▼───────────┐  ┌─────────────────────────────┐ │
│  │      Sofia Agent       │  │       LiveKit Server        │ │
│  │   (Voice Processing)   │  │    (WebRTC/Voice Comm)     │ │
│  │       3 replicas       │  │        2 replicas           │ │
│  └────────────┬───────────┘  └─────────────────────────────┘ │
│               │                                             │
│  ┌────────────▼───────────┐  ┌─────────────────────────────┐ │
│  │    Dental Calendar     │  │       CRM Dashboard         │ │
│  │   (Node.js Backend)    │  │     (Flask Frontend)        │ │
│  │       2 replicas       │  │        2 replicas           │ │
│  └────────────────────────┘  └─────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Monitoring Stack                        │ │
│  │  Prometheus + Grafana + AlertManager                   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Components

### Core Services
- **Sofia Agent** (3 replicas): Main voice processing and AI agent
- **LiveKit Server** (2 replicas): WebRTC voice communication server
- **Dental Calendar** (2 replicas): Appointment management backend
- **CRM Dashboard** (2 replicas): Customer relationship management interface
- **Sofia Web** (2 replicas): Main web interface for browser clients

### Monitoring & Observability
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization dashboards
- **AlertManager**: Alert routing and notification
- **Custom Dashboards**: Sofia-specific performance metrics

### Infrastructure
- **NGINX Ingress**: Load balancing and SSL termination
- **cert-manager**: Automatic SSL certificate management
- **Persistent Storage**: Database and log persistence
- **Auto-scaling**: HPA for dynamic scaling based on load

## 🚀 Quick Start

### Prerequisites

1. **Kubernetes Cluster** (v1.24+)
   - GKE, EKS, AKS, or self-managed cluster
   - At least 8 vCPUs and 16GB RAM available

2. **Required Tools**
   ```bash
   kubectl version --client  # v1.24+
   helm version             # v3.0+ (optional)
   docker --version         # Latest
   ```

3. **Container Registry Access**
   - Docker Hub, GCR, ECR, or private registry
   - Push permissions for your images

### One-Command Deployment

```bash
# Make deployment script executable
chmod +x k8s/deploy.sh

# Deploy with your domain and registry
./k8s/deploy.sh --domain=your-domain.com --registry=your-registry.com
```

### Manual Deployment

1. **Apply Manifests in Order**
   ```bash
   kubectl apply -f k8s/01-namespace.yaml
   kubectl apply -f k8s/02-configmaps-secrets.yaml
   kubectl apply -f k8s/03-storage.yaml
   kubectl apply -f k8s/04-livekit-deployment.yaml
   kubectl apply -f k8s/05-sofia-agent-deployment.yaml
   kubectl apply -f k8s/06-dental-calendar-deployment.yaml
   kubectl apply -f k8s/07-monitoring.yaml
   kubectl apply -f k8s/08-ingress-loadbalancer.yaml
   kubectl apply -f k8s/09-deployment-scripts.yaml
   ```

2. **Create Secrets**
   ```bash
   kubectl create secret generic sofia-secrets \
     --from-literal=GOOGLE_API_KEY="your-google-api-key" \
     --from-literal=LIVEKIT_API_SECRET="your-livekit-secret" \
     -n sofia-dental
   ```

3. **Wait for Deployment**
   ```bash
   kubectl wait --for=condition=available --timeout=600s \
     deployment --all -n sofia-dental
   ```

## 🔧 Configuration

### Environment Variables

Key configuration options in `02-configmaps-secrets.yaml`:

```yaml
# Core Configuration
LIVEKIT_URL: "wss://voice.your-domain.com"
CALENDAR_URL: "https://api.your-domain.com/calendar"
SOFIA_VOICE_ENABLED: "true"
LOG_LEVEL: "INFO"

# Performance Tuning
MAX_CONCURRENT_SESSIONS: "50"
SESSION_TIMEOUT: "300"
AUDIO_BUFFER_SIZE: "4096"
AUDIO_SAMPLE_RATE: "16000"

# Circuit Breaker
CIRCUIT_BREAKER_THRESHOLD: "5"
CIRCUIT_BREAKER_TIMEOUT: "60"
MAX_RETRIES: "3"
```

### Secrets Management

Required secrets in `sofia-secrets`:

- `GOOGLE_API_KEY`: Google Speech-to-Text API key
- `LIVEKIT_API_SECRET`: LiveKit server authentication
- `DATABASE_PASSWORD`: Database encryption password
- `JWT_SECRET`: JSON Web Token signing key
- `ENCRYPTION_KEY`: Application data encryption

### Domain Configuration

Update these domains in `08-ingress-loadbalancer.yaml`:

- `sofia-dental.com`: Main web interface
- `api.sofia-dental.com`: Backend API endpoints
- `voice.sofia-dental.com`: WebRTC voice communication
- `monitoring.sofia-dental.com`: Monitoring dashboards

## 🔍 Monitoring & Observability

### Grafana Dashboards

Access Grafana at `https://monitoring.your-domain.com/grafana`

**Default Credentials**: `admin` / `admin123`

**Available Dashboards**:
- Sofia Voice Agent Overview
- LiveKit Performance Metrics
- Kubernetes Cluster Health
- Application Response Times
- Error Rate Analysis

### Prometheus Metrics

Key metrics collected:

```prometheus
# Voice Session Metrics
sofia_active_sessions          # Current active voice sessions
sofia_session_duration_seconds # Session duration histogram
sofia_requests_total          # Total API requests
sofia_errors_total           # Total errors by type

# Performance Metrics
sofia_request_duration_seconds # Request latency histogram
sofia_memory_usage_bytes      # Memory consumption
sofia_cpu_usage_seconds       # CPU utilization

# Business Metrics
sofia_appointments_booked     # Successful appointment bookings
sofia_customer_satisfaction   # Voice interaction ratings
```

### Log Aggregation

Logs are centralized in persistent volumes:

```bash
# View real-time logs
kubectl logs -f deployment/sofia-agent -n sofia-dental

# View specific service logs
kubectl logs -l app=livekit-server -n sofia-dental --tail=100

# Export logs for analysis
kubectl logs deployment/sofia-agent -n sofia-dental --since=1h > sofia-logs.txt
```

## 🏥 Health Checks & Auto-healing

### Built-in Health Monitoring

- **Liveness Probes**: Restart unhealthy containers
- **Readiness Probes**: Remove unhealthy pods from load balancer
- **Startup Probes**: Allow proper initialization time

### Automated Health Checks

CronJob runs every 5 minutes to check:
- Service endpoint availability
- Response time thresholds
- Error rate monitoring
- Auto-restart failed pods

### Manual Health Check

```bash
# Run deployment validation
kubectl apply -f k8s/09-deployment-scripts.yaml
kubectl logs job/sofia-deployment-init -n sofia-dental

# Check all component status
kubectl get all -n sofia-dental

# View resource usage
kubectl top pods -n sofia-dental
```

## 📈 Scaling & Performance

### Horizontal Pod Autoscaling

Automatic scaling based on:
- CPU utilization (target: 60-70%)
- Memory utilization (target: 70-80%)
- Custom metrics (voice sessions, request rate)

```bash
# View current scaling status
kubectl get hpa -n sofia-dental

# Manual scaling
kubectl scale deployment sofia-agent --replicas=5 -n sofia-dental
```

### Resource Limits

| Component | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----------|-------------|----------------|-----------|-------------|
| Sofia Agent | 500m | 1Gi | 1000m | 2Gi |
| LiveKit | 500m | 512Mi | 1000m | 2Gi |
| Calendar | 200m | 256Mi | 500m | 512Mi |
| Web Interface | 200m | 256Mi | 500m | 512Mi |

### Performance Optimization

1. **Audio Processing**
   - Optimized buffer sizes for low latency
   - Efficient codec selection
   - WebRTC optimization for browser clients

2. **Database Performance**
   - SSD storage for persistent volumes
   - Connection pooling
   - Query optimization

3. **Network Optimization**
   - Session affinity for voice sessions
   - UDP optimization for WebRTC
   - CDN integration for static assets

## 🔒 Security

### Network Security

- **Network Policies**: Restrict inter-pod communication
- **TLS Encryption**: End-to-end encryption for all traffic
- **CORS Configuration**: Proper browser security headers

### Container Security

- **Non-root Containers**: All containers run as unprivileged users
- **Read-only Filesystems**: Immutable container filesystems
- **Security Contexts**: Dropped capabilities and security hardening

### Secrets Management

- **Kubernetes Secrets**: Encrypted at rest
- **RBAC**: Role-based access control
- **Service Accounts**: Minimal required permissions

### SSL/TLS Configuration

```bash
# Automatic certificate management with cert-manager
# Certificates auto-renew before expiration
# Strong cipher suites and TLS 1.2+ only
```

## 🛠️ Troubleshooting

### Common Issues

1. **Browser Can't Connect to Voice**
   ```bash
   # Check LiveKit service status
   kubectl get svc livekit-service -n sofia-dental
   
   # Verify LoadBalancer external IP
   kubectl get svc sofia-dental-loadbalancer -n sofia-dental
   
   # Check WebRTC ports (UDP 7882, 50000-50004)
   kubectl describe svc livekit-loadbalancer -n sofia-dental
   ```

2. **High Memory Usage**
   ```bash
   # Check resource usage
   kubectl top pods -n sofia-dental
   
   # Review memory limits
   kubectl describe pod -l app=sofia-agent -n sofia-dental
   
   # Check for memory leaks
   kubectl logs -f deployment/sofia-agent -n sofia-dental | grep -i memory
   ```

3. **Slow Response Times**
   ```bash
   # Check application metrics
   kubectl port-forward svc/grafana-service 3000:3000 -n sofia-dental
   
   # Review request latency
   kubectl logs deployment/sofia-agent -n sofia-dental | grep "response_time"
   
   # Check database connections
   kubectl exec -it deployment/dental-calendar -n sofia-dental -- ps aux
   ```

### Debug Commands

```bash
# Get detailed pod information
kubectl describe pod -l app=sofia-agent -n sofia-dental

# Access pod shell for debugging
kubectl exec -it deployment/sofia-agent -n sofia-dental -- /bin/bash

# View all events
kubectl get events -n sofia-dental --sort-by='.lastTimestamp'

# Check ingress configuration
kubectl describe ingress sofia-dental-ingress -n sofia-dental

# Test internal connectivity
kubectl run test-pod --image=curlimages/curl -it --rm -- /bin/sh
```

### Log Analysis

```bash
# Grep for specific errors
kubectl logs deployment/sofia-agent -n sofia-dental | grep -i error

# Monitor live logs with filtering
kubectl logs -f deployment/sofia-agent -n sofia-dental | grep "voice_session"

# Export logs for external analysis
kubectl logs --previous deployment/sofia-agent -n sofia-dental > previous-crash.log
```

## 🔄 Updates & Maintenance

### Rolling Updates

```bash
# Update Sofia Agent image
kubectl set image deployment/sofia-agent sofia-agent=your-registry.com/sofia-agent:v1.1.0 -n sofia-dental

# Check rollout status
kubectl rollout status deployment/sofia-agent -n sofia-dental

# Rollback if needed
kubectl rollout undo deployment/sofia-agent -n sofia-dental
```

### Backup & Recovery

```bash
# Backup runs automatically daily at 2 AM
# Manual backup trigger:
kubectl create job --from=cronjob/sofia-backup sofia-backup-manual -n sofia-dental

# Restore from backup
kubectl exec -it deployment/dental-calendar -n sofia-dental -- \
  cp /backups/dental_calendar_20240101_020000.db /app/data/dental_calendar.db
```

### Configuration Updates

```bash
# Update ConfigMap
kubectl patch configmap sofia-config -n sofia-dental --patch='{"data":{"LOG_LEVEL":"DEBUG"}}'

# Restart deployments to pick up config changes
kubectl rollout restart deployment/sofia-agent -n sofia-dental
```

## 📊 Production Readiness Checklist

### Before Going Live

- [ ] Update all default passwords and secrets
- [ ] Configure proper domain names and SSL certificates
- [ ] Set up monitoring alerts and notification channels
- [ ] Test voice functionality from different browsers and networks
- [ ] Verify backup and restore procedures
- [ ] Configure resource quotas and limits
- [ ] Set up log rotation and retention policies
- [ ] Test auto-scaling under load
- [ ] Configure firewall rules and network policies
- [ ] Set up disaster recovery procedures

### Performance Validation

- [ ] Load test with expected concurrent users
- [ ] Verify voice quality under various network conditions
- [ ] Test appointment booking flow end-to-end
- [ ] Validate response times meet SLA requirements
- [ ] Check memory usage under peak load
- [ ] Verify auto-scaling triggers work correctly

### Security Validation

- [ ] SSL certificate validation and renewal
- [ ] Network policy enforcement
- [ ] Container vulnerability scanning
- [ ] Secrets rotation procedures
- [ ] Access control and RBAC validation
- [ ] Penetration testing of external endpoints

## 📞 Support & Contact

### Monitoring Contacts

- **Prometheus**: `https://monitoring.your-domain.com/prometheus`
- **Grafana**: `https://monitoring.your-domain.com/grafana`
- **AlertManager**: `https://monitoring.your-domain.com/alerts`

### Emergency Procedures

1. **Service Down**: Check LoadBalancer and restart failed pods
2. **High Error Rate**: Review logs and check external API status
3. **Voice Issues**: Verify LiveKit service and WebRTC connectivity
4. **Database Issues**: Check persistent volume status and backups

### Getting Help

```bash
# Generate system report
kubectl get all -n sofia-dental -o yaml > sofia-system-report.yaml

# Collect logs for support
kubectl logs deployment/sofia-agent -n sofia-dental --since=1h > support-logs.txt

# Check cluster resources
kubectl describe nodes > cluster-status.txt
```

---

**Sofia Voice Agent v1.0.0** - Production Kubernetes Deployment

*For technical support, please include system reports and relevant log files.*
