from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PredictRequest(BaseModel):
    symptoms: List[str]

class PredictResponse(BaseModel):
    id: int
    predicted_disease: str
    description: str
    precautions: List[str]
    medications: List[str]
    diet: List[str]
    workout: List[str]
    ai_summary: Optional[str] = None

class FeedbackRequest(BaseModel):
    prediction_id: int
    was_helpful: bool
    comment: Optional[str] = None

class HistoryItem(BaseModel):
    id: int
    symptoms: str
    predicted_disease: str
    created_at: datetime

    class Config:
        from_attributes = True