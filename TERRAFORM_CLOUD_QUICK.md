# Terraform Cloud - Quick Setup (5 minutes)

## 1. Create Account
```
https://app.terraform.io/signup
→ Sign up with GitHub
→ Create organization: diagnostico-medico
```

## 2. Get API Token
```
Settings → Tokens → Create API token
Copy the token
```

## 3. Login Locally
```bash
terraform login
# Paste token when prompted
```

## 4. Update Backend

Edit `terraform/main.tf` - replace line 11:

**From:**
```hcl
  # Uncomment to use S3 backend
  # backend "s3" {
```

**To:**
```hcl
  cloud {
    organization = "diagnostico-medico"
    
    workspaces {
      name = "diagnostico-medico-api-dev"
    }
  }
```

## 5. Deploy
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**Done!** Your state is now in Terraform Cloud.

---

## Verify

Check Terraform Cloud dashboard:
- https://app.terraform.io → Your Organization → Workspaces
- See all your runs and state history

---

## Common Commands

```bash
# View state in cloud
terraform state list

# See cost estimate
terraform plan  # Shows cost in output

# View runs in browser
# https://app.terraform.io/app/YOUR_ORG/workspaces/diagnostico-medico-api-dev

# Add AWS credentials to cloud
# Terraform Cloud UI → Workspace Variables
# AWS_ACCESS_KEY_ID (sensitive)
# AWS_SECRET_ACCESS_KEY (sensitive)
```

---

**That's it!** Remote state, team collaboration, and cost estimation ready to go.
