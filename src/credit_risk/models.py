from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from credit_risk.database import Base


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    person_age: Mapped[int] = mapped_column(Integer)
    person_income: Mapped[float] = mapped_column(Float)
    person_home_ownership: Mapped[str] = mapped_column(String)
    person_emp_length: Mapped[float | None] = mapped_column(Float, nullable=True)
    loan_intent: Mapped[str] = mapped_column(String)
    loan_amnt: Mapped[float] = mapped_column(Float)
    loan_percent_income: Mapped[float] = mapped_column(Float)
    cb_person_default_on_file: Mapped[str] = mapped_column(String)
    cb_person_cred_hist_length: Mapped[int] = mapped_column(Integer)

    default_probability: Mapped[float] = mapped_column(Float)
    prediction: Mapped[int] = mapped_column(Integer)
    risk_label: Mapped[str] = mapped_column(String)
    threshold: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )