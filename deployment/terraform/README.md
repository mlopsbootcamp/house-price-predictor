# GitHub Actions deployment access

This Terraform root creates a GitHub OIDC role and a fixed-destination Systems Manager tunnel for the Kubernetes the Hard Way AWS lab. Apply it using credentials with IAM and SSM administration in the project account. State uses the Kubernetes the Hard Way S3 bucket under a separate key, with S3 locking. Terraform 1.10 or later is required.

The existing lab checkout stores its AWS profiles in a separate config file. Select it before running Terraform, and verify that the bootstrap profile assumes a role in the project account:

```sh
export AWS_CONFIG_FILE="../kubernetes-the-hard-way/infrastructure/terraform/project.awsconfig"
aws --profile kthw-bootstrap sts get-caller-identity
```

Use the path to your own lab checkout if it differs. Clear exported AWS credentials before selecting the profile below so Terraform uses the same profile as the AWS CLI. If `AWS_CONFIG_FILE` is already set to the file containing `kthw-bootstrap`, retain that value. Confirm the caller is the intended project account. Terraform discovers the account ID from the caller.

The lab bootstrap policy grants the provisioner role read, write, and delete access to all objects in the shared state bucket, including state and lock files for future projects. Apply that policy change first from the Hard Way checkout:

```sh
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_SECURITY_TOKEN AWS_CREDENTIAL_EXPIRATION
export AWS_PROFILE=kthw-bootstrap
terraform -chdir=../kubernetes-the-hard-way/infrastructure/terraform/state-bucket plan -out=house-price-state.tfplan
terraform -chdir=../kubernetes-the-hard-way/infrastructure/terraform/state-bucket apply house-price-state.tfplan
```

Review the plan before applying it. The backend uses `kthw-provisioner`, while the AWS provider uses `kthw-bootstrap`. Initialize this project with state migration and confirm the prompt. The backend config path is relative to `deployment/terraform`. Then create a fresh plan:

```sh
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_SECURITY_TOKEN AWS_CREDENTIAL_EXPIRATION
export AWS_PROFILE=kthw-bootstrap
aws sts get-caller-identity
terraform -chdir=deployment/terraform init -migrate-state \
  -backend-config=../../../kubernetes-the-hard-way/infrastructure/terraform/lab.s3.tfbackend
terraform -chdir=deployment/terraform plan -out=tfplan
terraform -chdir=deployment/terraform apply tfplan
terraform -chdir=deployment/terraform output -raw deploy_role_arn
```

Terraform selects the region from `AWS_REGION`, then `AWS_DEFAULT_REGION`, then the active AWS profile, and falls back to `us-east-1`. It needs Python 3 and the AWS CLI to read the profile. Pass `-var='aws_region=REGION'` to override the selected region. The `aws_region` output supplies the same value to the GitHub setup script.

Optionally pass `-var='aws_account_id=YOUR_ACCOUNT_ID'` to enforce an expected account ID.

If the GitHub OIDC provider already exists in the account, pass `-var='github_oidc_provider_arn=YOUR_PROVIDER_ARN'` to the plan. Set `github_oidc_subject` if your repository uses GitHub's immutable subject format or another environment. Check the actual token claims before setting the trust policy.

Install GitHub CLI on Debian or Ubuntu using GitHub’s official package repository:

```sh
sudo apt update
sudo apt install -y wget
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
sudo apt update
sudo apt install -y gh
```

For other Linux distributions, use the [official installation instructions](https://github.com/cli/cli/blob/trunk/docs/install_linux.md). Authenticate with an account that can administer this repository and its environment secrets:

```sh
gh auth login
gh auth status
```

After applying Terraform, configure GitHub:

```sh
deployment/terraform/scripts/setup-github.sh
```

The script creates the `kthw-lab` environment when needed, allows `main` and `v*.*.*` tags, and sets `KTHW_DEPLOY_ROLE_ARN` and `KTHW_AWS_REGION` from Terraform outputs. For an existing environment it preserves existing policies and adds those two rules. If the existing environment does not use custom branch policies, configure it explicitly before running the script. To supply outputs without Terraform, set both `KTHW_DEPLOY_ROLE_ARN` and `KTHW_AWS_REGION` in the environment. Set `GITHUB_REPOSITORY` to target a different owner and repository.

The pipeline also needs a Docker Hub username and access token. Set them with the CLI, entering the token at the interactive prompt:

```sh
gh variable set DOCKERHUB_USERNAME --repo cakesmith/house-price-predictor --body YOUR_DOCKERHUB_USERNAME
gh secret set DOCKERHUB_TOKEN --repo cakesmith/house-price-predictor
```


Open the existing `make kube-tunnel` from the Kubernetes the Hard Way repository and keep it running. In another terminal, authenticate `gh` with permission to manage environment secrets, then run:

```sh
KUBECONFIG="$HOME/.kube/kthw-aws.yaml" deployment/kubernetes/scripts/bootstrap-deployer.sh
```

The script applies the RBAC, requests and approves a client certificate, validates the resulting access through the tunnel, and updates the GitHub environment secret. Run it again to rotate the credential. The signer controls the actual expiry, which the script prints. Schedule rotation in an administrator-controlled environment before that expiry. The Role grants access to Helm release Secrets and workload resources throughout the `house-price` namespace.

The workflow discovers the running jumpbox by its lab tags. It skips deployment when no jumpbox is running and reports tunnel, authentication, or Helm failures as job failures. The cluster and SSM agent must be ready, and the agent must support remote-host port forwarding. The existing release trigger or manual dispatch starts the pipeline. Commit the chart with the workflow so Actions can check it out.

Reference: https://kubernetes.io/docs/tasks/tls/certificate-issue-client-csr/
