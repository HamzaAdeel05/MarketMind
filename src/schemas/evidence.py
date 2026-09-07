from typing import Literal
from pydantic import BaseModel, Field

class EvidenceRecord(BaseModel):
    evidence_id: str
    question_id: str
    claim: str = Field(min_length=3)
    claim_type: Literal["fact", "inference", "recommendation", "uncertainty"]
    source_ref: str
    source_kind: Literal["retrieved_document", "search_result", "calculation", "model_generated"]
    source_detail: str
    credibility: Literal["high", "medium", "low", "unknown"]
    recency: str
    corroboration: list[str]
    confidence: Literal["high", "medium", "low"]
    analyst_notes: str = ""
