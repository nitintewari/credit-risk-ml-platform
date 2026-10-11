# Credit Risk ML Platform

An end-to-end production-style machine learning system for predicting loan default risk.

The project covers the complete ML lifecycle: data analysis, preprocessing, model development, calibration, explainability, responsible ML, API development, persistent storage, containerization, CI/CD, monitoring, experiment tracking, and cloud deployment.

## Live Application

Frontend:
https://credit-risk-ml-platform-1.onrender.com

API Documentation:
https://credit-risk-ml-platform-urlf.onrender.com/docs

---

## Project Overview

The system estimates the probability that a loan applicant may default.

Instead of stopping at model training, the project demonstrates how a machine learning model can be converted into a production-style application.

The final system provides:

- Default probability prediction
- High Risk / Low Risk classification
- SHAP-based explanations
- Input validation
- Persistent prediction storage
- Prediction monitoring
- Data drift monitoring
- Automated testing
- Docker containerization
- CI/CD with GitHub Actions
- Experiment tracking with MLflow
- Cloud deployment
- React frontend

---

## Architecture

```text
                         GitHub
                            |
                            v
                     GitHub Actions
                Tests + Build + Docker
                            |
                            v
                       Render Cloud
                            |
              +-------------+-------------+
              |                           |
              v                           v
        React Frontend               FastAPI Backend
              |                           |
              |                     Pydantic Validation
              |                           |
              +------ POST /predict ----->|
                                          v
                               Calibrated XGBoost
                                          |
                                          v
                                  SHAP Explanation
                                          |
                                          v
                                     PostgreSQL