# AWS Fargate Setup - Complete Summary

This document provides a complete overview of the Fargate setup and how to use all the newly created files.

## What Was Created

### 1. Docker Configuration

#### `Dockerfile`
- Multi-stage build for optimized image size
- Python 3.11 slim base image
- Health check endpoint at `/health`
- Port 8000 exposed

#### `.dockerignore`
- Excludes unnecessary files from Docker build context
- Reduces image size

### 2. Terraform Infrastructure Files

#### Core Files
- **`terraform/main.tf`** - VPC, subnets, NAT gateways, internet gateway, security groups
- **`terraform/ecr.tf`** - ECR repository with lifecycle policies
- **`terraform/ecs.tf`** - ECS cluster, task definition, service, CloudWatch logs, IAM roles
- **`terraform/alb.tf`** - Application Load Balancer and target groups
- **`terraform/autoscaling.tf`** - Auto scaling policies based on CPU, memory, and requests
- **`terraform/variables.tf`** - All input variables with defaults
- **`terraform/outputs.tf`** - Key outputs (ALB URL, ECR repository, etc.)

#### Environment-Specific Files
- **`terraform/terraform.tfvars`** - Default dev configuration
- **`terraform/terraform.dev.tfvars`** - Development environment overrides
- **`terraform/terraform.prod.tfvars`** - Production environment overrides

### 3. CI/CD Pipeline

#### `.github/workflows/pipeline.yml`
Updated to include:
1. **Lint stage** - Code style checks with Ruff
2. **Test stage** - Unit tests with coverage reports
3. **Build-image stage** - Docker image build
4. **Push-ecr stage** - Push image to Amazon ECR
5. **Deploy-fargate stage** - Automatic deployment to ECS Fargate (main branch only)

Features:
- Uses AWS OIDC for secure authentication (no access keys stored)
- Multi-stage pipeline with dependencies
- Only deploys on main branch
- Waits for service stability before completion

### 4. Utility Files

#### `Makefile`
Convenient commands for common tasks:
```bash
make help              # Show all available commands
make lint              # Run linters
make test              # Run tests
make docker-build      # Build Docker image
make docker-run        # Run Docker locally
make docker-login      # Login to ECR
make docker-push       # Build and push to ECR
make terraform-init    # Initialize Terraform
make terraform-plan    # Plan infrastructure
make terraform-apply   # Deploy infrastructure
make terraform-destroy # Destroy infrastructure
make logs              # View CloudWatch logs
make status            # Check service status
```

#### `.env.example`
Template for environment variables. Copy to `.env` and fill in your values:
```bash
cp .env.example .env
```

#### `DEPLOYMENT.md`
Comprehensive deployment guide covering:
- Architecture overview
- Prerequisites
- Setup instructions
- Docker management
- GitHub Actions configuration
- Deployment process
- Monitoring and logging
- Troubleshooting
- Cost optimization
- HTTPS setup

## Quick Start Guide

