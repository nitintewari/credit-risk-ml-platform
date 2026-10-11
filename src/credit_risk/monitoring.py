from sqlalchemy import func
from sqlalchemy.orm import Session

from credit_risk.models import PredictionRecord


def get_prediction_summary(db: Session):
    total_predictions = (
        db.query(func.count(PredictionRecord.id))
        .scalar()
        or 0
    )

    if total_predictions == 0:
        return {
            "total_predictions": 0,
            "average_probability": 0.0,
            "high_risk_count": 0,
            "low_risk_count": 0,
            "high_risk_rate": 0.0,
        }

    average_probability = (
        db.query(
            func.avg(
                PredictionRecord.default_probability
            )
        )
        .scalar()
        or 0.0
    )

    high_risk_count = (
        db.query(func.count(PredictionRecord.id))
        .filter(PredictionRecord.prediction == 1)
        .scalar()
        or 0
    )

    low_risk_count = (
        total_predictions - high_risk_count
    )

    high_risk_rate = (
        high_risk_count / total_predictions
    )

    return {
        "total_predictions": total_predictions,
        "average_probability": round(
            float(average_probability),
            4,
        ),
        "high_risk_count": high_risk_count,
        "low_risk_count": low_risk_count,
        "high_risk_rate": round(
            high_risk_rate,
            4,
        ),
    }