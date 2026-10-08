from sqlalchemy.orm import Session

from credit_risk.models import PredictionRecord


def save_prediction(
    db: Session,
    applicant_data: dict,
    prediction_result: dict,
):
    record = PredictionRecord(
        **applicant_data,
        default_probability=prediction_result["default_probability"],
        prediction=prediction_result["prediction"],
        risk_label=prediction_result["risk_label"],
        threshold=prediction_result["threshold"],
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_prediction(db: Session, prediction_id: int):
    return (
        db.query(PredictionRecord)
        .filter(PredictionRecord.id == prediction_id)
        .first()
    )