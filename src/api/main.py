from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from inference import predict_price, batch_predict
from schemas import HousePredictionRequest, PredictionResponse
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import start_http_server
import threading
from typing import List

# Initialize FastAPI app with metadata
app = FastAPI(
    title="House Price Prediction API",
    description=(
        "An API for predicting house prices based on various features. "
        "This application is part of the MLOps Bootcamp by School of Devops. "
        "Authored by Gourav Shah."
    ),
    version="1.0.0",
    contact={
        "name": "School of Devops",
        "url": "https://schoolofdevops.com",
        "email": "learn@schoolofdevops.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize and instrument Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Start Prometheus metrics server on port 9100 in a background thread
def start_metrics_server():
    start_http_server(9100)

threading.Thread(target=start_metrics_server, daemon=True).start()

# Health check endpoint
@app.get("/health", response_model=dict)
async def health_check():
    return {"status": "healthy", "model_loaded": True}

# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
async def predict(request: HousePredictionRequest):
    return predict_price(request)

# Batch prediction endpoint
@app.post("/batch-predict", response_model=List[PredictionResponse])
async def batch_predict_endpoint(requests: List[HousePredictionRequest]):
    return batch_predict(requests)
