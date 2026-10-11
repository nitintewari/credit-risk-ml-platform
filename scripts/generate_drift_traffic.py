from fastapi.testclient import TestClient

from credit_risk.api.main import app


client = TestClient(app)

successful = 0

for i in range(100):
    applicant = {
        "person_age": 55,
        "person_income": 180000,
        "person_home_ownership": "MORTGAGE",
        "person_emp_length": 25,
        "loan_intent": "PERSONAL",
        "loan_amnt": 40000,
        "loan_percent_income": 0.35,
        "cb_person_default_on_file": "N",
        "cb_person_cred_hist_length": 20,
    }

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

print(f"Successful drift predictions: {successful}/100")