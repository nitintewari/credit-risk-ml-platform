from pathlib import Path

import joblib
import numpy as np

from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import precision_recall_curve
from sklearn.model_selection import train_test_split

from credit_risk.data import (
    load_data,
    clean_data,
    split_features_target,
)
from credit_risk.model import build_model


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "credit_risk_dataset.csv"
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"


def train():
    # 1. Load and clean data
    df = load_data(DATA_PATH)
    df = clean_data(df)

    X, y = split_features_target(df)

    # 2. Create train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    # 3. Create train/validation split
    X_train_core, X_val, y_train_core, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.20,
        random_state=42,
        stratify=y_train,
    )

    # 4. Build base XGBoost pipeline
    base_model = build_model()
    # Train a separate base model for SHAP explanations
    explainability_model = build_model()
    explainability_model.fit(X_train_core, y_train_core)    
    # 5. Apply isotonic calibration
    calibrated_model = CalibratedClassifierCV(
        estimator=base_model,
        method="isotonic",
        cv=5,
    )

    calibrated_model.fit(X_train_core, y_train_core)

    # 6. Find best F1 threshold using validation data
    val_prob = calibrated_model.predict_proba(X_val)[:, 1]

    precision, recall, thresholds = precision_recall_curve(
        y_val,
        val_prob,
    )

    f1_scores = (
        2 * precision[:-1] * recall[:-1]
        / (precision[:-1] + recall[:-1] + 1e-10)
    )

    best_index = np.argmax(f1_scores)
    best_threshold = thresholds[best_index]

    # 7. Save model and threshold
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        calibrated_model,
        ARTIFACT_DIR / "credit_risk_model.pkl",
    )

    joblib.dump(
        best_threshold,
        ARTIFACT_DIR / "decision_threshold.pkl",
    )
    joblib.dump(
        explainability_model,
        ARTIFACT_DIR / "explainability_model.pkl",
    )

    print("Training complete.")
    print(f"Best threshold: {best_threshold:.3f}")
    print("Model saved to artifacts/credit_risk_model.pkl")


if __name__ == "__main__":
    train()