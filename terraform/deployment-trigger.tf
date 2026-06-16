# Note: ECS deployment is handled by GitHub Actions pipeline
# When a new image is pushed to ECR, the pipeline automatically triggers:
# aws ecs update-service --force-new-deployment
#
# Terraform manages the infrastructure (VPC, cluster, service definition)
# GitHub Actions handles the deployment (build, push, update service)
