from typing import Literal
from pydantic import BaseModel, Field

class Finding(BaseModel):
    statement: str
    claim_type: Literal["fact", "inference", "recommendation", "uncertainty"]
    evidence_ids: list[str]
    confidence: Literal["high", "medium", "low"]

class Approval(BaseModel):
    approver: str
    decision: Literal["approve", "reject", "request_additional_research", "modify_scope"]
    timestamp: str
    notes: str

class FinalReport(BaseModel):
    report_id: str
    generated_at: str
    model_versions: list[str]
    run_cost: float
    research_objective: dict
    executive_summary: str
    market_overview: list[Finding]
    key_trends: list[Finding]
    competitor_analysis: dict
    opportunities: list[Finding]
    risks: list[Finding]
    evidence_appendix: list[dict]
    recommendations: list[Finding]
    confidence_level: Literal["high", "medium", "low"]
    confidence_rationale: str
    limitations_and_gaps: list[str]
    sources: list[dict]
    approval: Approval | None = None