### Step 1: Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region: us-east-1
# Enter default output format: json
```

### Step 2: Initialize Terraform

```bash
cd terraform
terraform init
```

### Step 3: Plan Infrastructure

```bash
terraform plan -out=tfplan
```

### Step 4: Deploy Infrastructure

```bash
terraform apply tfplan
```

This creates the entire AWS infrastructure:
- VPC with public and private subnets
- ECR repository for Docker images
- ECS Fargate cluster with auto-scaling
- Application Load Balancer
- CloudWatch logs
- All necessary IAM roles

### Step 5: Get Outputs

```bash
terraform output
```

Save important values:
- `ecr_repository_url` - For pushing Docker images
- `application_url` - Public URL to access your API
- `ecs_cluster_name` - For manual deployments

### Step 6: Setup GitHub Actions (Optional)

If using GitHub Actions for CI/CD:

1. Create AWS OIDC provider (see DEPLOYMENT.md for commands)
2. Create IAM role for GitHub Actions
3. Add `AWS_ROLE_TO_ASSUME` secret to GitHub repository
4. Push code to trigger automatic deployment

## Environment Switching

### Deploy to Dev Environment

```bash
cd terraform
terraform apply -var-file="terraform.dev.tfvars"
```

### Deploy to Prod Environment

```bash
cd terraform
terraform apply -var-file="terraform.prod.tfvars"
```

Each environment has separate:
- Task count and scaling limits
- CPU and memory allocation
- Log retention periods
- Resource tags

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    AWS Account                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │              VPC (10.0.0.0/16)               │   │
│  │                                              │   │
│  │  ┌────────────────────────────────────────┐ │   │
│  │  │     Public Subnets (x2)                │ │   │
│  │  │                                        │ │   │
│  │  │  ┌─────────────────────────────────┐  │ │   │
│  │  │  │  Application Load Balancer      │  │ │   │
│  │  │  │  (Listens on port 80/443)       │  │ │   │
│  │  │  │  - Health Check: /health        │  │ │   │
│  │  │  │  - Target Group: ECS Tasks      │  │ │   │
│  │  │  └─────────────────────────────────┘  │ │   │
│  │  │           │                           │ │   │
│  │  │  ┌────────┴─────────┐                 │ │   │
│  │  │  │   NAT Gateways   │                 │ │   │
│  │  │  │   (for outbound)  │                 │ │   │
│  │  │  └────────┬─────────┘                 │ │   │
│  │  └────────────────────────────────────────┘ │   │
│  │                    │                         │   │
│  │  ┌────────────────┴────────────────────┐   │   │
│  │  │   Private Subnets (x2)              │   │   │
│  │  │                                     │   │   │
│  │  │  ┌────────────────────────────┐    │   │   │
│  │  │  │  ECS Fargate Tasks (x2+)   │    │   │   │
│  │  │  │                            │    │   │   │
│  │  │  │  ┌──────────────────────┐  │    │   │   │
│  │  │  │  │  FastAPI Container   │  │    │   │   │
│  │  │  │  │  (Port 8000)          │  │    │   │   │
│  │  │  │  │  - Auto Scaling       │  │    │   │   │
│  │  │  │  │  - Health Checks      │  │    │   │   │
│  │  │  │  └──────────────────────┘  │    │   │   │
│  │  │  └────────────────────────────┘    │   │   │
│  │  │                                     │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  ECR Repository                              │   │
│  │  (Docker Image Storage)                      │   │
│  │  - Image Scanning enabled                    │   │
│  │  - Lifecycle policies (keep last 5)          │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  CloudWatch                                  │   │
│  │  - Log Group: /ecs/diagnostico-medico-api    │   │
│  │  - Metrics: CPU, Memory, Requests            │   │
│  │  - Alarms: (optional)                        │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Data Flow

```
1. User Request
   ↓
2. Application Load Balancer (port 80/443)
   ↓
3. Health Check → /health endpoint (every 30 seconds)
   ↓
4. Route to Healthy ECS Task(s)
   ↓
5. FastAPI Container (port 8000)
   ↓
6. Response returned to user
   ↓
7. Logs sent to CloudWatch
   ↓
8. Metrics collected for auto-scaling
```

## Auto Scaling Behavior

The service automatically scales based on three metrics:

1. **CPU Utilization**: Target 70%
   - If > 70% → Add tasks
   - If < 70% → Remove tasks

2. **Memory Utilization**: Target 80%
   - If > 80% → Add tasks
   - If < 80% → Remove tasks

3. **ALB Request Count**: Target 1000 requests/target/minute
   - If > 1000 → Add tasks
   - If < 1000 → Remove tasks

Scaling limits:
- **Dev**: 1-2 tasks
- **Prod**: 3-10 tasks

## Common Tasks

### Deploy Application

```bash
# Automatic (via GitHub push)
git push origin main

