#!/bin/bash
# Sofia Agent Auto-Deployment Setup Script
# This script sets up the complete Sofia Kubernetes auto-deployment system

set -e

echo "🚀 Setting up Sofia Agent Auto-Deployment System..."
echo "=================================================="

# Configuration
NAMESPACE="dental-voice"
IMAGE_NAME="sofia-agent:auto-deploy"
CONTEXT=$(kubectl config current-context)

echo "📋 Configuration:"
echo "  Namespace: $NAMESPACE"
echo "  Image: $IMAGE_NAME"
echo "  Context: $CONTEXT"
echo ""

# Step 1: Create namespace if it doesn't exist
echo "1️⃣ Creating namespace '$NAMESPACE'..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Step 2: Build Sofia Docker image
echo "2️⃣ Building Sofia Docker image..."
cd ..
docker build -f Dockerfile.sofia -t $IMAGE_NAME .

# Step 3: Apply RBAC configuration
echo "3️⃣ Setting up RBAC for Sofia deployment manager..."
kubectl apply -f k8s/sofia-rbac.yaml

# Step 4: Create secrets (if not exist)
echo "4️⃣ Creating LiveKit secrets..."
kubectl create secret generic livekit-secrets \
  --namespace=$NAMESPACE \
  --from-literal=LIVEKIT_API_KEY="devkey" \
  --from-literal=LIVEKIT_API_SECRET="secret" \
  --from-literal=LIVEKIT_URL="ws://livekit:7880" \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 5: Deploy Sofia auto-deployment system
echo "5️⃣ Deploying Sofia auto-deployment system..."
kubectl apply -f k8s/sofia-auto-deployment.yaml

# Step 6: Verify deployment
echo "6️⃣ Verifying deployment..."
kubectl get deployments -n $NAMESPACE
kubectl get services -n $NAMESPACE
kubectl get hpa -n $NAMESPACE

# Step 7: Create initial job template
echo "7️⃣ Setting up deployment job template..."
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: sofia-deployment-test
  namespace: $NAMESPACE
spec:
  template:
    spec:
      containers:
      - name: test-deployment
        image: bitnami/kubectl:latest
        command:
        - /bin/sh
        - -c
        - |
          echo "Testing Sofia deployment scaling..."
          kubectl get deployment sofia-agent-auto -n $NAMESPACE
          echo "Sofia auto-deployment system is ready!"
      restartPolicy: Never
      serviceAccountName: sofia-deployment-manager
  backoffLimit: 1
  ttlSecondsAfterFinished: 60
EOF

echo ""
echo "✅ Sofia Agent Auto-Deployment System Setup Complete!"
echo ""
echo "📋 Summary:"
echo "  ✓ Namespace '$NAMESPACE' created"
echo "  ✓ Docker image '$IMAGE_NAME' built"
echo "  ✓ RBAC configuration applied"
echo "  ✓ Secrets created/updated"
echo "  ✓ Sofia auto-deployment system deployed"
echo "  ✓ HPA (Horizontal Pod Autoscaler) configured"
echo ""
echo "🚀 How it works:"
echo "  1. Sofia deployment starts with 0 replicas (idle)"
echo "  2. When Sofia button is clicked in calendar:"
echo "     - Calendar server calls /api/sofia/deploy"
echo "     - Server executes 'kubectl scale deployment sofia-agent-auto --replicas=1'"
echo "     - Kubernetes creates Sofia pod in ~30-60 seconds"
echo "     - User gets LiveKit token and connects to sofia-room"
echo "     - Sofia greets user automatically when pod is ready"
echo ""
echo "🔧 Manual Testing:"
echo "  # Scale Sofia to 1 replica manually:"
echo "  kubectl scale deployment sofia-agent-auto --replicas=1 -n $NAMESPACE"
echo ""
echo "  # Check Sofia pod status:"
echo "  kubectl get pods -l app=sofia-agent-auto -n $NAMESPACE"
echo ""
echo "  # View Sofia logs:"
echo "  kubectl logs -l app=sofia-agent-auto -n $NAMESPACE -f"
echo ""
echo "  # Scale back to 0 (idle):"
echo "  kubectl scale deployment sofia-agent-auto --replicas=0 -n $NAMESPACE"
echo ""
echo "🌐 Calendar Integration:"
echo "  - Calendar server now has /api/sofia/deploy endpoint"
echo "  - Sofia button triggers Kubernetes deployment"
echo "  - Browser connects via LiveKit when Sofia is ready"
echo ""
echo "🎯 Next Steps:"
echo "  1. Start calendar server: cd dental-calendar && npm start"
echo "  2. Open browser: http://localhost:3005"
echo "  3. Click 'Start Sofia Agent' button"
echo "  4. Sofia will deploy automatically in Kubernetes!"
echo ""

# Optional: Display current status
echo "📊 Current Status:"
kubectl get all -n $NAMESPACE | grep sofia || echo "No Sofia resources currently running"

echo ""
echo "🎉 Sofia Agent Auto-Deployment is ready to use!"