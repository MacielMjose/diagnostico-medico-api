# Deployment trigger - forces ECS service to redeploy when image changes
# This gets the latest image digest from ECR and uses it as a trigger

data "aws_ecr_image" "app_latest" {
  repository_name = aws_ecr_repository.app.name
  image_tag       = "latest"
  depends_on      = [aws_ecr_repository.app]
}

# Force redeployment when image changes
resource "null_resource" "ecs_deployment_trigger" {
  triggers = {
    image_digest = data.aws_ecr_image.app_latest.image_digest
  }

  provisioner "local-exec" {
    command = <<-EOT
      aws ecs update-service \
        --cluster ${aws_ecs_cluster.main.name} \
        --service ${aws_ecs_service.app.name} \
        --force-new-deployment \
        --region ${var.aws_region}
    EOT
  }

  depends_on = [aws_ecs_service.app]
}
