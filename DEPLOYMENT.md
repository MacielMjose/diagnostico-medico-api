# Deployment Guide - AWS Fargate

This guide provides instructions for deploying the Diagnostico Médico API to AWS using Fargate with Terraform infrastructure-as-code.

## Architecture Overview

The solution uses:
- **AWS Fargate**: Serverless container orchestration
- **Amazon ECS**: Elastic Container Service for container management
- **Amazon ECR**: Elastic Container Registry for Docker images
- **Application Load Balancer (ALB)**: Route traffic to tasks
- **Auto Scaling**: Dynamic scaling based on CPU, memory, and request count
- **VPC**: Isolated network with public and private subnets
- **NAT Gateway**: Allow private subnets to access the internet
- **CloudWatch**: Logs and monitoring

## Prerequisites

1. **AWS Account** with permissions to create:
   - VPC, subnets, NAT gateways
   - ECR repositories
   - ECS clusters and services
   - Application Load Balancers
   - CloudWatch log groups
   - IAM roles and policies

2. **Local Tools**:
   - Terraform >= 1.0
   - AWS CLI v2
   - Docker (for testing images locally)
   - Git

3. **AWS Credentials**: Configure AWS credentials locally
   ```bash
   aws configure
   # or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables
   ```

## Setup Instructions

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Plan the Infrastructure

```bash
terraform plan -out=tfplan
```

Review the plan to ensure all resources are correct.

### 3. Apply the Infrastructure

```bash
terraform apply tfplan
```

This will create:
- VPC with public and private subnets
- ECR repository
- ECS cluster with Fargate capacity providers
- Application Load Balancer
- Auto Scaling configuration
- CloudWatch log group
- IAM roles and security groups

### 4. Get Outputs

After successful deployment, get the infrastructure details:

```bash
terraform output
```

Key outputs:
- `ecr_repository_url`: URL for pushing Docker images
- `application_url`: URL to access your API
- `ecs_cluster_name`: ECS cluster name
- `ecs_service_name`: ECS service name

## Docker Image Management

### Build and Push Image Manually

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t diagnostico-medico-api:v1.0 .

# Tag for ECR
docker tag diagnostico-medico-api:v1.0 \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/diagnostico-medico-api:v1.0

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/diagnostico-medico-api:v1.0
```

### Test Image Locally

```bash
docker build -t diagnostico-medico-api:latest .
docker run -p 8000:8000 diagnostico-medico-api:latest

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/swagger
```

## GitHub Actions Setup

The CI/CD pipeline is configured in `.github/workflows/pipeline.yml`.

### 1. Configure AWS OIDC Authentication

Set up OIDC provider for GitHub Actions:

```bash
# Create OIDC provider
aws iam create-openid-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# Create IAM role for GitHub Actions
aws iam create-role \
  --role-name GitHub-Actions-Deploy \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
        },
        "Action": "sts:AssumeRoleWithWebIdentity",
        "Condition": {
          "StringLike": {
            "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_ORG/diagnostico-medico-api:*"
          }
        }
      }
    ]
  }'

# Attach policy
aws iam attach-role-policy \
  --role-name GitHub-Actions-Deploy \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser

# Attach ECS deployment policy
aws iam put-role-policy \
  --role-name GitHub-Actions-Deploy \
  --policy-name ECS-Deploy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:DescribeContainerInstances",
          "ecs:UpdateTaskSet",
          "iam:PassRole"
        ],
        "Resource": "*"
      }
    ]
  }'
```

### 2. Add GitHub Secrets

Add the following secret to your GitHub repository settings:

```
AWS_ROLE_TO_ASSUME=arn:aws:iam::ACCOUNT_ID:role/GitHub-Actions-Deploy
```

Where `ACCOUNT_ID` is your AWS Account ID.

## Deployment Process

### Automatic Deployment (via GitHub Actions)

1. Push code to main branch:
   ```bash
   git push origin main
   ```

2. GitHub Actions pipeline will:
   - Run lint checks
   - Run tests
   - Build Docker image
   - Push image to ECR
   - Update ECS task definition
   - Deploy to Fargate
   - Wait for service stability
   - Output ALB URL

3. Monitor the deployment:
   - Check GitHub Actions tab for build logs
   - View ECS service in AWS Console
   - Check CloudWatch logs: `/ecs/diagnostico-medico-api`

### Manual Deployment

If needed, you can manually trigger an ECS update:

```bash
# Update ECS service to pull latest image
aws ecs update-service \
  --cluster diagnostico-medico-api-cluster \
  --service diagnostico-medico-api-service \
  --force-new-deployment \
  --region us-east-1

