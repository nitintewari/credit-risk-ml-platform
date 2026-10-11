import json
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.orm import Session

from credit_risk.config import NUMERIC_FEATURES
from credit_risk.models import PredictionRecord


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASELINE_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "monitoring_baseline.json"
)

MINIMUM_SAMPLES = 30


def load_baseline():
    with open(BASELINE_PATH, "r") as file:
        return json.load(file)


def check_data_drift(db: Session):
    total_predictions = (
        db.query(func.count(PredictionRecord.id))
        .scalar()
        or 0
    )

    if total_predictions < MINIMUM_SAMPLES:
        return {
            "status": "insufficient_data",
            "samples": total_predictions,
            "minimum_required": MINIMUM_SAMPLES,
        }

    baseline = load_baseline()

    results = {}

    for feature in NUMERIC_FEATURES:
        column = getattr(PredictionRecord, feature)

        production_mean = (
            db.query(func.avg(column))
            .scalar()
        )

        if production_mean is None:
            continue

        training_mean = baseline[feature]["mean"]
        training_std = baseline[feature]["std"]

        if training_std == 0:
            shift = 0.0
        else:
            shift = abs(
                float(production_mean) - training_mean
            ) / training_std

        if shift >= 1.0:
            status = "drift"
        elif shift >= 0.5:
            status = "warning"
        else:
            status = "stable"

        results[feature] = {
            "training_mean": round(training_mean, 4),
            "production_mean": round(
                float(production_mean),
                4,
            ),
            "mean_shift_std": round(shift, 4),
            "status": status,
        }

    statuses = [
        result["status"]
        for result in results.values()
    ]

    if "drift" in statuses:
        overall_status = "drift"
    elif "warning" in statuses:
        overall_status = "warning"
    else:
        overall_status = "stable"

    return {
        "status": overall_status,
        "samples": total_predictions,
        "features": results,
    }