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
      source = "hashicorp/external"
      version = "~> 2.0"
    }
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = local.aws_region
  allowed_account_ids = var.aws_account_id == null ? null : [var.aws_account_id]
}

data "external" "aws_region" {
  program = ["python3", "${path.module}/scripts/aws-region.py"]
}

locals {
  aws_region = var.aws_region != null ? var.aws_region : data.external.aws_region.result.region
}

data "aws_partition" "current" {}
data "aws_caller_identity" "current" {}

# Pass an existing provider ARN when the account already trusts GitHub.
resource "aws_iam_openid_connect_provider" "github" {
  count = var.github_oidc_provider_arn == "" ? 1 : 0
  url = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

resource "aws_ssm_document" "kubernetes_tunnel" {
  name = "house-price-kubernetes-api"
  document_type = "Session"
  document_format = "JSON"
  content = jsonencode({
    schemaVersion = "1.0"
    description = "Forward to the Kubernetes API"
    sessionType = "Port"
    properties = {
      host = "server.kubernetes.local"
      portNumber = "6443"
      localPortNumber = "16443"
      type = "LocalPortForwarding"
    }
  })
}

resource "aws_iam_role" "deploy" {
  name = "house-price-github-deploy"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Federated = var.github_oidc_provider_arn != "" ? var.github_oidc_provider_arn : aws_iam_openid_connect_provider.github[0].arn }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = { StringEquals = {
        "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        "token.actions.githubusercontent.com:sub" = var.github_oidc_subject
      } }
    }]
  })
}

resource "aws_iam_role_policy" "deploy" {
  role = aws_iam_role.deploy.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = "ec2:DescribeInstances", Resource = "*" },
      { Effect = "Allow", Action = "ssm:StartSession", Resource = "arn:${data.aws_partition.current.partition}:ec2:${local.aws_region}:${data.aws_caller_identity.current.account_id}:instance/*", Condition = { StringEquals = { "ssm:resourceTag/Name" = "jumpbox", "ssm:resourceTag/ManagedBy" = "kubernetes-hard-way" }, BoolIfExists = { "ssm:SessionDocumentAccessCheck" = "true" } } },
      { Effect = "Allow", Action = "ssm:StartSession", Resource = aws_ssm_document.kubernetes_tunnel.arn },
      { Effect = "Allow", Action = ["ssmmessages:OpenDataChannel", "ssm:TerminateSession"], Resource = "arn:${data.aws_partition.current.partition}:ssm:${local.aws_region}:${data.aws_caller_identity.current.account_id}:session/$${aws:userid}-*" }
    ]
  })
}

output "deploy_role_arn" { value = aws_iam_role.deploy.arn }
output "session_document" { value = aws_ssm_document.kubernetes_tunnel.name }
output "aws_region" { value = local.aws_region }

output "aws_account_id" { value = data.aws_caller_identity.current.account_id }
