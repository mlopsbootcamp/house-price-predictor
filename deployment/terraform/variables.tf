variable "aws_region" {
  description = "Optional override for the AWS region"
  type = string
  default = null
}
variable "aws_account_id" {
  description = "Optional account ID guard for the AWS provider"
  type = string
  default = null
}
variable "github_oidc_provider_arn" {
  type = string
  default = ""
}
variable "github_oidc_subject" {
  description = "Exact GitHub Actions OIDC subject allowed to assume the deployment role"
  type = string
  default = "repo:cakesmith@4943196/house-price-predictor@1451739636:environment:kthw-lab"
}
