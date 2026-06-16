# Production environment variables
aws_region          = "us-east-1"
app_name            = "diagnostico-medico-api"
environment         = "prod"
container_port      = 8000
container_cpu       = 512
container_memory    = 1024
desired_count       = 3
min_capacity        = 3
max_capacity        = 10
enable_nat_gateway  = true
enable_cloudwatch_logs = true
log_retention_days  = 30
image_tag           = "latest"

vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.101.0/24", "10.0.102.0/24"]
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]

tags = {
  Project     = "Diagnostico-Medico"
  ManagedBy   = "Terraform"
  Environment = "prod"
  Owner       = "Platform"
  CostCenter  = "Operations"
}
