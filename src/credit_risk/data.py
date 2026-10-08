import numpy as np
import pandas as pd

from credit_risk.config import (
    TARGET,
    LEAKAGE_COLUMNS,
)


def load_data(path):
    return pd.read_csv(path)


def clean_data(df):
    df = df.copy()

    # Remove exact duplicate records
    df = df.drop_duplicates().reset_index(drop=True)

    # Remove impossible ages
    df = df[df["person_age"] <= 100].reset_index(drop=True)

    # Mark impossible employment length as missing
    invalid_emp = (
        df["person_emp_length"] > df["person_age"]
    )

    df.loc[
        invalid_emp,
        "person_emp_length"
    ] = np.nan

    return df


def split_features_target(df):
    X = df.drop(
        columns=[TARGET] + LEAKAGE_COLUMNS
    )

    y = df[TARGET]

    return X, y