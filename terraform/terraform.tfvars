# Terraform variables for dev environment
aws_region          = "us-east-1"
app_name            = "diagnostico-medico-api"
environment         = "dev"
container_port      = 8000
container_cpu       = 256
container_memory    = 512
desired_count       = 2
min_capacity        = 2
max_capacity        = 4
enable_nat_gateway  = true
enable_cloudwatch_logs = true
log_retention_days  = 7
image_tag           = "latest"

vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.101.0/24", "10.0.102.0/24"]
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]

tags = {
  Project     = "Diagnostico-Medico"
  ManagedBy   = "Terraform"
  Environment = "dev"
  Owner       = "Platform"
}
