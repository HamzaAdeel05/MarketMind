from typing import Literal
from pydantic import BaseModel, Field

class SubQuestion(BaseModel):
    id: str = Field(min_length=2, max_length=80)
    question: str = Field(min_length=5, max_length=500)
    evidence_types: list[Literal["fact", "comparison", "metric", "uncertainty"]] = Field(min_length=1, max_length=4)
    candidate_tools: list[str] = Field(min_length=1, max_length=6)

class Objective(BaseModel):
    id: str
    objective: str
    subquestions: list[SubQuestion] = Field(min_length=2, max_length=5)

class ResearchPlan(BaseModel):
    entity_type: str
    segment: str
    geography: str
    time_horizon: str
    deliverable_type: str
    assumptions: list[str]
    ambiguities: list[str]
    objectives: list[Objective] = Field(min_length=3, max_length=6)
