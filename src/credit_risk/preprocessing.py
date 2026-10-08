from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from credit_risk.config import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)


def build_preprocessor():

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        (
            "encoder",
            OneHotEncoder(handle_unknown="ignore"),
        ),
    ])

    preprocessor = ColumnTransformer([
        (
            "num",
            numeric_pipeline,
            NUMERIC_FEATURES,
        ),
        (
            "cat",
            categorical_pipeline,
            CATEGORICAL_FEATURES,
        ),
    ])

    return preprocessor