from fastapi.testclient import TestClient

from credit_risk.api.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "Credit Risk API is running"


def test_valid_prediction():
    applicant = {
        "person_age": 43,
        "person_income": 47840,
        "person_home_ownership": "RENT",
        "person_emp_length": 27,
        "loan_intent": "PERSONAL",
        "loan_amnt": 15000,
        "loan_percent_income": 0.31,
        "cb_person_default_on_file": "N",
        "cb_person_cred_hist_length": 12,
    }

    response = client.post("/predict", json=applicant)

    assert response.status_code == 200

    data = response.json()

    assert "default_probability" in data
    assert "prediction" in data
    assert "risk_label" in data
    assert "increasing_risk" in data
    assert "decreasing_risk" in data

    assert len(data["increasing_risk"]) > 0
    assert len(data["decreasing_risk"]) > 0


def test_invalid_age():
    applicant = {
        "person_age": 15,
        "person_income": 50000,
        "person_home_ownership": "RENT",
        "person_emp_length": 2,
        "loan_intent": "PERSONAL",
        "loan_amnt": 10000,
        "loan_percent_income": 0.2,
        "cb_person_default_on_file": "N",
        "cb_person_cred_hist_length": 5,
    }

    response = client.post("/predict", json=applicant)

    assert response.status_code == 422


def test_employment_greater_than_age():
    applicant = {
        "person_age": 25,
        "person_income": 50000,
        "person_home_ownership": "RENT",
        "person_emp_length": 40,
        "loan_intent": "PERSONAL",
        "loan_amnt": 10000,
        "loan_percent_income": 0.2,
        "cb_person_default_on_file": "N",
        "cb_person_cred_hist_length": 5,
    }

    response = client.post("/predict", json=applicant)

    assert response.status_code == 422