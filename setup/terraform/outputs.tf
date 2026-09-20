output "aws_account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  value = var.aws_region
}

output "cluster_name" {
  value = aws_eks_cluster.main.name
}

output "cluster_version" {
  value = aws_eks_cluster.main.version
}

output "frontend_ecr" {
  value = aws_ecr_repository.frontend.repository_url
}

output "backend_ecr" {
  value = aws_ecr_repository.backend.repository_url
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}

output "github_actions_secrets" {
  value = {
    AWS_ROLE_ARN            = aws_iam_role.github_actions.arn
    AWS_REGION              = var.aws_region
    EKS_CLUSTER_NAME        = aws_eks_cluster.main.name
    ECR_REPOSITORY_BACKEND  = aws_ecr_repository.backend.name
    ECR_REPOSITORY_FRONTEND = aws_ecr_repository.frontend.name
  }
}

output "next_commands" {
  value = <<-EOT
    aws eks update-kubeconfig --name ${aws_eks_cluster.main.name} --region ${var.aws_region}
    kubectl get nodes
    terraform output -json github_actions_secrets
  EOT
}
