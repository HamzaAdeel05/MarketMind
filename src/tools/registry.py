from dataclasses import dataclass
from typing import Any, Callable, Type
from pydantic import BaseModel

@dataclass
class ToolSpec:
    name: str
    description: str
    args_model: Type[BaseModel]
    permission: str
    handler: Callable[[BaseModel, Any], dict]

class ToolRegistry:
    def __init__(self): self._tools: dict[str, ToolSpec] = {}
    def register(self, spec: ToolSpec): self._tools[spec.name] = spec
    def get(self, name: str) -> ToolSpec | None: return self._tools.get(name)
    def all(self) -> list[ToolSpec]: return list(self._tools.values())
    def definitions(self) -> list[dict]:
        return [{"name": t.name, "description": t.description, "parameters": t.args_model.model_json_schema()} for t in self.all()]
