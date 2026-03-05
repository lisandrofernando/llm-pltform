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
