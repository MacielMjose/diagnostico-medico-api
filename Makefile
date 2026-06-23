.PHONY: help build push lint test terraform-init terraform-plan terraform-apply terraform-destroy docker-login docker-build docker-run

# Load environment variables (optional — não falha se ausente)
-include .env-example

help:
	@echo "Diagnostico Médico API - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make lint              - Run linter and formatter check"
	@echo "  make test              - Run tests with coverage"
	@echo "  make docker-build      - Build Docker image locally"
	@echo "  make docker-run        - Run Docker image locally"
	@echo ""
	@echo "Docker Registry:"
	@echo "  make docker-login      - Login to AWS ECR"
	@echo "  make docker-push       - Build and push image to ECR"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make terraform-init    - Initialize Terraform"
	@echo "  make terraform-plan    - Plan infrastructure changes"
	@echo "  make terraform-apply   - Apply infrastructure changes"
	@echo "  make terraform-destroy - Destroy all infrastructure"
	@echo "  make terraform-output  - Show Terraform outputs"
	@echo ""

# Development commands
lint:
	pip install -e ".[dev]"
	ruff check .
	ruff format --check .

test:
	pip install -e ".[dev]"
	pytest --cov=app --cov-report=html --cov-report=term-missing

# Docker commands
docker-build:
	docker build -t $(ECR_REPOSITORY):$(DOCKER_IMAGE_TAG) .

docker-run:
	docker run -p 8000:8000 $(ECR_REPOSITORY):$(DOCKER_IMAGE_TAG)

docker-login:
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

docker-push: docker-build docker-login
	docker tag $(ECR_REPOSITORY):$(DOCKER_IMAGE_TAG) \
		$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPOSITORY):$(DOCKER_IMAGE_TAG)
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPOSITORY):$(DOCKER_IMAGE_TAG)

# Terraform commands
terraform-init:
	cd terraform && terraform init

terraform-plan:
	cd terraform && terraform plan -out=tfplan

terraform-apply:
	cd terraform && terraform apply tfplan

terraform-destroy:
	cd terraform && terraform destroy

terraform-output:
	cd terraform && terraform output

# CI/CD simulation (for local testing)
ci-lint: lint
ci-test: test
ci-build: docker-build
ci-full: ci-lint ci-test ci-build

# Deployment
deploy-fargate: docker-push terraform-apply
	@echo "✓ Docker image pushed to ECR"
	@echo "✓ Infrastructure deployed"
	@echo ""
	@echo "Access your application at:"
	@make terraform-output | grep application_url

# Monitoring
logs:
	aws logs tail /ecs/$(ECR_REPOSITORY) --follow

status:
	aws ecs describe-services \
		--cluster $(ECS_CLUSTER) \
		--services $(ECS_SERVICE)

rollback:
	aws ecs update-service \
		--cluster $(ECS_CLUSTER) \
		--service $(ECS_SERVICE) \
		--force-new-deployment

# Clean up
clean:
	rm -rf .coverage htmlcov .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

terraform-clean:
	cd terraform && rm -rf .terraform tfplan
