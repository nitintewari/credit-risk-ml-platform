from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ApplicantRequest(BaseModel):
    person_age: int = Field(ge=18, le=100)
    person_income: float = Field(gt=0)

    person_home_ownership: Literal[
        "RENT",
        "MORTGAGE",
        "OWN",
        "OTHER",
    ]

    person_emp_length: float | None = Field(
        default=None,
        ge=0,
    )

    loan_intent: Literal[
        "PERSONAL",
        "EDUCATION",
        "MEDICAL",
        "VENTURE",
        "HOMEIMPROVEMENT",
        "DEBTCONSOLIDATION",
    ]

    loan_amnt: float = Field(gt=0)

    loan_percent_income: float = Field(
        ge=0,
        le=1,
    )

    cb_person_default_on_file: Literal["Y", "N"]

    cb_person_cred_hist_length: int = Field(
        ge=0
    )

    @model_validator(mode="after")
    def validate_employment_length(self):
        if self.person_emp_length is not None and self.person_emp_length > self.person_age:
            raise ValueError("Employment length cannot be greater than age.")
        return self