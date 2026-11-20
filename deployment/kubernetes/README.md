# Kubernetes deployment

The Helm chart runs the FastAPI inference service and the Streamlit UI.
It uses two public Docker Hub images for Linux AMD64 workers:

- `docker.io/cakesmith/house-price-model:e11e73e` comes from the
  [MLOps pipeline](../../.github/workflows/mlops-pipeline.yaml) and contains
  the trained model and preprocessor.
- `docker.io/cakesmith/streamlit:dev` provides the UI and is the image named
  in [Docker Compose](../../docker-compose.yml).

From the repository root, with Helm installed and your Kubernetes context
pointing at the target cluster, run:

```bash
helm upgrade --install house-price ./deployment/kubernetes/house-price-model \
  --namespace default --wait --timeout 5m
```

Each app gets a Deployment and a ClusterIP Service in the same namespace.
Streamlit uses `API_URL` to call FastAPI through its ClusterIP Service.
For the `house-price` release, Kubernetes expands
`http://$(HOUSE_PRICE_API_SERVICE_HOST):8000` to the Service address when
it starts the container. This works on the lab cluster without CoreDNS.
If the API Service is recreated separately, restart the Streamlit Deployment
so its pods pick up the Service address.

```bash
kubectl -n default port-forward service/house-price-streamlit 8501:8501
```

Open `http://localhost:8501` and submit a prediction to check the complete
request path. To check FastAPI directly, run
`kubectl -n default port-forward service/house-price-api 8000:8000` in a
separate terminal, then run `curl -fsS http://localhost:8000/health`.

To roll out a different published model, override `api.image.tag` using its
seven-character SHA:

```bash
helm upgrade --install house-price ./deployment/kubernetes/house-price-model \
  --namespace default --wait --timeout 5m --set-string api.image.tag=YOUR_COMMIT_SHA
```

For an image from the [manual CI workflow](../../.github/workflows/mlops-ci-workflow.yaml),
set `api.image.repository=docker.io/cakesmith/fastapi` and use the full
commit SHA as `api.image.tag`. Set `streamlit.image.tag` to select another
published UI tag.
