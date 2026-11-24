#!/usr/bin/env bash
set -euo pipefail

repository=${1:?Pass the API image repository}
digest=${2:?Pass the tested API image digest}
if [[ ! $digest =~ ^sha256:[0-9a-f]{64}$ ]]; then
  printf 'Expected a tested image digest in sha256 format.\n' >&2
  exit 1
fi
export API_IMAGE_REPOSITORY="$repository" API_IMAGE_DIGEST="$digest"
image="$repository@$digest"
values=deployment/kubernetes/house-price-model/values-kthw-lab.yaml
check_workflow=helm-validate.yaml

summarize() {
  if [[ -n ${GITHUB_STEP_SUMMARY:-} ]]; then
    printf '%s\n' "$1" >> "$GITHUB_STEP_SUMMARY"
  fi
}

stop_promotion() {
  printf '%s\n' "$1" >&2
  summarize "- Result: $1"
  exit 1
}

printf 'Checking the lab image pin in %s for %s.\n' "$values" "$image"
summarize "- Tested image: \`$image\`"
yq -i '.api.image.repository = strenv(API_IMAGE_REPOSITORY) | .api.image.digest = strenv(API_IMAGE_DIGEST)' "$values"
if git diff --quiet -- "$values"; then
  printf 'The lab values on main already pin %s. Skipping Helm validation and the main update.\n' "$image"
  summarize '- Result: The lab values on `main` already pin this image. Helm validation and the `main` update were skipped.'
  exit 0
fi

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -- "$values"
git commit -m "Promote the house price API to the Kubernetes lab"
commit=$(git rev-parse HEAD)
branch="lab-promotion/${GITHUB_RUN_ID:?}-${GITHUB_RUN_ATTEMPT:?}"
printf 'Pushing candidate commit %s to temporary branch %s.\n' "$commit" "$branch"
summarize "- Candidate commit: \`$commit\` on \`$branch\`"
if ! git push origin "HEAD:refs/heads/$branch"; then
  stop_promotion "Could not push the temporary branch $branch for Helm validation."
fi
trap 'printf "Deleting temporary branch %s.\n" "$branch"; git push origin --delete "$branch" || true' EXIT

# A dispatch runs under GITHUB_TOKEN and attaches the render check to this commit.
printf 'Starting the Helm validation workflow for commit %s.\n' "$commit"
if ! gh workflow run "$check_workflow" --ref "$branch"; then
  stop_promotion "Could not start Helm validation for $commit."
fi
printf 'Waiting for Helm validation before updating main.\n'
validation_url=''
for attempt in {1..36}; do
  if ! run=$(gh run list --workflow "$check_workflow" --event workflow_dispatch \
    --commit "$commit" --limit 1 --json url,status,conclusion \
    --jq '.[] | [.url, .status, .conclusion] | @tsv'); then
    stop_promotion "Could not look up the Helm validation run for $commit."
  fi
  IFS=$'\t' read -r run_url status conclusion <<< "$run"
  if [[ -n $run_url && $run_url != "$validation_url" ]]; then
    validation_url=$run_url
    printf 'Follow Helm validation at %s\n' "$validation_url"
    summarize "- [Helm validation run]($validation_url)"
  fi
  if [[ $status != completed || -z $conclusion ]]; then
    sleep 5
    continue
  fi
  if [[ $conclusion != success ]]; then
    stop_promotion "Helm validation finished with result '$conclusion'. Promotion stopped before updating main."
  fi

  printf 'Helm validation passed for %s. Updating main with the validated commit.\n' "$commit"
  # A concurrent change to main is a non-fast-forward and requires a fresh render.
  if ! git push origin "HEAD:refs/heads/main"; then
    stop_promotion 'Helm validation passed, but Git could not update main. See the promotion step log for the push error.'
  fi
  printf 'Main now pins %s at commit %s. Argo CD can reconcile this Git revision.\n' "$image" "$commit"
  summarize '- Result: Helm validation passed and `main` now pins this image. Argo CD can reconcile the Git revision.'
  exit 0
done
stop_promotion 'Timed out waiting for Helm validation. Promotion stopped before updating main.'
