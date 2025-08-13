# Sofia Dental Voice Agent - Kubernetes Deployment Script (PowerShell)

param(
    [switch]$BuildOnly,
    [switch]$DeployOnly,
    [string]$Namespace = "sofia-dental"
)

Write-Host "🚀 Deploying Sofia Dental Voice Agent to Kubernetes..." -ForegroundColor Blue

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check prerequisites
Write-Status "Checking prerequisites..."

if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Error "kubectl is not installed or not in PATH"
    exit 1
}

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "docker is not installed or not in PATH"
    exit 1
}

if (!$DeployOnly) {
    Write-Status "Building Docker images..."
    
    # Build Sofia Agent image
    Write-Status "Building Sofia Agent image..."
    docker build -t sofia-agent:latest -f Dockerfile.sofia .
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build Sofia Agent image"
        exit 1
    }
    
    # Build Dental Calendar image
    Write-Status "Building Dental Calendar image..."
    docker build -t dental-calendar:latest -f dental-calendar/Dockerfile ./dental-calendar
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build Dental Calendar image"
        exit 1
    }
    
    Write-Success "Docker images built successfully!"
}

if ($BuildOnly) {
    Write-Success "Build completed. Use -DeployOnly to deploy to Kubernetes."
    exit 0
}

# Deploy to Kubernetes
Write-Status "Deploying to Kubernetes..."

# Create namespace
Write-Status "Creating namespace..."
kubectl apply -f k8s/namespace.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create namespace"
    exit 1
}

# Apply ConfigMaps and Secrets
Write-Status "Applying configuration..."
kubectl apply -f k8s/configmap.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to apply configuration"
    exit 1
}

# Deploy LiveKit Server
Write-Status "Deploying LiveKit Server..."
kubectl apply -f k8s/livekit-deployment.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to deploy LiveKit Server"
    exit 1
}

# Wait for LiveKit to be ready
Write-Status "Waiting for LiveKit to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/livekit-server -n $Namespace
if ($LASTEXITCODE -ne 0) {
    Write-Warning "LiveKit deployment may not be ready yet"
}

# Deploy Dental Calendar
Write-Status "Deploying Dental Calendar..."
kubectl apply -f k8s/dental-calendar-deployment.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to deploy Dental Calendar"
    exit 1
}

# Deploy Sofia Agent
Write-Status "Deploying Sofia Agent..."
kubectl apply -f k8s/sofia-agent-deployment.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to deploy Sofia Agent"
    exit 1
}

# Deploy Ingress
Write-Status "Deploying Ingress..."
kubectl apply -f k8s/ingress.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Failed to deploy Ingress (may not be supported in this cluster)"
}

# Wait for deployments
Write-Status "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/dental-calendar -n $Namespace
kubectl wait --for=condition=available --timeout=300s deployment/sofia-agent -n $Namespace

Write-Success "Deployment completed!"

# Show status
Write-Status "Deployment Status:"
kubectl get pods -n $Namespace
kubectl get services -n $Namespace

# Setup port forwarding for local access
Write-Status "Setting up port forwarding for local access..."

Write-Host ""
Write-Host "📋 Access Information:" -ForegroundColor Yellow
Write-Host "To access the services locally, run these commands in separate terminals:"
Write-Host ""
Write-Host "# Dental Calendar (Voice-enabled)" -ForegroundColor Cyan
Write-Host "kubectl port-forward service/dental-calendar-service 3005:3005 -n $Namespace" -ForegroundColor White
Write-Host ""
Write-Host "# LiveKit Voice Server" -ForegroundColor Cyan  
Write-Host "kubectl port-forward service/livekit-service 7880:7880 -n $Namespace" -ForegroundColor White
Write-Host ""
Write-Host "# Sofia Agent Health" -ForegroundColor Cyan
Write-Host "kubectl port-forward service/sofia-agent-service 8080:8080 -n $Namespace" -ForegroundColor White

Write-Success "🎉 Sofia Dental Voice Agent deployment completed!"
Write-Status "Voice features are now integrated into the calendar system."

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run the port-forward commands above"
Write-Host "2. Access calendar at: http://localhost:3005"
Write-Host "3. Click '🎤 Mit Sofia sprechen' to test voice"
Write-Host "4. Monitor logs: kubectl logs -f deployment/sofia-agent -n $Namespace"
Write-Host "5. Test appointment booking via voice"
