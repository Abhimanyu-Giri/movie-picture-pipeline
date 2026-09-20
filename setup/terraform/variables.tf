variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "movie-picture-pipeline"
}

variable "cluster_name" {
  type    = string
  default = "movie-picture-pipeline"
}

variable "kubernetes_version" {
  type        = string
  description = "Use a version in EKS standard support to avoid extended-support charges."
  default     = "1.35"
}

variable "node_instance_type" {
  type        = string
  description = "One small node is sufficient for this short-lived proof deployment."
  default     = "t3.small"
}

variable "frontend_ecr_repo" {
  type    = string
  default = "frontend"
}

variable "backend_ecr_repo" {
  type    = string
  default = "backend"
}

variable "github_owner" {
  type    = string
  default = "Abhimanyu-Giri"
}

variable "github_repo" {
  type    = string
  default = "movie-picture-pipeline"
}

variable "billing_email" {
  type        = string
  description = "Email for AWS Budget alerts. Empty disables budget creation."
  default     = ""
}

variable "monthly_budget_usd" {
  type        = number
  description = "Account-level alert threshold. A budget warns; it does not stop resources."
  default     = 10
}
