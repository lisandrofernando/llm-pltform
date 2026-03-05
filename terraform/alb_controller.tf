# ALB Controller will be installed manually after cluster creation
# Run: helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
#   -n kube-system \
#   --set clusterName=ai-qa-cluster \
#   --set serviceAccount.create=true \
#   --set serviceAccount.name=aws-load-balancer-controller \
#   --set serviceAccount.annotations.eks\.amazonaws\.com/role-arn=<ALB_CONTROLLER_ROLE_ARN>

# Uncomment below after EKS cluster is created and kubectl is configured
# resource "helm_release" "aws_load_balancer_controller" {
#   name       = "aws-load-balancer-controller"
#   repository = "https://aws.github.io/eks-charts"
#   chart      = "aws-load-balancer-controller"
#   namespace  = "kube-system"
#
#   set {
#     name  = "clusterName"
#     value = module.eks.cluster_name
#   }
#
#   set {
#     name  = "serviceAccount.create"
#     value = "true"
#   }
#
#   set {
#     name  = "serviceAccount.name"
#     value = "aws-load-balancer-controller"
#   }
#
#   set {
#     name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
#     value = aws_iam_role.alb_controller.arn
#   }
#
#   depends_on = [module.eks]
# }
