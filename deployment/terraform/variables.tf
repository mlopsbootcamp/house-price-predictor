variable "aws_region" {
  description = "Optional override for the AWS region"
  type        = string
  default     = null
}
variable "aws_account_id" {
  description = "Optional account ID guard for the AWS provider"
  type        = string
  default     = null
}
variable "github_oidc_provider_arn" {
  type    = string
  default = ""
}
