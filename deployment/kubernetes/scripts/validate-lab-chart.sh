#!/usr/bin/env bash
set -euo pipefail

chart=deployment/kubernetes/house-price-model
values=$chart/values-kthw-lab.yaml
helm lint "$chart" --strict --values "$values"
rendered=$(helm template house-price "$chart" --namespace house-price --values "$values")
images=$(awk '/^[[:space:]]*image:/ { print $2 }' <<< "$rendered")
[[ $(wc -l <<< "$images") -eq 2 ]]
if grep -Ev '^"[^"]+@sha256:[a-f0-9]{64}"$' <<< "$images"; then
  echo "Every lab container image must use a pinned digest." >&2
  exit 1
fi
