from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "artifacts" / "credit_risk_model.pkl"
THRESHOLD_PATH = PROJECT_ROOT / "artifacts" / "decision_threshold.pkl"


model = joblib.load(MODEL_PATH)
threshold = joblib.load(THRESHOLD_PATH)


def predict_risk(applicant_data):
    applicant_df = pd.DataFrame([applicant_data])

    probability = model.predict_proba(applicant_df)[0, 1]

    prediction = int(probability >= threshold)

    return {
        "default_probability": round(float(probability), 4),
        "prediction": prediction,
        "risk_label": "High Risk" if prediction == 1 else "Low Risk",
        "threshold": round(float(threshold), 4),
    }