from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import logging
import time
from fastapi.middleware.cors import CORSMiddleware
from credit_risk.monitoring import get_prediction_summary
from fastapi import Request
from credit_risk.drift import check_data_drift
from credit_risk.logging_config import setup_logging
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
setup_logging()

logger = logging.getLogger("credit_risk.api")

app = FastAPI(
    title="Credit Risk API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    logger.info(
        "%s %s - status=%s - duration=%.3fs",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )

    return response
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
    logger.info(
    "Prediction created - id=%s - risk=%s - probability=%.4f",
    record.id,
    prediction["risk_label"],
    prediction["default_probability"],
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
@app.get("/monitoring/summary")
def monitoring_summary(
    db: Session = Depends(get_db),
):
    return get_prediction_summary(db)    

@app.get("/monitoring/drift")
def monitoring_drift(
    db: Session = Depends(get_db),
):
    return check_data_drift(db)    