# Wait for deployment
aws ecs wait services-stable \
  --cluster diagnostico-medico-api-cluster \
  --services diagnostico-medico-api-service \
  --region us-east-1
```

## Monitoring and Logging

### View Logs

```bash
# Stream logs from CloudWatch
aws logs tail /ecs/diagnostico-medico-api --follow

# View specific container logs
aws logs tail /ecs/diagnostico-medico-api --follow --log-stream-names ecs
```

### Monitor ECS Service

```bash
# Get service details
aws ecs describe-services \
  --cluster diagnostico-medico-api-cluster \
  --services diagnostico-medico-api-service

# Get running tasks
aws ecs list-tasks \
  --cluster diagnostico-medico-api-cluster \
  --service-name diagnostico-medico-api-service
```

### CloudWatch Metrics

Monitor these metrics in CloudWatch:
- `ECS:ServiceCount` - Number of running tasks
- `ALB:RequestCount` - Total requests to API
- `ALB:TargetResponseTime` - Response time
- `ECS:CPUUtilization` - Container CPU usage
- `ECS:MemoryUtilization` - Container memory usage

## Scaling Configuration

Auto scaling is configured with three policies:

1. **CPU Utilization**: Target 70%
2. **Memory Utilization**: Target 80%
3. **ALB Request Count**: Target 1000 requests/target/minute

Modify in `terraform/autoscaling.tf` and update:

```bash
cd terraform
terraform apply
```

## Cost Optimization

To reduce costs:

1. **Use Fargate Spot** (already configured):
   - 70% cheaper than on-demand
   - Good for non-critical workloads

2. **Reduce Task Count**:
   ```hcl
   # In terraform.tfvars
   desired_count = 1
   min_capacity = 1
   ```

3. **Reduce CPU/Memory**:
   ```hcl
   # Minimum viable for Python FastAPI
   container_cpu = 256
   container_memory = 512
   ```

4. **Schedule Scaling**:
   - Scale down during off-hours
   - See `terraform/autoscaling.tf` for scheduled scaling example

## HTTPS/SSL Configuration

To enable HTTPS:

1. Get an SSL certificate from AWS Certificate Manager (ACM)

2. Uncomment the HTTPS listener in `terraform/alb.tf`:
   ```hcl
   resource "aws_lb_listener" "app_https" {
     ...
     certificate_arn = "arn:aws:acm:region:account:certificate/id"
   }
   ```

3. Add HTTP to HTTPS redirect

4. Apply terraform:
   ```bash
   cd terraform
   terraform apply
   ```

## Rollback

If deployment fails:

```bash
# Rollback to previous task definition
aws ecs update-service \
  --cluster diagnostico-medico-api-cluster \
  --service diagnostico-medico-api-service \
  --task-definition diagnostico-medico-api:PREVIOUS_VERSION \
  --region us-east-1
```

## Cleanup

To destroy all AWS resources:

```bash
cd terraform
terraform destroy
```

This will delete:
- ECS cluster, service, and tasks
- ECR repository (if empty)
- ALB and target groups
- VPC and subnets
- NAT gateways and elastic IPs
- CloudWatch log groups
- IAM roles

**Warning**: This action cannot be undone. Ensure you don't have production data before destroying.

## Troubleshooting

### Tasks not starting

```bash
# Check task definition
aws ecs describe-task-definition \
  --task-definition diagnostico-medico-api

# Check service events
aws ecs describe-services \
  --cluster diagnostico-medico-api-cluster \
  --services diagnostico-medico-api-service \
  --query 'services[0].events'
```

### Image not found in ECR

```bash
# List ECR images
aws ecr describe-images \
  --repository-name diagnostico-medico-api \
  --region us-east-1
```

### Application not responding

```bash
# Check ALB health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...

# Check security groups
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=diagnostico-medico-api*"
```

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review ECS task definition and events
3. Verify security groups allow traffic
4. Check IAM permissions
5. Review terraform outputs for resource details

## Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
