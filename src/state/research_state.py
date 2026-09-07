from dataclasses import dataclass, field
from src.schemas.evidence import EvidenceRecord
from src.schemas.plan import ResearchPlan

@dataclass
class ResearchState:
    run_id: str
    request: str
    plan: ResearchPlan | None = None
    evidence: list[EvidenceRecord] = field(default_factory=list)
    source_refs: dict[str,str] = field(default_factory=dict)
    tool_history: list[dict] = field(default_factory=list)
    iteration: int = 0
    status: str = "running"
    limitations: list[str] = field(default_factory=list)
