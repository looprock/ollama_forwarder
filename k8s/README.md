# Kubernetes Deployment for Ollama Service

This directory contains Kubernetes manifests for deploying the Ollama Service.

## Prerequisites

- Kubernetes cluster (1.24+)
- `kubectl` configured to access your cluster
- Docker image built and pushed to a registry (via GitHub Actions)

## Quick Start

### 1. Update Configuration

Before deploying, update the following files:

**k8s/secret.yaml:**
```yaml
stringData:
  api-key: "your-actual-secret-api-key"  # Change this!
```

**k8s/deployment.yaml:**
```yaml
image: ghcr.io/YOUR_GITHUB_USERNAME/ollama-service:latest  # Update with your image
```

**k8s/secret.yaml (ConfigMap section):**
```yaml
data:
  OLLAMA_URL: "http://your-ollama-host:8080/api/generate"  # Update if needed
  MODEL: "granite4:latest"  # Change model if needed
  PREPEND_STATEMENT: ""  # Add system prompt if desired
```

### 2. Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Or apply individually
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 3. Verify Deployment

```bash
# Check pod status
kubectl get pods -l app=ollama-service

# Check service
kubectl get svc ollama-service

# View logs
kubectl logs -l app=ollama-service --tail=50 -f

# Check deployment
kubectl get deployment ollama-service
```

### 4. Test the Service

```bash
# Port-forward to test locally
kubectl port-forward svc/ollama-service 8080:80

# Test with curl
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-actual-secret-api-key" \
  -d '{"user": "Alice", "message": "What is Python?"}'
```

## GitHub Actions Setup

The included GitHub Actions workflow (`.github/workflows/docker-build.yml`) will automatically:

1. Build the Docker image on push to main
2. Push to GitHub Container Registry (ghcr.io)
3. Tag with branch name, SHA, and `latest`

### Enable GitHub Actions

1. Go to your repository Settings → Actions → General
2. Enable "Read and write permissions" for GITHUB_TOKEN
3. Go to Packages settings and make the package public (or configure image pull secrets)

### Trigger a Build

```bash
git add .
git commit -m "Deploy ollama service"
git push origin main
```

The workflow will build and push the image to `ghcr.io/YOUR_USERNAME/lsl/ollama-service:latest`

## Configuration

### Environment Variables

Configure via ConfigMap (`k8s/secret.yaml`):

- `OLLAMA_URL`: Ollama API endpoint
- `MODEL`: Ollama model to use
- `PREPEND_STATEMENT`: Optional text prepended to all prompts

### Secrets

API key is stored in Kubernetes Secret (`k8s/secret.yaml`):

```bash
# Create/update secret manually
kubectl create secret generic ollama-service-secret \
  --from-literal=api-key='your-new-api-key' \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Resource Limits

Adjust in `k8s/deployment.yaml`:

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Scaling

```bash
# Scale replicas
kubectl scale deployment ollama-service --replicas=5

# Or edit deployment.yaml and reapply
```

## External Access

### Option 1: LoadBalancer Service

Edit `k8s/service.yaml`:

```yaml
spec:
  type: LoadBalancer  # Change from ClusterIP
```

### Option 2: Ingress

Uncomment the Ingress section in `k8s/service.yaml` and configure:

```yaml
spec:
  rules:
  - host: ollama.your-domain.com  # Your domain
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ollama-service
            port:
              number: 80
```

Then apply:

```bash
kubectl apply -f k8s/service.yaml
```

## Monitoring

### View Logs

```bash
# All pods
kubectl logs -l app=ollama-service --tail=100 -f

# Specific pod
kubectl logs ollama-service-xxxxxxxxx-xxxxx
```

### Health Checks

The deployment includes:
- **Liveness probe**: `/health` endpoint (restarts unhealthy pods)
- **Readiness probe**: `/health` endpoint (removes from service when not ready)

### Debugging

```bash
# Describe deployment
kubectl describe deployment ollama-service

# Describe pod
kubectl describe pod -l app=ollama-service

# Get events
kubectl get events --sort-by=.metadata.creationTimestamp

# Execute into pod
kubectl exec -it deployment/ollama-service -- /bin/sh
```

## Updating

### Update Configuration

```bash
# Edit ConfigMap or Secret
kubectl edit configmap ollama-service-config
kubectl edit secret ollama-service-secret

# Restart pods to pick up changes
kubectl rollout restart deployment ollama-service
```

### Update Image

```bash
# After pushing new image via GitHub Actions
kubectl set image deployment/ollama-service \
  ollama-service=ghcr.io/YOUR_USERNAME/lsl/ollama-service:new-tag

# Or trigger rollout with latest tag
kubectl rollout restart deployment ollama-service
```

## Cleanup

```bash
# Delete all resources
kubectl delete -f k8s/

# Or delete individually
kubectl delete deployment ollama-service
kubectl delete service ollama-service
kubectl delete configmap ollama-service-config
kubectl delete secret ollama-service-secret
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod -l app=ollama-service
kubectl logs -l app=ollama-service
```

Common issues:
- Image pull errors: Check image name and registry access
- Secret not found: Ensure secret is created in the same namespace
- Health check failures: Verify Ollama connectivity

### Service not accessible

```bash
kubectl get svc ollama-service
kubectl get endpoints ollama-service
```

Ensure pods are ready and endpoints are populated.

### Ollama connectivity issues

```bash
# Test from inside a pod
kubectl exec -it deployment/ollama-service -- /bin/sh
# Then: curl http://100.85.146.10:8080/api/generate
```

Verify `OLLAMA_URL` in ConfigMap is correct.
