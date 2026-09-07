from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class UsageRecord:
    run_id: str
    stage: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0

class UsageTracker:
    def __init__(self) -> None:
        self.records: list[UsageRecord] = []

    def add(self, record: UsageRecord) -> None:
        self.records.append(record)

    @property
    def total_cost(self) -> float:
        return sum(r.estimated_cost_usd for r in self.records)

    def as_dict(self) -> dict[str, Any]:
        return {"records": [asdict(r) for r in self.records], "total_cost_usd": round(self.total_cost, 8)}
