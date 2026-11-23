#!/usr/bin/env bash
set -euo pipefail

repository=${1:?Pass the API image repository}
digest=${2:?Pass the tested API image digest}
[[ $digest =~ ^sha256:[0-9a-f]{64}$ ]]
export API_IMAGE_REPOSITORY="$repository" API_IMAGE_DIGEST="$digest"
values=deployment/kubernetes/house-price-model/values-kthw-lab.yaml
check_workflow=helm-validate.yaml

yq -i '.api.image.repository = strenv(API_IMAGE_REPOSITORY) | .api.image.digest = strenv(API_IMAGE_DIGEST)' "$values"
if git diff --quiet -- "$values"; then
  printf 'The lab already tracks %s@%s.\n' "$repository" "$digest"
  exit 0
fi

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -- "$values"
git commit -m "Promote the house price API to the Kubernetes lab"
commit=$(git rev-parse HEAD)
branch="lab-promotion/${GITHUB_RUN_ID:?}-${GITHUB_RUN_ATTEMPT:?}"
git push origin "HEAD:refs/heads/$branch"
trap 'git push origin --delete "$branch" || true' EXIT

# A dispatch runs under GITHUB_TOKEN and attaches the render check to this commit.
gh workflow run "$check_workflow" --ref "$branch"
for attempt in {1..36}; do
  conclusion=$(gh run list --workflow "$check_workflow" --event workflow_dispatch \
    --commit "$commit" --limit 1 --json status,conclusion \
    --jq '.[] | select(.status == "completed") | .conclusion')
  case "$conclusion" in
    success)
      # A concurrent change to main is a non-fast-forward and requires a fresh render.
      git push origin "HEAD:refs/heads/main"
      printf 'Argo CD can now reconcile %s at %s.\n' "$repository@$digest" "$commit"
      exit 0
      ;;
    '') sleep 5 ;;
    *) printf 'Helm validation finished with %s for %s.\n' "$conclusion" "$commit" >&2; exit 1 ;;
  esac
done
printf 'Timed out waiting for Helm validation of %s.\n' "$commit" >&2
exit 1
