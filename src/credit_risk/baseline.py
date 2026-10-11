import json
from pathlib import Path

import pandas as pd

from credit_risk.config import NUMERIC_FEATURES


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "monitoring_baseline.json"
)


def save_monitoring_baseline(
    X_train: pd.DataFrame,
):
    baseline = {}

    for feature in NUMERIC_FEATURES:
        baseline[feature] = {
            "mean": float(X_train[feature].mean()),
            "std": float(X_train[feature].std()),
        }

    BASELINE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(BASELINE_PATH, "w") as file:
        json.dump(
            baseline,
            file,
            indent=2,
        )