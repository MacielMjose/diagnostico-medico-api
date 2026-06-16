# Terraform Cloud / HCP Setup Guide

This guide covers setting up Terraform Cloud or self-managed backends for state management.

## Why Use Terraform Cloud?

✅ **Remote State** - State stored securely in cloud, not on your machine  
✅ **Team Collaboration** - Share state with team members  
✅ **Cost Estimation** - See estimated AWS costs before applying  
✅ **VCS Integration** - Auto-run on GitHub push  
✅ **Run History** - View all terraform runs and changes  
✅ **Policy as Code** - Enforce terraform policies  
✅ **State Locking** - Prevent concurrent modifications  

---

## Option 1: Terraform Cloud (Recommended)

### Step 1: Create Account

1. Go to https://app.terraform.io/signup
2. Sign up with email or GitHub
3. Create free account (includes 50 free state storage)

### Step 2: Create Organization

1. After signup, create new organization
2. Name: `diagnostico-medico` (or your org name)
3. Email: your-email@example.com

### Step 3: Create API Token

1. Click your avatar (top right) → Account Settings
2. Go to Tokens
3. Click "Create an API token"
4. Description: "Local CLI Token"
5. Save the token securely

### Step 4: Authenticate Locally

```bash
terraform login

# When prompted for API token, paste your token
# Press Enter
# This creates ~/.terraform.d/credentials.tfrc.json
```

Verify login:
```bash
cat ~/.terraform.d/credentials.tfrc.json
# Should show your token
```

### Step 5: Configure Backend

Edit `terraform/main.tf` and replace `YOUR_ORG_NAME`:

```hcl
terraform {
  cloud {
    organization = "diagnostico-medico"  # Your org name
    
    workspaces {
      name = "diagnostico-medico-api-dev"
    }
  }
}
```

### Step 6: Add AWS Credentials to Cloud

1. Go to Terraform Cloud → Your Organization → Settings
2. Click "Variables"
3. Add environment variables:
   - `AWS_ACCESS_KEY_ID` - your AWS access key
   - `AWS_SECRET_ACCESS_KEY` - your AWS secret key
   - Mark secrets as sensitive (eye icon)

### Step 7: Initialize

```bash
cd terraform
terraform init

# Follow prompts to link workspace
# Select workspace: diagnostico-medico-api-dev
# Type 'yes' to confirm
```

### Step 8: Plan and Apply

```bash
terraform plan
terraform apply
```

Now all runs are tracked in Terraform Cloud!

---

## Option 2: S3 Backend (Self-Managed)

Use this if you prefer not to use Terraform Cloud.

### Step 1: Create S3 Bucket

```bash
aws s3 mb s3://diagnostico-medico-terraform-state-$(date +%s) --region us-east-1

# Save the bucket name
BUCKET_NAME="your-bucket-name"
```

### Step 2: Enable Versioning

```bash
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled
```

### Step 3: Enable Encryption

```bash
aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}
    }]
  }'
```

### Step 4: Create DynamoDB Table (for state locking)

```bash
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1
```

### Step 5: Update Terraform Configuration

Edit `terraform/main.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "diagnostico-medico-terraform-state-1234567890"
    key            = "diagnostico-medico-api/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

Replace `bucket` with your actual bucket name.

### Step 6: Initialize

```bash
cd terraform
terraform init

# Type 'yes' to confirm backend migration
```

### Step 7: Apply

```bash
terraform plan
terraform apply
```

---

## Option 3: VCS-Driven Workflow (Terraform Cloud + GitHub)

Automatically run Terraform when you push to GitHub.

### Step 1: Complete Terraform Cloud Setup (Option 1)

Follow steps 1-7 above.

### Step 2: Create GitHub OAuth Application

1. Go to Terraform Cloud → Settings → VCS Providers
2. Click "GitHub" 
3. Click "Connect to GitHub"
4. Authorize Terraform Cloud

### Step 3: Connect Repository

1. In Terraform Cloud, go to Workspaces
2. Click your workspace: `diagnostico-medico-api-dev`
3. Go to Settings → VCS
4. Click "Connect to a VCS repository"
5. Select `your-github-org/diagnostico-medico-api`

### Step 4: Configure Workspace

In workspace settings:
- **Auto apply**: OFF (for safety, review first)
- **Terraform version**: Latest
- **Working directory**: `terraform`

### Step 5: Test

```bash
# Make a change
cd terraform
echo "# test" >> main.tf

