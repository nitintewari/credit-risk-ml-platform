import mlflow
import numpy as np
import mlflow.sklearn

from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from credit_risk.data import (
    clean_data,
    load_data,
    split_features_target,
)
from credit_risk.model import build_model
from credit_risk.train import DATA_PATH


mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("Credit Risk Model")


def run_experiment():

    # Load and clean data
    df = load_data(DATA_PATH)
    df = clean_data(df)

    X, y = split_features_target(df)

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    # Train / validation split
    X_train_core, X_val, y_train_core, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.20,
        random_state=42,
        stratify=y_train,
    )

    base_model = build_model()

    calibrated_model = CalibratedClassifierCV(
        estimator=base_model,
        method="isotonic",
        cv=5,
    )

    calibrated_model.fit(
        X_train_core,
        y_train_core,
    )

    # Find threshold using validation data
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
    best_threshold = float(thresholds[best_index])

    # Final evaluation on untouched test data
    test_prob = calibrated_model.predict_proba(X_test)[:, 1]

    test_pred = (
        test_prob >= best_threshold
    ).astype(int)

    metrics = {
        "accuracy": accuracy_score(y_test, test_pred),
        "precision": precision_score(y_test, test_pred),
        "recall": recall_score(y_test, test_pred),
        "f1": f1_score(y_test, test_pred),
        "roc_auc": roc_auc_score(y_test, test_prob),
        "pr_auc": average_precision_score(y_test, test_prob),
        "brier_score": brier_score_loss(y_test, test_prob),
    }

    with mlflow.start_run():

        mlflow.log_params({
            "model": "XGBoost",
            "n_estimators": 300,
            "learning_rate": 0.05,
            "max_depth": 4,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "calibration": "isotonic",
            "decision_threshold": best_threshold,
            "train_samples": len(X_train_core),
            "validation_samples": len(X_val),
            "test_samples": len(X_test),
        })
        mlflow.sklearn.log_model(
    sk_model=calibrated_model,
    name="model",
    serialization_format="cloudpickle",
)
        mlflow.log_metrics(metrics)

        print("MLflow experiment recorded.")
        print(f"Threshold: {best_threshold:.4f}")

        for name, value in metrics.items():
            print(f"{name}: {value:.4f}")


if __name__ == "__main__":
    run_experiment()