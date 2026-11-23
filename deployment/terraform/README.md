# AWS state for legacy deployment access

Argo CD now deploys the application from Git. The GitHub workflow needs Docker
Hub publishing credentials and its GitHub token. See the
[Kubernetes deployment guide](../kubernetes/README.md#kubernetes-the-hard-way-gitops-deployment).

This Terraform root retains the AWS account's GitHub OIDC provider when it
owns that provider. For existing state, applying the GitOps migration removes
the dedicated legacy role, its inline policy, and its SSM tunnel document.
Review the plan against the existing backend before applying.

```sh
export AWS_CONFIG_FILE="$(realpath ../kubernetes-the-hard-way/infrastructure/terraform/project.awsconfig)"
export AWS_PROFILE=kthw-bootstrap
terraform -chdir=deployment/terraform init \
  -backend-config=../../../kubernetes-the-hard-way/infrastructure/terraform/lab.s3.tfbackend
terraform -chdir=deployment/terraform plan
```

The backend uses the Kubernetes The Hard Way state bucket and the
`kthw-provisioner` profile. Preserve the existing provider ARN setting if
the GitHub OIDC provider is managed by another Terraform state.
