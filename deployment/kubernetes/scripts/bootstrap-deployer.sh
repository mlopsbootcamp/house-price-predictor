#!/usr/bin/env bash
set -euo pipefail

# Run with an administrator kubeconfig and an authenticated GitHub CLI.
repo=${GITHUB_REPOSITORY:-cakesmith/house-price-predictor}
environment=${DEPLOY_ENVIRONMENT:-kthw-lab}
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
umask 077
work_dir=$(mktemp -d)
csr_name="house-price-deploy-$(openssl rand -hex 12)"
csr_created=false
cleanup() {
  if [[ $csr_created == true ]]; then
    kubectl --kubeconfig="$work_dir/admin-config" delete csr "$csr_name" --ignore-not-found >/dev/null 2>&1 || true
  fi
  rm -rf "$work_dir"
}
trap cleanup EXIT

for command in kubectl openssl gh base64; do
  command -v "$command" >/dev/null || { echo "Missing required command: $command" >&2; exit 1; }
done
gh auth status >/dev/null
kubectl --request-timeout=10s get --raw=/version >/dev/null
kubectl config view --minify --flatten --raw > "$work_dir/admin-config"

# Flatten paths in the active admin configuration and extract only the public CA.
kubectl config view --minify --flatten --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d > "$work_dir/ca.crt"
if [[ ! -s "$work_dir/ca.crt" ]]; then
  echo "The active admin kubeconfig has no cluster CA certificate." >&2
  exit 1
fi
kubectl apply -f "$script_dir/../deployer-rbac.yaml"
openssl req -new -newkey rsa:3072 -nodes -keyout "$work_dir/client.key" \
  -out "$work_dir/client.csr" -subj '/CN=github-actions-helm' >/dev/null 2>&1
request=$(base64 < "$work_dir/client.csr" | tr -d '\n')
cat <<MANIFEST | kubectl create -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: $csr_name
spec:
  request: $request
  signerName: kubernetes.io/kube-apiserver-client
  expirationSeconds: 7776000
  usages:
    - client auth
MANIFEST
csr_created=true
kubectl certificate approve "$csr_name"
for attempt in {1..30}; do
  certificate=$(kubectl get csr "$csr_name" -o jsonpath='{.status.certificate}')
  if [[ -n "$certificate" ]]; then break; fi
  sleep 1
done
if [[ -z "$certificate" ]]; then
  echo "The certificate signer did not issue a certificate within 30 seconds." >&2
  exit 1
fi
printf '%s' "$certificate" | base64 -d > "$work_dir/client.crt"
openssl verify -purpose sslclient -CAfile "$work_dir/ca.crt" "$work_dir/client.crt" >/dev/null
openssl x509 -in "$work_dir/client.crt" -noout -checkend 86400 >/dev/null

export KUBECONFIG="$work_dir/config"
kubectl config set-cluster kthw --server=https://127.0.0.1:16443 \
  --tls-server-name=server.kubernetes.local --certificate-authority="$work_dir/ca.crt" --embed-certs=true >/dev/null
kubectl config set-credentials github-actions-helm --client-certificate="$work_dir/client.crt" \
  --client-key="$work_dir/client.key" --embed-certs=true >/dev/null
kubectl config set-context deploy --cluster=kthw --user=github-actions-helm --namespace=house-price >/dev/null
kubectl config use-context deploy >/dev/null
# The administrator connection must use the same local tunnel as the deployment job.
if [[ $(kubectl --request-timeout=10s auth can-i create deployments -n house-price) != yes ]] || \
   [[ $(kubectl --request-timeout=10s auth can-i list secrets -n house-price) != yes ]]; then
  echo "The issued credential could not access the deployment namespace." >&2
  exit 1
fi
gh secret set KTHW_DEPLOY_KUBECONFIG --repo "$repo" --env "$environment" < "$KUBECONFIG"
printf 'Updated %s environment in %s. Certificate ' "$environment" "$repo"
openssl x509 -in "$work_dir/client.crt" -noout -enddate
