from pydantic import BaseModel, Field
from typing import List

class HousePredictionRequest(BaseModel):
    sqft: float = Field(..., gt=0, description="Square footage of the house")
    bedrooms: int = Field(..., ge=1, description="Number of bedrooms")
    bathrooms: float = Field(..., gt=0, description="Number of bathrooms")
    location: str = Field(..., description="Location (urban, suburban, rural)")
    year_built: int = Field(..., ge=1800, le=2023, description="Year the house was built")
    condition: str = Field(..., description="Condition of the house (e.g., Good, Excellent, Fair)")

class PredictionResponse(BaseModel):
    predicted_price: float
    confidence_interval: List[float]
    features_importance: dict
    prediction_time: str