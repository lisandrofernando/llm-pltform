# AI Q&A LLM Platform

Production-ready AI Q&A platform using vLLM and FastAPI on AWS EKS with comprehensive scaling strategies for LLM workloads.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [AWS Deployment](#aws-deployment)
- [Scaling Strategies](#scaling-strategies)
- [Monitoring & Observability](#monitoring--observability)
- [Cost Optimization](#cost-optimization)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

### High-Level Architecture

```
                                    ┌─────────────────────────────────────┐
                                    │         AWS Cloud (us-east-1)       │
                                    │                                     │
┌──────────┐                        │  ┌───────────────────────────────┐ │
│  Client  │───────────────────────────►│  Application Load Balancer    │ │
└──────────┘      HTTPS/HTTP        │  │  (Internet-facing)            │ │
                                    │  └───────────┬───────────────────┘ │
                                    │              │                     │
                                    │  ┌───────────▼───────────────────┐ │
                                    │  │   EKS Cluster (ai-qa-cluster) │ │
                                    │  │                               │ │
                                    │  │  ┌─────────────────────────┐  │ │
                                    │  │  │  Backend Pods (2-20)    │  │ │
                                    │  │  │  FastAPI + Uvicorn      │  │ │
                                    │  │  │  Port: 8080             │  │ │
                                    │  │  └──────────┬──────────────┘  │ │
                                    │  │             │                 │ │
                                    │  │  ┌──────────▼──────────────┐  │ │
                                    │  │  │  vLLM Pods (1-5)        │  │ │
                                    │  │  │  SmolLM2-135M-Instruct  │  │ │
                                    │  │  │  Port: 8000             │  │ │
                                    │  │  └─────────────────────────┘  │ │
                                    │  │                               │ │
                                    │  │  ┌─────────────────────────┐  │ │
                                    │  │  │  Redis Cache (Optional) │  │ │
                                    │  │  └─────────────────────────┘  │ │
                                    │  └───────────────────────────────┘ │
                                    └─────────────────────────────────────┘
```

### Detailed AWS Infrastructure

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          VPC (10.0.0.0/16)                                 │
│                                                                            │
│  ┌─────────────────────────────────┬─────────────────────────────────┐   │
│  │  Availability Zone us-east-1a   │  Availability Zone us-east-1b   │   │
│  │                                 │                                 │   │
│  │  ┌──────────────────────────┐   │  ┌──────────────────────────┐   │   │
│  │  │ Public Subnet            │   │  │ Public Subnet            │   │   │
│  │  │ 10.0.101.0/24            │   │  │ 10.0.102.0/24            │   │   │
│  │  │                          │   │  │                          │   │   │
│  │  │  ┌────────────────────┐  │   │  │  ┌────────────────────┐  │   │   │
│  │  │  │  NAT Gateway       │  │   │  │  │  ALB (Public)      │  │   │   │
│  │  │  └────────────────────┘  │   │  │  └────────────────────┘  │   │   │
│  │  └──────────┬───────────────┘   │  └──────────────────────────┘   │   │
│  │             │                     │                                 │   │
│  │  ┌──────────▼───────────────┐   │  ┌──────────────────────────┐   │   │
│  │  │ Private Subnet           │   │  │ Private Subnet           │   │   │
│  │  │ 10.0.1.0/24              │   │  │ 10.0.2.0/24              │   │   │
│  │  │                          │   │  │                          │   │   │
│  │  │  ┌────────────────────┐  │   │  │  ┌────────────────────┐  │   │   │
│  │  │  │ EKS Worker Nodes   │  │   │  │  │ EKS Worker Nodes   │  │   │   │
│  │  │  │ (t3.medium)        │  │   │  │  │ (t3.medium)        │  │   │   │
│  │  │  │                    │  │   │  │  │                    │  │   │   │
│  │  │  │ - Backend Pods     │  │   │  │  │ - Backend Pods     │  │   │   │
│  │  │  │ - vLLM Pods        │  │   │  │  │ - vLLM Pods        │  │   │   │
│  │  │  └────────────────────┘  │   │  │  └────────────────────┘  │   │   │
│  │  └──────────────────────────┘   │  └──────────────────────────┘   │   │
│  └─────────────────────────────────┴─────────────────────────────────┘   │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  EKS Control Plane (Managed by AWS)                              │    │
│  │  - API Server  - Scheduler  - Controller Manager                 │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  Supporting Services                                                       │
│  - ECR (Container Registry)                                                │
│  - CloudWatch (Logging & Monitoring)                                       │
│  - IAM (Roles & Policies)                                                  │
│  - Route 53 (DNS - Optional)                                               │
└────────────────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
1. Client Request
   │
   ▼
2. Internet Gateway
   │
   ▼
3. Application Load Balancer (ALB)
   │  - Health checks
   │  - SSL termination
   │  - Path-based routing
   ▼
4. Backend Service (Kubernetes Service)
   │  - Load balancing across pods
   │  - Session affinity (optional)
   ▼
5. Backend Pod (FastAPI)
   │  - Request validation
   │  - Cache check (Redis)
   │  - Rate limiting
   ▼
6. vLLM Service (Kubernetes Service)
   │  - Internal load balancing
   ▼
7. vLLM Pod
   │  - Model inference
   │  - Token generation
   ▼
8. Response back through chain
```

**Components:**
- **Backend**: FastAPI application handling HTTP requests
- **vLLM**: High-performance LLM inference engine
- **EKS**: Managed Kubernetes cluster (v1.29)
- **ALB**: Application Load Balancer for traffic distribution
- **VPC**: Isolated network with public/private subnets across 2 AZs
- **NAT Gateway**: Enables private subnet internet access
- **ECR**: Container image registry
- **IAM**: Identity and access management

## Prerequisites

### Local Development
- Docker 20.10+ and Docker Compose 2.0+
- 8GB+ RAM available for Docker
- Python 3.11+ (for standalone testing)

### AWS Deployment
- AWS CLI 2.0+ configured with appropriate credentials
- Terraform 1.5+
- kubectl 1.29+
- Helm 3.12+
- AWS account with permissions for EKS, VPC, IAM, EC2

### Required AWS Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "eks:*", "ec2:*", "iam:*", "elasticloadbalancing:*",
      "autoscaling:*", "cloudwatch:*", "logs:*"
    ],
    "Resource": "*"
  }]
}
```

## Local Development

### Quick Start

1. **Clone and navigate to project:**
```bash
cd ai-qa-llm-platform
```

2. **Start services:**
```bash
docker-compose up --build
```

3. **Wait for model download** (first run: 2-5 minutes)
```bash
# Monitor logs
docker-compose logs -f vllm
```

4. **Test the API:**
```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is artificial intelligence?"}'
```

5. **Stop services:**
```bash
docker-compose down
```

### Mock Testing (No GPU Required)
```bash
docker-compose -f docker-compose.mock.yml up
```

## AWS Deployment

### Step 1: Infrastructure Setup

**1.1 Configure AWS credentials:**
```bash
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)
```

**1.2 Initialize Terraform:**
```bash
cd terraform
terraform init
```

**1.3 Review infrastructure plan:**
```bash
terraform plan
```

Expected resources:
- VPC with 2 AZs (10.0.0.0/16)
- EKS cluster (v1.29)
- 2 managed node groups
- ALB controller
- IAM roles and policies

**1.4 Deploy infrastructure:**
```bash
terraform apply
# Type 'yes' when prompted
# Deployment time: 15-20 minutes
```

**1.5 Verify deployment:**
```bash
terraform output
```

### Step 2: Configure kubectl

```bash
aws eks update-kubeconfig --name ai-qa-cluster --region us-east-1

# Verify connection
kubectl get nodes
kubectl get namespaces
```

### Step 3: Install AWS Load Balancer Controller

```bash
cd terraform
./install-alb-controller.sh

# Verify installation
kubectl get deployment -n kube-system aws-load-balancer-controller
```

### Step 4: Deploy vLLM Service

```bash
cd ../helm

# Review configuration
cat vllm-smollm/values.yaml

# Deploy vLLM
helm install vllm ./vllm-smollm

# Monitor deployment
kubectl get pods -w
kubectl logs -f deployment/vllm
```

**Wait for vLLM to be ready** (5-10 minutes for model download)

### Step 5: Build and Push Backend Image

**5.1 Create ECR repository:**
```bash
aws ecr create-repository --repository-name ai-qa-backend --region us-east-1
```

**5.2 Authenticate Docker to ECR:**
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

**5.3 Build and push image:**
```bash
cd ../app

docker build -t ai-qa-backend:latest .

docker tag ai-qa-backend:latest \
  <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/ai-qa-backend:latest

docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/ai-qa-backend:latest
```

### Step 6: Deploy Backend Service

**6.1 Update Helm values:**
```bash
cd ../helm/backend

# Edit values.yaml
vim values.yaml
# Update: image.repository to your ECR URL
```

**6.2 Deploy backend:**
```bash
helm install backend ./backend

# Verify deployment
kubectl get pods
kubectl get svc
kubectl get ingress
```

**6.3 Get ALB URL:**
```bash
kubectl get ingress backend-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

### Step 7: Test Deployment

```bash
export ALB_URL=$(kubectl get ingress backend-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

curl -X POST http://$ALB_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain machine learning in simple terms"}'
```

## Scaling Strategies

### 1. Horizontal Pod Autoscaling (HPA)

**Backend Service HPA:**
```yaml
# backend-hpa.yaml
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
  maxReplicas: 20
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

**vLLM Service HPA:**
```yaml
# vllm-hpa.yaml
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
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 85
```

**Apply HPA:**
```bash
kubectl apply -f backend-hpa.yaml
kubectl apply -f vllm-hpa.yaml

# Monitor autoscaling
kubectl get hpa -w
```

### 2. Cluster Autoscaling

**Update EKS node groups in terraform/eks.tf:**
```hcl
eks_managed_node_groups = {
  # CPU-optimized nodes for backend
  cpu_nodes = {
    instance_types = ["t3.large", "t3.xlarge"]
    min_size       = 2
    max_size       = 20
    desired_size   = 3
    
    labels = {
      workload = "backend"
    }
  }
  
  # Memory-optimized nodes for vLLM
  memory_nodes = {
    instance_types = ["r5.xlarge", "r5.2xlarge"]
    min_size       = 1
    max_size       = 10
    desired_size   = 2
    
    labels = {
      workload = "llm"
    }
    
    taints = [{
      key    = "workload"
      value  = "llm"
      effect = "NoSchedule"
    }]
  }
  
  # GPU nodes for production LLM workloads
  gpu_nodes = {
    instance_types = ["g4dn.xlarge", "g4dn.2xlarge"]
    min_size       = 0
    max_size       = 5
    desired_size   = 0
    
    labels = {
      workload     = "llm-gpu"
      "nvidia.com/gpu" = "true"
    }
    
    taints = [{
      key    = "nvidia.com/gpu"
      value  = "true"
      effect = "NoSchedule"
    }]
  }
}
```

**Install Cluster Autoscaler:**
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml

kubectl -n kube-system annotate deployment.apps/cluster-autoscaler \
  cluster-autoscaler.kubernetes.io/safe-to-evict="false"

kubectl -n kube-system set image deployment.apps/cluster-autoscaler \
  cluster-autoscaler=registry.k8s.io/autoscaling/cluster-autoscaler:v1.29.0
```

### 3. Vertical Pod Autoscaling (VPA)

**Install VPA:**
```bash
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

**Configure VPA for vLLM:**
```yaml
# vllm-vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vllm-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vllm
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: vllm
      minAllowed:
        cpu: 2
        memory: 4Gi
      maxAllowed:
        cpu: 8
        memory: 16Gi
```

### 4. Load Balancing Strategies

**Connection-based routing:**
```yaml
# backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
spec:
  type: LoadBalancer
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 300
```

**Request queuing with rate limiting:**
```python
# Add to app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/ask")
@limiter.limit("10/minute")
async def ask_question(request: Request, question: QuestionRequest):
    # Implementation
```

### 5. Model Optimization

**Quantization for reduced memory:**
```yaml
# vllm deployment with quantization
env:
  - name: VLLM_QUANTIZATION
    value: "awq"  # or "gptq", "squeezellm"
  - name: VLLM_MAX_MODEL_LEN
    value: "2048"
  - name: VLLM_GPU_MEMORY_UTILIZATION
    value: "0.9"
```

**Batch processing configuration:**
```yaml
env:
  - name: VLLM_MAX_NUM_BATCHED_TOKENS
    value: "8192"
  - name: VLLM_MAX_NUM_SEQS
    value: "256"
  - name: VLLM_ENABLE_PREFIX_CACHING
    value: "true"
```

### 6. Caching Strategy

**Deploy Redis for response caching:**
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis \
  --set auth.enabled=false \
  --set master.persistence.size=8Gi
```

**Update backend with caching:**
```python
import redis
import hashlib

redis_client = redis.Redis(host='redis-master', port=6379, decode_responses=True)

@app.post("/ask")
async def ask_question(question: QuestionRequest):
    cache_key = f"llm:{hashlib.sha256(question.question.encode()).hexdigest()}"
    
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    response = await call_vllm(question.question)
    redis_client.setex(cache_key, 3600, json.dumps(response))
    return response
```

### 7. High Availability Configuration

**Pod Disruption Budget:**
```yaml
# pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: backend-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: backend
---
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

**Pod Anti-Affinity:**
```yaml
# Spread pods across nodes
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - vllm
        topologyKey: kubernetes.io/hostname
```

## Monitoring & Observability

### Install Prometheus & Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

### Access Grafana

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Default credentials: admin / prom-operator
```

### Key Metrics to Monitor

**Application Metrics:**
- Request latency (p50, p95, p99)
- Throughput (requests/second)
- Error rate (4xx, 5xx)
- Queue depth
- Cache hit rate

**Infrastructure Metrics:**
- CPU utilization per pod
- Memory usage per pod
- Network I/O
- Disk I/O
- Node count

**LLM-Specific Metrics:**
- Model inference time
- Token generation rate
- Batch size utilization
- GPU memory usage (if applicable)
- Model loading time

### Custom Metrics

```python
# Add to app/main.py
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('llm_requests_total', 'Total LLM requests')
REQUEST_LATENCY = Histogram('llm_request_duration_seconds', 'LLM request latency')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Cost Optimization

### 1. Use Spot Instances

```hcl
# terraform/eks.tf
eks_managed_node_groups = {
  spot_nodes = {
    instance_types = ["t3.large", "t3.xlarge", "t3a.large"]
    capacity_type  = "SPOT"
    min_size       = 1
    max_size       = 10
    desired_size   = 2
  }
}
```

### 2. Right-Sizing Resources

```bash
# Analyze resource usage
kubectl top nodes
kubectl top pods

# Use VPA recommendations
kubectl describe vpa vllm-vpa
```

### 3. Scheduled Scaling

```yaml
# scale-schedule.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scale-down-night
spec:
  schedule: "0 22 * * *"  # 10 PM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: kubectl
            image: bitnami/kubectl
            command:
            - kubectl
            - scale
            - deployment/backend
            - --replicas=1
```

### 4. Enable Cluster Autoscaler Scale-Down

```bash
kubectl -n kube-system edit deployment cluster-autoscaler

# Add flags:
# --scale-down-enabled=true
# --scale-down-delay-after-add=10m
# --scale-down-unneeded-time=10m
```

## Troubleshooting

### Common Issues

**1. Pods stuck in Pending:**
```bash
kubectl describe pod <pod-name>
# Check: Insufficient resources, node selector mismatch, taints
```

**2. ALB not created:**
```bash
kubectl logs -n kube-system deployment/aws-load-balancer-controller
# Verify: IAM permissions, subnet tags
```

**3. vLLM OOM errors:**
```bash
# Increase memory limits in values.yaml
resources:
  limits:
    memory: "16Gi"
```

**4. High latency:**
```bash
# Check vLLM logs
kubectl logs deployment/vllm

# Enable batch processing
# Increase max_num_seqs in vLLM config
```

### Debugging Commands

```bash
# Check cluster status
kubectl cluster-info
kubectl get nodes -o wide

# Check pod logs
kubectl logs -f deployment/backend
kubectl logs -f deployment/vllm --tail=100

# Check resource usage
kubectl top nodes
kubectl top pods

# Describe resources
kubectl describe deployment backend
kubectl describe ingress backend-ingress

# Check HPA status
kubectl get hpa
kubectl describe hpa backend-hpa

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Cleanup

```bash
# Delete Helm releases
helm uninstall backend
helm uninstall vllm
helm uninstall prometheus

# Destroy infrastructure
cd terraform
terraform destroy
```

## Additional Resources

- [vLLM Documentation](https://docs.vllm.ai/)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Kubernetes Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)

## License

MIT
