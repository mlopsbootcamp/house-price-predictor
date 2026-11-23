terraform {
  required_version = ">= 1.10.0"

  backend "s3" {
    key          = "house-price-predictor/terraform.tfstate"
    profile      = "kthw-provisioner"
    encrypt      = true
    use_lockfile = true
  }
  required_providers {
    external = {
      source  = "hashicorp/external"
      version = "~> 2.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region              = local.aws_region
  allowed_account_ids = var.aws_account_id == null ? null : [var.aws_account_id]
}

data "external" "aws_region" {
  program = ["python3", "${path.module}/scripts/aws-region.py"]
}

locals {
  aws_region = var.aws_region != null ? var.aws_region : data.external.aws_region.result.region
}

data "aws_caller_identity" "current" {}

# Pass an existing provider ARN when the account already trusts GitHub.
resource "aws_iam_openid_connect_provider" "github" {
  count          = var.github_oidc_provider_arn == "" ? 1 : 0
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

output "aws_region" { value = local.aws_region }

output "aws_account_id" { value = data.aws_caller_identity.current.account_id }
