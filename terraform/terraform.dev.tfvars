# Development environment variables
aws_region          = "us-east-1"
app_name            = "diagnostico-medico-api"
environment         = "dev"
container_port      = 8000
container_cpu       = 256
container_memory    = 512
desired_count       = 1
min_capacity        = 1
max_capacity        = 2
enable_nat_gateway  = true
enable_cloudwatch_logs = true
log_retention_days  = 7
image_tag           = "latest"

llm_provider           = "groq"
llm_fallback_providers = ""

openai_model       = "gpt-4o-mini"
anthropic_model    = "claude-haiku-4-5-20251001"
groq_model         = "llama-3.1-8b-instant"
gemini_model       = "gemini-2.0-flash"

vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.101.0/24", "10.0.102.0/24"]
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]

tags = {
  Project     = "Diagnostico-Medico"
  ManagedBy   = "Terraform"
  Environment = "dev"
  Owner       = "Platform"
  CostCenter  = "Engineering"
}
