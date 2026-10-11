import random

from fastapi.testclient import TestClient

from credit_risk.api.main import app
from credit_risk.data import (
    clean_data,
    load_data,
    split_features_target,
)


client = TestClient(app)

df = load_data("data/raw/credit_risk_dataset.csv")
df = clean_data(df)

X, _ = split_features_target(df)

sample = X.sample(
    n=100,
    random_state=42,
)

successful = 0

for _, row in sample.iterrows():
    applicant = row.to_dict()

    # Convert pandas NaN employment length to JSON-compatible None
    if applicant["person_emp_length"] != applicant["person_emp_length"]:
        applicant["person_emp_length"] = None

    response = client.post(
        "/predict",
        json=applicant,
    )

    if response.status_code == 200:
        successful += 1
    else:
        print(
            "Failed:",
            response.status_code,
            response.json(),
        )

print(f"Successful predictions: {successful}/100")