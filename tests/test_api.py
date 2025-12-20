"""
Unit tests for House Price Prediction API
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'api'))

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check_returns_200(self, client):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_returns_healthy_status(self, client):
        """Test that health endpoint returns healthy status."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True


class TestPredictEndpoint:
    """Tests for the prediction endpoint."""
    
    def test_predict_with_valid_input(self, client, sample_house_data):
        """Test prediction with valid input data."""
        response = client.post("/predict", json=sample_house_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "predicted_price" in data
        assert "confidence_interval" in data
        assert "prediction_time" in data
        assert isinstance(data["predicted_price"], (int, float))
        assert len(data["confidence_interval"]) == 2
    
    def test_predict_returns_reasonable_price(self, client, sample_house_data):
        """Test that predicted price is within reasonable range."""
        response = client.post("/predict", json=sample_house_data)
        data = response.json()
        
        # Price should be positive and reasonable (between 10k and 10M)
        assert data["predicted_price"] > 10000
        assert data["predicted_price"] < 10000000
    
    def test_predict_with_missing_fields(self, client):
        """Test prediction with missing required fields."""
        incomplete_data = {"bedrooms": 3}
        response = client.post("/predict", json=incomplete_data)
        assert response.status_code == 422  # Validation error


class TestBatchPredictEndpoint:
    """Tests for the batch prediction endpoint."""
    
    def test_batch_predict_with_multiple_houses(self, client, sample_house_data):
        """Test batch prediction with multiple houses."""
        batch_data = [sample_house_data, sample_house_data]
        response = client.post("/batch-predict", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_batch_predict_empty_list(self, client):
        """Test batch prediction with empty list."""
        response = client.post("/batch-predict", json=[])
        assert response.status_code == 200
        data = response.json()
        assert data == []


# Fixtures
@pytest.fixture
def client():
    """Create test client for the API."""
    from main import app
    return TestClient(app)


@pytest.fixture
def sample_house_data():
    """Sample house data for testing."""
    return {
        "bedrooms": 3,
        "bathrooms": 2,
        "sqft_living": 1800,
        "sqft_lot": 5000,
        "floors": 1,
        "waterfront": 0,
        "view": 0,
        "condition": 3,
        "grade": 7,
        "sqft_above": 1800,
        "sqft_basement": 0,
        "year_built": 1990,
        "year_renovated": 0,
        "zipcode": 98001,
        "lat": 47.5,
        "long": -122.2,
        "sqft_living15": 1800,
        "sqft_lot15": 5000
    }
