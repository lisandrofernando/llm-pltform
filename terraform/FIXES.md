# Terraform Configuration Fixes

## Issues Fixed

### 1. EKS Module Configuration (eks.tf)
**Problem**: 
- Trying to override EKS module's managed security groups and IAM roles
- `cluster_security_group_id`, `iam_role_arn`, and `vpc_security_group_ids` were conflicting with module's internal management

**Fix**:
- Removed custom security group and IAM role overrides
- Let EKS module create and manage its own resources
- Module automatically creates proper security groups and IAM roles

### 2. Helm Provider Authentication (alb_controller.tf)
**Problem**:
- Using deprecated `token` attribute
- Missing required ALB controller configuration (cluster name, service account)

**Fix**:
- Changed to `exec` block with AWS CLI for dynamic token generation
- Added `clusterName` configuration
- Added service account annotation with IAM role ARN
- Added explicit dependency on EKS module

### 3. VPC Configuration (vpc.tf)
**Problem**:
- Missing DNS settings required for EKS
- Missing subnet tags required for ALB controller auto-discovery

**Fix**:
- Added `enable_dns_hostnames = true`
- Added `enable_dns_support = true`
- Added `kubernetes.io/role/elb` tag to public subnets
- Added `kubernetes.io/role/internal-elb` tag to private subnets

### 4. IAM Policies (iam.tf)
**Problem**:
- Using overly broad `ElasticLoadBalancingFullAccess` managed policy
- Creating custom EKS node role that conflicts with module's role

**Fix**:
- Created specific IAM policy with only required ALB controller permissions
- Removed custom EKS node role (module creates it automatically)
- Policy includes EC2, ELB, WAF, Shield, and tagging permissions

### 5. Security Groups (security.tf)
**Problem**:
- Custom security groups conflicting with EKS module's managed security groups

**Fix**:
- Removed entire file
- EKS module automatically creates and manages security groups with proper rules

### 6. Outputs (outputs.tf)
**Added**:
- Cluster endpoint and name
- VPC and subnet IDs
- Security group IDs
- ALB controller role ARN
- kubectl configuration command

## Terraform File Structure

```
terraform/
├── versions.tf          # Provider version constraints
├── providers.tf         # AWS provider configuration
├── vpc.tf              # VPC with proper tags and DNS
├── eks.tf              # EKS cluster configuration
├── iam.tf              # IAM roles for ALB controller
├── alb_controller.tf   # Helm release for ALB controller
└── outputs.tf          # Output values
```

## Deployment Commands

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan

# Apply configuration
terraform apply

# Configure kubectl
aws eks update-kubeconfig --name ai-qa-cluster --region us-east-1

# Verify cluster
kubectl get nodes
```

## Key Improvements

1. **No Conflicts**: Removed all resource conflicts with EKS module
2. **Proper Authentication**: Helm provider uses AWS CLI for dynamic tokens
3. **EKS Compatibility**: VPC has required DNS and subnet tags
4. **Least Privilege**: IAM policies follow principle of least privilege
5. **Maintainability**: Simplified configuration by leveraging module defaults
6. **Outputs**: Added useful outputs for post-deployment configuration

## Testing

After applying, verify:
```bash
# Check EKS cluster
aws eks describe-cluster --name ai-qa-cluster --region us-east-1

# Check nodes
kubectl get nodes

# Check ALB controller
kubectl get deployment -n kube-system aws-load-balancer-controller

# Check IAM role
aws iam get-role --role-name ai-qa-alb-controller-role
```

## Notes

- EKS module version 20.0.0 automatically handles most security and IAM configurations
- ALB controller requires IRSA (IAM Roles for Service Accounts) which is enabled
- VPC subnet tags are critical for ALB controller to discover subnets
- Helm provider authentication uses AWS CLI to avoid token expiration issues