# Manual
make docker-push
make terraform-apply
```

### Update Application

```bash
# Make code changes
git add .
git commit -m "Update API"
git push origin main  # Triggers automatic deployment
```

### View Logs

```bash
make logs
# or
aws logs tail /ecs/diagnostico-medico-api --follow
```

### Check Status

```bash
make status
# or
aws ecs describe-services \
  --cluster diagnostico-medico-api-cluster \
  --services diagnostico-medico-api-service
```

### Scale Service

Edit `terraform/terraform.tfvars`:
```hcl
desired_count = 5  # Change number of tasks
max_capacity = 10  # Change max scaling limit
```

Then apply:
```bash
cd terraform
terraform apply
```

### Destroy Infrastructure

```bash
cd terraform
terraform destroy
# Type 'yes' to confirm
```

## Security Considerations

1. **Network Isolation**
   - Application runs in private subnets
   - Only ALB has public access
   - Security groups restrict traffic

2. **Authentication**
   - GitHub Actions uses OIDC (no hardcoded credentials)
   - IAM roles with least privilege

3. **Image Security**
   - ECR image scanning enabled
   - Only last 5 images kept in registry

4. **Secrets Management**
   - Use AWS Secrets Manager for sensitive data
   - Don't commit secrets to Git

5. **HTTPS/SSL**
   - Setup instructions in DEPLOYMENT.md
   - Use AWS Certificate Manager (ACM)

## Cost Estimation (Monthly)

### Dev Environment
- ECS Fargate (1 task, 256 CPU, 512 MB): ~$5
- ALB: ~$15
- ECR: ~$0.50
- NAT Gateway: ~$30
- **Total**: ~$50/month

### Prod Environment
- ECS Fargate (3+ tasks, 512 CPU, 1 GB): ~$50
- ALB: ~$15
- ECR: ~$2
- NAT Gateways (x2): ~$60
- **Total**: ~$130/month

Use Fargate Spot instances to reduce by 70%.

## Next Steps

1. **Configure AWS Credentials** - `aws configure`
2. **Initialize Terraform** - `cd terraform && terraform init`
3. **Deploy Infrastructure** - `terraform apply`
4. **Setup GitHub Actions** - Create OIDC provider (see DEPLOYMENT.md)
5. **Push Code** - Git push triggers automatic deployment
6. **Monitor** - View logs and metrics in CloudWatch

## Support Files

- **DEPLOYMENT.md** - Detailed deployment instructions
- **Dockerfile** - Container configuration
- **.dockerignore** - Docker build optimization
- **Makefile** - Common commands
- **.env.example** - Environment variables template
- **terraform/*** - All infrastructure code

## File Structure

```
diagnostico-medico-api/
├── .github/workflows/
│   └── pipeline.yml              # CI/CD pipeline
├── terraform/
│   ├── main.tf                   # VPC & networking
│   ├── ecr.tf                    # Container registry
│   ├── ecs.tf                    # ECS cluster & service
│   ├── alb.tf                    # Load balancer
│   ├── autoscaling.tf            # Auto scaling
│   ├── variables.tf              # Input variables
│   ├── outputs.tf                # Output values
│   ├── terraform.tfvars          # Default config
│   ├── terraform.dev.tfvars      # Dev config
│   └── terraform.prod.tfvars     # Prod config
├── src/
│   └── minha_api/
│       ├── main.py               # FastAPI app
│       └── __init__.py
├── tests/
│   └── test_main.py
├── Dockerfile                    # Container image
├── .dockerignore                 # Docker build filter
├── .gitignore                    # Git ignores
├── .env.example                  # Environment template
├── Makefile                      # Convenience commands
├── pyproject.toml               # Python project config
├── DEPLOYMENT.md                # Deployment guide
└── SETUP.md                     # This file
```

---

Ready to deploy! Start with `aws configure` and then `cd terraform && terraform init`.
