# DigitalOcean Infrastructure Manager - Terraform Configuration
#
# This is the main entry point for Terraform.
# Use `dom export terraform` to generate resource definitions from existing infrastructure.

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }

  # Uncomment to use remote state (recommended for teams)
  # backend "s3" {
  #   endpoint                    = "fra1.digitaloceanspaces.com"
  #   bucket                      = "your-terraform-state-bucket"
  #   key                         = "terraform.tfstate"
  #   region                      = "us-east-1"  # Required but ignored by DO Spaces
  #   skip_credentials_validation = true
  #   skip_metadata_api_check     = true
  # }
}

provider "digitalocean" {
  token = var.do_token
}
