from pathlib import Path

import joblib
import pandas as pd
import shap

from credit_risk.config import CATEGORICAL_FEATURES


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "explainability_model.pkl"
)


explainability_model = joblib.load(MODEL_PATH)

preprocessor = explainability_model.named_steps["preprocessor"]
classifier = explainability_model.named_steps["classifier"]

explainer = shap.TreeExplainer(classifier)


def get_original_feature(transformed_feature):
    if transformed_feature.startswith("num__"):
        return transformed_feature.replace("num__", "", 1)

    if transformed_feature.startswith("cat__"):
        encoded_name = transformed_feature.replace("cat__", "", 1)

        for feature in CATEGORICAL_FEATURES:
            if encoded_name.startswith(feature + "_"):
                return feature

    return transformed_feature


def format_feature_value(feature, value):
    if value is None:
        return "Unknown"

    if feature in ["person_income", "loan_amnt"]:
        return f"${float(value):,.0f}"

    if feature == "loan_percent_income":
        return f"{float(value):.0%}"

    if feature == "cb_person_default_on_file":
        return "Yes" if value == "Y" else "No"

    return str(value)


def explain_risk(applicant_data, top_n=3):
    applicant_df = pd.DataFrame([applicant_data])

    transformed = preprocessor.transform(applicant_df)

    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()

    feature_names = preprocessor.get_feature_names_out()

    transformed_df = pd.DataFrame(
        transformed,
        columns=feature_names,
    )

    shap_values = explainer(transformed_df)

    explanation_df = pd.DataFrame({
        "transformed_feature": feature_names,
        "shap_value": shap_values.values[0],
    })

    explanation_df["feature"] = explanation_df[
        "transformed_feature"
    ].apply(get_original_feature)

    aggregated = (
        explanation_df
        .groupby("feature", as_index=False)["shap_value"]
        .sum()
    )

    increasing = (
        aggregated[aggregated["shap_value"] > 0]
        .sort_values("shap_value", ascending=False)
        .head(top_n)
    )

    decreasing = (
        aggregated[aggregated["shap_value"] < 0]
        .sort_values("shap_value")
        .head(top_n)
    )

    return {
        "increasing_risk": [
            {
                "feature": row["feature"],
                "value": format_feature_value(
                    row["feature"],
                    applicant_data[row["feature"]],
                ),
            }
            for _, row in increasing.iterrows()
        ],
        "decreasing_risk": [
            {
                "feature": row["feature"],
                "value": format_feature_value(
                    row["feature"],
                    applicant_data[row["feature"]],
                ),
            }
            for _, row in decreasing.iterrows()
        ],
    }