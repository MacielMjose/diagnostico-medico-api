variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "diagnostico-medico-api"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

variable "container_cpu" {
  description = "CPU units for Fargate task (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Memory (MB) for Fargate task"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Number of tasks to run"
  type        = number
  default     = 2
}

variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 4
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "enable_cloudwatch_logs" {
  description = "Enable CloudWatch logs for ECS"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

variable "llm_provider" {
  description = "Primary LLM provider. Valid values: openai, anthropic, groq, gemini."
  type        = string
  default     = "groq"

  validation {
    condition     = contains(["openai", "anthropic", "groq", "gemini"], lower(var.llm_provider))
    error_message = "llm_provider must be one of: openai, anthropic, groq, gemini."
  }
}

variable "llm_fallback_providers" {
  description = "Comma-separated fallback LLM providers tried after llm_provider, for example: openai,gemini."
  type        = string
  default     = "groq,gemini"

  validation {
    condition = alltrue([
      for provider in compact([
        for provider in split(",", var.llm_fallback_providers) : trimspace(lower(provider))
      ]) : contains(["openai", "anthropic", "groq", "gemini"], provider)
    ])
    error_message = "llm_fallback_providers must contain only: openai, anthropic, groq, gemini."
  }
}

variable "openai_model" {
  description = "OpenAI model used when openai is selected as primary or fallback provider."
  type        = string
  default     = "gpt-4o-mini"
}

variable "anthropic_model" {
  description = "Anthropic model used when anthropic is selected as primary or fallback provider."
  type        = string
  default     = "claude-haiku-4-5-20251001"
}

variable "groq_model" {
  description = "Groq model used when groq is selected as primary or fallback provider."
  type        = string
  default     = "llama-3.1-8b-instant"
}

variable "gemini_model" {
  description = "Gemini model used when gemini is selected as primary or fallback provider."
  type        = string
  default     = "gemini-2.5-flash"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "Diagnostico-Medico"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}

variable "secrets_to_create" {
  description = "Map of secrets to create in AWS Secrets Manager. Values must be set manually in AWS Console."
  type = map(object({
    description          = string
    container_env_name   = string
  }))
  default = {
    "posthog_api_key" = {
      description        = "PostHog API Key for analytics"
      container_env_name = "POSTHOG_API_KEY"
    }
    "groq_api_key" = {
      description        = "Groq API Key for LLM inference"
      container_env_name = "GROQ_API_KEY"
    }
  }
}
