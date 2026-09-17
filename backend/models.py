from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    symptoms = Column(String, nullable=False)
    predicted_disease = Column(String, nullable=False)
    description = Column(Text)
    precautions = Column(Text)
    medications = Column(Text)
    diet = Column(Text)
    workout = Column(Text)
    ai_summary = Column(Text, nullable=True)   # new — holds the Gemini-generated explanation
    created_at = Column(DateTime, default=datetime.utcnow)

    feedback = relationship("Feedback", back_populates="prediction")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"))
    was_helpful = Column(Boolean, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("PredictionRecord", back_populates="feedback")