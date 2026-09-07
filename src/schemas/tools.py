from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class SearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=3, max_length=500)
    source_type: Literal["local_corpus"] = "local_corpus"
    max_results: int = Field(default=5, ge=1, le=10)
    recency_window: str = Field(default="all", max_length=40)

class RetrieveArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(min_length=1, max_length=100)
    section: str | None = Field(default=None, max_length=100)

class CalculateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Literal["sum", "average", "difference", "percentage_change"]
    values: list[float] = Field(min_length=1, max_length=20)
    period: str | None = None

class CompareArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entities: list[str] = Field(min_length=2, max_length=10)
    attributes: list[str] = Field(min_length=1, max_length=10)

class SaveEvidenceArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_id: str
    claim: str
    claim_type: Literal["fact", "inference", "recommendation", "uncertainty"]
    source_ref: str
    confidence: Literal["high", "medium", "low"]

class GenerateReportArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: str
    sections: list[str] | None = None
