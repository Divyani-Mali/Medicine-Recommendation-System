from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from backend import models, schemas
from backend.database import engine, get_db
from backend.ml_service import predict_disease, get_disease_details, get_all_symptoms
from backend.ai_service import generate_ai_summary

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medicine Recommendation System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "API running"}

@app.get("/symptoms", response_model=list[str])
def list_symptoms():
    return get_all_symptoms()

@app.post("/predict", response_model=schemas.PredictResponse)
def predict(request: schemas.PredictRequest, db: Session = Depends(get_db)):
    if not request.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom is required")

    predicted = predict_disease(request.symptoms)
    desc, pre, med, die, wrkout = get_disease_details(predicted)

    ai_summary = generate_ai_summary(predicted, request.symptoms, desc, pre, med, die, wrkout)

    record = models.PredictionRecord(
        symptoms=", ".join(request.symptoms),
        predicted_disease=predicted,
        description=desc,
        precautions=str(pre),
        medications=str(med),
        diet=str(die),
        workout=str(wrkout),
        ai_summary=ai_summary,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return schemas.PredictResponse(
        id=record.id,
        predicted_disease=predicted,
        description=desc,
        precautions=pre,
        medications=med,
        diet=die,
        workout=wrkout,
        ai_summary=ai_summary,
    )

@app.get("/history", response_model=list[schemas.HistoryItem])
def get_history(limit: int = 20, db: Session = Depends(get_db)):
    return db.query(models.PredictionRecord).order_by(
        models.PredictionRecord.created_at.desc()
    ).limit(limit).all()

@app.post("/feedback")
def submit_feedback(fb: schemas.FeedbackRequest, db: Session = Depends(get_db)):
    prediction = db.query(models.PredictionRecord).filter_by(id=fb.prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

    feedback = models.Feedback(
        prediction_id=fb.prediction_id,
        was_helpful=fb.was_helpful,
        comment=fb.comment,
    )
    db.add(feedback)
    db.commit()
    return {"message": "Feedback recorded"}

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.PredictionRecord).count()
    top_diseases = db.query(models.PredictionRecord.predicted_disease).all()
    from collections import Counter
    counts = Counter([d[0] for d in top_diseases])
    return {
        "total_predictions": total,
        "top_diseases": counts.most_common(5),
    }