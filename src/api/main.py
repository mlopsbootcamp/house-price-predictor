from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
from inference import predict_price, batch_predict
from schemas import HousePredictionRequest, PredictionResponse

# Custom Prometheus metrics
PREDICTION_COUNTER = Counter(
    "prediction_requests_total",
    "Total number of prediction requests",
    ["endpoint"]
)
PREDICTION_LATENCY = Histogram(
    "prediction_latency_seconds",
    "Time spent processing prediction requests",
    ["endpoint"]
)

# Initialize FastAPI app with metadata
app = FastAPI(
    title="House Price Prediction API",
    description=(
        "An API for predicting house prices based on various features. "
        "This application is part of the IT5414 Machine Learning course project."
    ),
    version="1.0.0",
    contact={
        "name": "IT5414 Team",
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

# Initialize Prometheus instrumentator
Instrumentator().instrument(app).expose(app)

# Health check endpoint
@app.get("/health", response_model=dict)
async def health_check():
    return {"status": "healthy", "model_loaded": True}

# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
async def predict(request: HousePredictionRequest):
    import time
    start_time = time.time()
    PREDICTION_COUNTER.labels(endpoint="predict").inc()
    result = predict_price(request)
    PREDICTION_LATENCY.labels(endpoint="predict").observe(time.time() - start_time)
    return result

# Batch prediction endpoint
@app.post("/batch-predict", response_model=list)
async def batch_predict_endpoint(requests: list[HousePredictionRequest]):
    import time
    start_time = time.time()
    PREDICTION_COUNTER.labels(endpoint="batch_predict").inc()
    result = batch_predict(requests)
    PREDICTION_LATENCY.labels(endpoint="batch_predict").observe(time.time() - start_time)
    return result
