#!/bin/bash
# Install AWS Load Balancer Controller after EKS cluster is created

set -e

echo "Installing AWS Load Balancer Controller..."

# Get the ALB controller IAM role ARN from Terraform output
ALB_ROLE_ARN=$(terraform output -raw alb_controller_role_arn)
CLUSTER_NAME=$(terraform output -raw cluster_name)

echo "Cluster: $CLUSTER_NAME"
echo "IAM Role: $ALB_ROLE_ARN"

# Add EKS Helm repository
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install AWS Load Balancer Controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=$CLUSTER_NAME \
  --set serviceAccount.create=true \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"=$ALB_ROLE_ARN

echo "Waiting for ALB controller to be ready..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/aws-load-balancer-controller -n kube-system

echo "✅ AWS Load Balancer Controller installed successfully!"
