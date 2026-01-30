.PHONY: help install dev audit status costs cleanup export-tf export-ansible terraform-init terraform-plan terraform-apply lint test

# Default target
help:
	@echo "DigitalOcean Infrastructure Manager"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install the CLI tool"
	@echo "  make dev            Install in development mode"
	@echo ""
	@echo "CLI Commands (requires DIGITALOCEAN_TOKEN):"
	@echo "  make status         Quick account status"
	@echo "  make audit          Audit all resources"
	@echo "  make costs          Show cost estimates"
	@echo "  make cleanup        Find orphaned resources"
	@echo "  make export-tf      Export to Terraform"
	@echo "  make export-ansible Export to Ansible inventory"
	@echo ""
	@echo "Terraform:"
	@echo "  make terraform-init   Initialize Terraform"
	@echo "  make terraform-plan   Show planned changes"
	@echo "  make terraform-apply  Apply changes"
	@echo ""
	@echo "Development:"
	@echo "  make lint           Run linter"
	@echo "  make test           Run tests"

# Setup
install:
	pip install .

dev:
	pip install -e ".[dev]"

# CLI shortcuts
status:
	dom status

audit:
	dom audit all

costs:
	dom costs estimate

cleanup:
	dom cleanup all --dry-run

export-tf:
	dom export terraform --output ./generated/terraform

export-ansible:
	dom export ansible --output ./generated/ansible

# Terraform
terraform-init:
	cd terraform && terraform init

terraform-plan:
	cd terraform && terraform plan

terraform-apply:
	cd terraform && terraform apply

# Development
lint:
	ruff check dom/
	mypy dom/

test:
	pytest tests/ -v

# Clean generated files
clean:
	rm -rf generated/
	rm -rf __pycache__ .pytest_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
