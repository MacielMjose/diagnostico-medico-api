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

llm_provider           = "groq"
llm_fallback_providers = "openai,gemini"

openai_model       = "gpt-4o-mini"
anthropic_model    = "claude-haiku-4-5-20251001"
groq_model         = "llama-3.1-8b-instant"
gemini_model       = "gemini-2.0-flash"

vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.101.0/24", "10.0.102.0/24"]
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]

secrets_to_create = {
  "posthog_api_key" = {
    description        = "PostHog API Key for analytics"
    container_env_name = "POSTHOG_API_KEY"
  }
  "groq_api_key" = {
    description        = "Groq API Key for LLM inference"
    container_env_name = "GROQ_API_KEY"
  }
  "openai_api_key" = {
    description        = "OpenAI API Key for LLM inference"
    container_env_name = "OPENAI_API_KEY"
  }
  "gemini_api_key" = {
    description        = "Gemini API Key for LLM inference"
    container_env_name = "GEMINI_API_KEY"
  }
}

tags = {
  Project     = "Diagnostico-Medico"
  ManagedBy   = "Terraform"
  Environment = "prod"
  Owner       = "Platform"
  CostCenter  = "Operations"
}
