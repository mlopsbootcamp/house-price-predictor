#!/usr/bin/env bash
set -euo pipefail

repo=${GITHUB_REPOSITORY:-cakesmith/house-price-predictor}
environment=kthw-lab
region=${KTHW_AWS_REGION:-}
role_arn=${KTHW_DEPLOY_ROLE_ARN:-}
terraform_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

command -v gh >/dev/null || { echo "Install the GitHub CLI first." >&2; exit 1; }
gh auth status >/dev/null
if [[ -z "$role_arn" ]]; then
  command -v terraform >/dev/null || { echo "Set KTHW_DEPLOY_ROLE_ARN or install Terraform." >&2; exit 1; }
  role_arn=$(terraform -chdir="$terraform_dir" output -raw deploy_role_arn)
fi
if [[ -z "$region" ]]; then
  command -v terraform >/dev/null || { echo "Set KTHW_AWS_REGION or install Terraform." >&2; exit 1; }
  region=$(terraform -chdir="$terraform_dir" output -raw aws_region)
fi
[[ -n "$role_arn" && -n "$region" ]] || { echo "The role ARN and AWS region are required." >&2; exit 1; }

endpoint="repos/$repo/environments/$environment"
existing=$(gh api --paginate "repos/$repo/environments?per_page=100" --jq ".environments[] | select(.name == \"$environment\") | .name")
if [[ -z "$existing" ]]; then
  printf '%s' '{"deployment_branch_policy":{"protected_branches":false,"custom_branch_policies":true}}' |
    gh api --method PUT "$endpoint" --input - >/dev/null
else
  custom=$(gh api "$endpoint" --jq '.deployment_branch_policy.custom_branch_policies // false')
  if [[ "$custom" != true ]]; then
    echo "Existing $environment environment does not use custom deployment policies. Configure it explicitly before rerunning." >&2
    exit 1
  fi
fi

policies=$(gh api --paginate "$endpoint/deployment-branch-policies?per_page=100" --jq '.branch_policies[] | [.type, .name] | @tsv')
if ! grep -Fxq $'branch\tmain' <<< "$policies"; then
  gh api --method POST "$endpoint/deployment-branch-policies" -f name=main -f type=branch >/dev/null
fi
if ! grep -Fxq $'tag\tv*.*.*' <<< "$policies"; then
  gh api --method POST "$endpoint/deployment-branch-policies" -f 'name=v*.*.*' -f type=tag >/dev/null
fi
gh variable set KTHW_DEPLOY_ROLE_ARN --repo "$repo" --env "$environment" --body "$role_arn"
gh variable set KTHW_AWS_REGION --repo "$repo" --env "$environment" --body "$region"
printf 'Configured %s in %s. Existing deployment rules and repository Docker Hub credentials were preserved.\n' "$environment" "$repo"
