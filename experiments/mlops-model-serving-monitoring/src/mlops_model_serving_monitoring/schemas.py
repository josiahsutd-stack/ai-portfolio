from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "demo-churn-schema-v1"


class ChurnPredictionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenure_months: float = Field(ge=0, le=120)
    monthly_spend: float = Field(ge=0, le=1000)
    support_tickets: float = Field(ge=0, le=100)
    usage_score: float = Field(ge=0, le=1.5)
