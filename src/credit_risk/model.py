from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from credit_risk.preprocessing import build_preprocessor


def build_model():
    preprocessor = build_preprocessor()

    classifier = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier),
    ])

    return model