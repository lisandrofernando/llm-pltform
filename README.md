# AI Q&A LLM Platform

## Local Testing

### Prerequisites
- Docker and Docker Compose installed
- At least 8GB RAM available for Docker

### Run Locally

1. Start the services:
```bash
docker-compose up --build
```

2. Wait for vLLM to download the model (first run takes a few minutes)

3. Test the backend:
```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is artificial intelligence?"}'
```

4. Stop the services:
```bash
docker-compose down
```

## AWS Deployment

### Prerequisites
- AWS CLI configured
- Terraform installed
- kubectl installed
- Helm installed

### Deploy Infrastructure

1. Initialize Terraform:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

2. Configure kubectl:
```bash
aws eks update-kubeconfig --name ai-qa-cluster --region us-east-1
```

3. Deploy vLLM:
```bash
cd ../helm
helm install vllm ./vllm-smollm
```

4. Build and push backend image:
```bash
cd ../app
docker build -t <YOUR_ECR_REPO>:latest .
docker push <YOUR_ECR_REPO>:latest
```

5. Deploy backend:
```bash
cd ../helm
helm install backend ./backend
```

6. Get the ALB URL:
```bash
kubectl get ingress backend-ingress
```

## Production-Ready Scaling Strategies for LLM Workloads

### Horizontal Pod Autoscaling (HPA)

**Backend Service:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**vLLM Service:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vllm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vllm
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
```

### Cluster Autoscaling

**EKS Node Group Configuration:**
```hcl
eks_managed_node_groups = {
  gpu_nodes = {
    instance_types = ["g4dn.xlarge", "g4dn.2xlarge"]
    min_size       = 1
    max_size       = 10
    desired_size   = 2
    
    labels = {
      workload = "llm"
    }
    
    taints = [{
      key    = "nvidia.com/gpu"
      value  = "true"
      effect = "NoSchedule"
    }]
  }
  
  cpu_nodes = {
    instance_types = ["t3.large", "t3.xlarge"]
    min_size       = 2
    max_size       = 20
    desired_size   = 3
  }
}
```

### Resource Optimization

**1. Model Quantization:**
- Use INT8/INT4 quantization to reduce memory footprint
- Configure vLLM with `--quantization awq` or `--quantization gptq`

**2. Batch Processing:**
```yaml
env:
  - name: VLLM_MAX_BATCH_SIZE
    value: "32"
  - name: VLLM_MAX_SEQ_LEN
    value: "2048"
```

**3. GPU Utilization:**
```yaml
resources:
  limits:
    nvidia.com/gpu: 1
  requests:
    nvidia.com/gpu: 1
```

### Load Balancing Strategy

**1. Application Load Balancer:**
- Distributes traffic across multiple backend pods
- Health checks ensure traffic only to healthy pods
- Connection draining for graceful shutdowns

**2. Service Mesh (Optional):**
```bash
# Install Istio for advanced traffic management
istioctl install --set profile=production
```

### Caching Strategy

**Redis Cache for Frequent Queries:**
```python
import redis

redis_client = redis.Redis(host='redis-service', port=6379)

@app.post("/ask")
def ask_question(request: QuestionRequest):
    cache_key = f"llm:{hash(request.question)}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    response = call_vllm(request.question)
    redis_client.setex(cache_key, 3600, json.dumps(response))
    return response
```

### Monitoring & Observability

**Prometheus Metrics:**
```yaml
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: vllm-metrics
spec:
  selector:
    matchLabels:
      app: vllm
  endpoints:
  - port: metrics
    interval: 30s
```

**Key Metrics to Monitor:**
- Request latency (p50, p95, p99)
- Throughput (requests/second)
- GPU utilization
- Model inference time
- Queue depth
- Error rates

### Cost Optimization

**1. Spot Instances:**
```hcl
eks_managed_node_groups = {
  spot_nodes = {
    instance_types = ["g4dn.xlarge", "g4dn.2xlarge"]
    capacity_type  = "SPOT"
    min_size       = 0
    max_size       = 5
  }
}
```

**2. Scheduled Scaling:**
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: ScheduledAction
metadata:
  name: scale-down-night
spec:
  schedule: "0 22 * * *"
  minReplicas: 1
```

### High Availability

**Multi-AZ Deployment:**
- Deploy across multiple availability zones
- Use pod anti-affinity rules
- Configure PodDisruptionBudget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: vllm-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: vllm
```

### Performance Tuning

**1. Connection Pooling:**
- Configure uvicorn workers: `--workers 4`
- Use connection pooling for vLLM requests

**2. Request Queuing:**
- Implement request queue with timeout
- Use async processing for long-running requests

**3. Model Warm-up:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 120
  periodSeconds: 30
```