# Push to GitHub
git add terraform/main.tf
git commit -m "test: trigger terraform cloud"
git push origin main
```

You'll see:
- GitHub shows pending Terraform check
- Terraform Cloud shows "queued" run
- Results appear in PR comments

### Step 6: Update CI/CD Pipeline

Update `.github/workflows/pipeline.yml` to skip terraform apply (let Terraform Cloud handle it):

```yaml
deploy-fargate:
  name: Deploy to ECS Fargate
  # Remove manual terraform apply
  # Let Terraform Cloud handle it
  steps:
    - name: Terraform Cloud Check
      run: |
        echo "Terraform Cloud will auto-apply changes"
        echo "Check run status at: https://app.terraform.io"
```

---

## Workspace Management

### Create Multiple Workspaces

```bash
# For staging environment
terraform workspace new diagnostico-medico-api-staging

# For production
terraform workspace new diagnostico-medico-api-prod

# List workspaces
terraform workspace list

# Switch workspace
terraform workspace select diagnostico-medico-api-prod
```

Use different `terraform.prod.tfvars` for each:

```bash
terraform plan -var-file=terraform.prod.tfvars
```

---

## View Terraform Cloud

### Check Runs
```bash
# In browser: https://app.terraform.io
# Organization → Workspaces → Your Workspace → Runs
```

### Access Terraform State
```bash
# Download state
terraform state pull > state.json

# View specific resource
terraform state show aws_ecs_service.app
```

### Workspace Variables

Set variables in Terraform Cloud instead of terraform.tfvars:

1. Go to Workspace → Variables
2. Add variables:
   - `container_cpu` = "256"
   - `container_memory` = "512"
   - `desired_count` = "2"

---

## Migrate State

### From Local to Terraform Cloud

```bash
# Current state: local (terraform.tfstate)
# Target: Terraform Cloud

# 1. Add cloud block to main.tf
# 2. Run init (confirm migration)
terraform init

# It will ask: Copy state to new backend?
# Type: yes

# Verify state moved
terraform state list
```

### From S3 to Terraform Cloud

```bash
# 1. Current backend is S3
# 2. Update main.tf cloud block
# 3. Run init
terraform init

# Type: yes to migrate
terraform state list
```

---

## Best Practices

### 1. Protect Sensitive Data
```hcl
# Mark as sensitive in Terraform Cloud
sensitive = true
```

### 2. Use Version Control
```bash
# Always commit state configuration changes
git add terraform/main.tf
git commit -m "Configure Terraform Cloud backend"
git push
```

### 3. Set Up RBAC
In Terraform Cloud:
- Organization → Settings → Teams
- Create teams: admins, developers, viewers
- Assign workspace access

### 4. Enable Notifications
```bash
# Terraform Cloud → Workspace → Notifications
# Slack, email, webhooks
```

### 5. Cost Estimation

Enable in workspace:
1. Workspace → Settings → Cost estimation
2. Toggle ON
3. See estimated costs in PR comments

### 6. Enforce Policies

Create sentinel policies:
```hcl
# Require tags
main = rule {
  all_resources as r {
    r.change.after.tags is not empty
  }
}
```

---

## Troubleshooting

### "Error loading state"
```bash
# Check credentials
terraform login

# Verify token in ~/.terraform.d/credentials.tfrc.json
cat ~/.terraform.d/credentials.tfrc.json
```

### "Workspace not found"
```bash
# Create workspace in Terraform Cloud first, or:
terraform workspace new diagnostico-medico-api-dev
```

### "Access denied to S3"
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify bucket exists
aws s3 ls s3://your-bucket-name
```

### State locked
```bash
# Force unlock (DANGEROUS - only if certain)
terraform force-unlock LOCK_ID
```

---

## Cleanup

### Delete Terraform Cloud Workspace
1. Workspace → Settings → Danger Zone
2. "Delete from Cloud"
3. Confirm

### Delete S3 Backend
```bash
# Empty bucket first
aws s3 rm s3://$BUCKET_NAME --recursive

# Delete bucket
aws s3 rb s3://$BUCKET_NAME

# Delete DynamoDB table
aws dynamodb delete-table --table-name terraform-locks
```

---

## Recommended Setup Path

1. **Start**: Option 1 (Terraform Cloud) - simplest for teams
2. **Team Scale**: Add VCS integration (Option 3)
3. **Multi-env**: Create separate workspaces for dev/staging/prod

---

## Resources

- [Terraform Cloud Docs](https://developer.hashicorp.com/terraform/cloud-docs)
- [AWS S3 Backend](https://developer.hashicorp.com/terraform/language/settings/backends/s3)
- [State Management](https://developer.hashicorp.com/terraform/language/state)
- [Sentinel Policies](https://developer.hashicorp.com/sentinel)

---

**Next Step**: Choose your backend option and update `terraform/main.tf`!
