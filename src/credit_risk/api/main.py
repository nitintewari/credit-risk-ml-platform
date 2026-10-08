from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from credit_risk.api.schemas import ApplicantRequest
from credit_risk.database import Base, engine, get_db
from credit_risk.explain import explain_risk
from credit_risk.models import PredictionRecord
from credit_risk.predict import predict_risk
from credit_risk.repository import (
    get_prediction,
    save_prediction,
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Credit Risk API",
    version="1.0.0",
)


@app.get("/")
def health_check():
    return {"status": "Credit Risk API is running"}


@app.post("/predict")
def predict(
    applicant: ApplicantRequest,
    db: Session = Depends(get_db),
):
    applicant_data = applicant.model_dump()

    prediction = predict_risk(applicant_data)
    explanation = explain_risk(applicant_data)

    record = save_prediction(
        db=db,
        applicant_data=applicant_data,
        prediction_result=prediction,
    )

    return {
        **prediction,
        **explanation,
        "prediction_id": record.id,
    }
@app.get("/predictions/{prediction_id}")
def get_prediction_by_id(
    prediction_id: int,
    db: Session = Depends(get_db),
):
    record = get_prediction(db, prediction_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Prediction not found",
        )

    return {
        "id": record.id,
        "person_age": record.person_age,
        "person_income": record.person_income,
        "loan_amnt": record.loan_amnt,
        "default_probability": record.default_probability,
        "prediction": record.prediction,
        "risk_label": record.risk_label,
        "threshold": record.threshold,
        "created_at": record.created_at,
    }    