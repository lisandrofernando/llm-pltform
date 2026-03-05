# CI/CD Pipeline Setup

## Overview
The GitHub Actions pipeline automates building, testing, security scanning, and deploying the AI Q&A backend application.

## Pipeline Triggers
- **Push to branches**: `main`, `development`
- **Manual trigger**: workflow_dispatch

## Jobs

### 1. Build Application
- Checks out code
- Sets up Python 3.10
- Installs dependencies
- Builds Docker image
- Saves image as artifact for downstream jobs

### 2. Security Scan (Trivy)
- Downloads built Docker image
- Scans for vulnerabilities (CRITICAL & HIGH severity)
- Fails pipeline if vulnerabilities found

### 3. Test Application
- Runs application tests
- Validates code functionality

### 4. Push to ECR
- Runs only if all previous jobs succeed
- Authenticates with AWS
- Pushes image to Amazon ECR with:
  - Commit SHA tag
  - `latest` tag

## Required GitHub Secrets

Add these secrets in your repository settings (Settings → Secrets and variables → Actions):

```
AWS_ACCESS_KEY_ID       - AWS access key for ECR push
AWS_SECRET_ACCESS_KEY   - AWS secret key for ECR push
```

## Environment Variables

Configure in the workflow file:
- `AWS_REGION`: us-east-1 (default)
- `ECR_REPOSITORY`: ai-qa-backend

## Prerequisites

1. **Create ECR Repository**:
```bash
aws ecr create-repository \
  --repository-name ai-qa-backend \
  --region us-east-1
```

2. **IAM Permissions**:
The AWS credentials need these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    }
  ]
}
```

## Pipeline Flow

```
┌─────────────┐
│   Trigger   │
│ (push/manual)│
└──────┬──────┘
       │
       v
┌─────────────┐
│    Build    │
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       v              v              v
┌─────────────┐ ┌──────────┐ ┌──────────┐
│  Security   │ │   Test   │ │          │
│    Scan     │ │          │ │          │
└──────┬──────┘ └────┬─────┘ └────┬─────┘
       │             │            │
       └─────────────┴────────────┘
                     │
                     v
              ┌─────────────┐
              │  Push ECR   │
              └─────────────┘
```

## Usage

### Automatic Deployment
Push to `main` or `development` branch:
```bash
git push origin main
```

### Manual Deployment
1. Go to Actions tab in GitHub
2. Select "CI/CD Pipeline"
3. Click "Run workflow"
4. Select branch and run

## Monitoring

View pipeline status:
- GitHub Actions tab
- Commit status checks
- ECR console for pushed images
