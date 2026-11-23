#!/usr/bin/env bash
set -euo pipefail

image=${1:?Pass the API image to test}
container=$(docker run --detach --publish 127.0.0.1::8000 "$image")
trap 'docker rm -f "$container" >/dev/null' EXIT
url="http://$(docker port "$container" 8000/tcp)"

if ! curl --fail --silent --show-error --retry 15 --retry-all-errors --retry-delay 2 --max-time 5 "$url/health"; then
  docker logs "$container"
  exit 1
fi

curl --fail-with-body --silent --show-error --max-time 20 \
  --header 'Content-Type: application/json' \
  --data '{"sqft":1500,"bedrooms":3,"bathrooms":2,"location":"suburban","year_built":2000,"condition":"Good"}' \
  "$url/predict" | jq --exit-status '.predicted_price | type == "number" and isfinite'
