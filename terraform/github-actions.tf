# GitHub Actions OIDC Provider and IAM Role

variable "github_username" {
  description = "GitHub username or organization"
  type        = string
  default     = "MacielMjose"  # Change to your GitHub username
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "diagnostico-medico-api"
}

# Data source to reference existing OIDC Provider
# (It was already created outside of Terraform)
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

# IAM Role for GitHub Actions
resource "aws_iam_role" "github_actions" {
  name = "GitHub-Actions-Deploy"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_username}/${var.github_repo}:*"
          }
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Name = "GitHub-Actions-Deploy"
  }
}

# Attach ECR permissions
resource "aws_iam_role_policy_attachment" "github_ecr" {
  role       = aws_iam_role.github_actions.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

# Attach ECS permissions
resource "aws_iam_role_policy" "github_ecs" {
  name = "GitHub-Actions-ECS-Deploy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "iam:PassRole"
        ]
        Resource = "*"
      }
    ]
  })
}

# Output the role ARN for GitHub secrets
output "github_actions_role_arn" {
  description = "ARN of the GitHub Actions IAM role"
  value       = aws_iam_role.github_actions.arn
}

output "oidc_provider_arn" {
  description = "ARN of the GitHub Actions OIDC provider"
  value       = data.aws_iam_openid_connect_provider.github.arn
}
