# Quick Start - Fargate Deployment

## 5-Minute Setup

### 1. Install Prerequisites
```bash
# Install AWS CLI
# Install Terraform: https://www.terraform.io/downloads
# Install Docker (for testing locally)
```

### 2. Configure AWS
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Default region: us-east-1
# Default output format: json
```

### 3. Setup Terraform Backend (Choose One)

**Option A: Terraform Cloud (Recommended)**
```bash
# 1. Sign up: https://app.terraform.io/signup
# 2. Create organization: diagnostico-medico
# 3. Create API token and save it
# 4. Run: terraform login (paste token)
# 5. See TERRAFORM_CLOUD_QUICK.md for 5-min setup
```

**Option B: Local State (Quick Start)**
```bash
# No setup needed, uses terraform.tfstate file locally
# Not recommended for team collaboration
```

**Option C: S3 Backend (Self-Managed)**
```bash
# See TERRAFORM_CLOUD.md → Option 2 for detailed setup
```

### 4. Deploy Infrastructure
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 5. Get Application URL
```bash
terraform output application_url
```

**Your API is now live!** 🎉

---

## Common Commands

### Development
```bash
make lint              # Check code style
make test              # Run tests
make docker-build      # Build image locally
make docker-run        # Run locally on port 8000
```

### Deployment
```bash
make docker-push       # Push to ECR
make terraform-apply   # Deploy infrastructure
make logs              # View application logs
make status            # Check service status
```

### Monitoring
```bash
# View logs
aws logs tail /ecs/diagnostico-medico-api --follow

# Check running tasks
aws ecs list-tasks --cluster diagnostico-medico-api-cluster

# Get service details
aws ecs describe-services --cluster diagnostico-medico-api-cluster --services diagnostico-medico-api-service

# View metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=diagnostico-medico-api-service Name=ClusterName,Value=diagnostico-medico-api-cluster \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

### Cleanup
```bash
cd terraform
terraform destroy
# Type 'yes' to confirm
```

---

## GitHub Actions CI/CD

### Setup (One-time)
```bash
# 1. Create OIDC provider in AWS (see DEPLOYMENT.md)
# 2. Create GitHub Actions IAM role
# 3. Add AWS_ROLE_TO_ASSUME secret to GitHub repository
```

### Deploy (Automatic)
```bash
git push origin main
# Pipeline automatically runs and deploys
```

---

## Test the API

```bash
# Get ALB URL
ALB_URL=$(aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?contains(LoadBalancerName, 'diagnostico-medico-api')].DNSName" \
  --output text)

# Test health endpoint
curl http://$ALB_URL/health

# View API documentation
curl http://$ALB_URL/swagger
```

---

## Troubleshooting

### Tasks not starting?
```bash
# Check logs
aws logs tail /ecs/diagnostico-medico-api

# Check service events
aws ecs describe-services --cluster diagnostico-medico-api-cluster --services diagnostico-medico-api-service --query 'services[0].events'
```

### Can't access ALB?
```bash
# Check security groups
aws ec2 describe-security-groups --filters "Name=group-name,Values=diagnostico-medico-api*"

# Check target health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
```

### Terraform errors?
```bash
# Validate configuration
cd terraform
terraform validate

# Check state
terraform show

# Import state if needed
terraform import aws_ecr_repository.app diagnostico-medico-api
```

---

## Scaling

### Change task count
Edit `terraform/terraform.tfvars`:
```hcl
desired_count = 5  # Change this
```

Apply changes:
```bash
cd terraform
terraform apply
```

### Change CPU/Memory
Edit `terraform/terraform.tfvars`:
```hcl
container_cpu = 512    # 256, 512, 1024, 2048, 4096
container_memory = 1024  # Must match CPU
```

Available combinations:
- 256 CPU: 512, 1024, 2048 MB
- 512 CPU: 1024, 2048, 3072, 4096 MB
- 1024 CPU: 2048-8192 MB (1 GB increments)
- etc.

---

## Cost Saving Tips

1. **Use Fargate Spot** (70% cheaper)
   - Already configured
   - Good for non-critical workloads

2. **Reduce resources in dev**
   ```hcl
   container_cpu = 256
   container_memory = 512
   desired_count = 1
   ```

3. **Schedule scaling** (off-hours)
   - Scale down at night
   - Scale up during business hours

---

## Documentation

- **SETUP.md** - Complete setup guide with architecture
- **DEPLOYMENT.md** - Detailed deployment and troubleshooting
- **QUICK_START.md** - This file (quick reference)

---

## API Endpoints

After deployment, your API is accessible at:
```
http://<ALB-DNS-NAME>/
http://<ALB-DNS-NAME>/health
http://<ALB-DNS-NAME>/swagger
```

Example:
```bash
curl http://my-app-alb-123456789.us-east-1.elb.amazonaws.com/health
# Response: {"status":"healthy"}
```

---

## Next Steps

1. ✅ Run `aws configure`
2. ✅ Run `terraform init && terraform apply`
3. ✅ Get your ALB URL
4. ✅ Test the API
5. ✅ Setup GitHub Actions (optional)
6. ✅ Monitor with CloudWatch

---

**Questions?** Check DEPLOYMENT.md for detailed documentation.
