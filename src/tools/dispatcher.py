import time
from pydantic import ValidationError

class ToolDispatcher:
    def __init__(self, registry, state, logger, max_calls: int):
        self.registry, self.state, self.logger = registry, state, logger
        self.max_calls = max_calls
        self.calls = 0

    def execute(self, name: str, raw_args: dict, allowed_permissions: set[str]) -> dict:
        if self.calls >= self.max_calls:
            return {"ok": False, "error_type": "budget", "message": "Tool-call ceiling reached."}
        spec = self.registry.get(name)
        if not spec:
            return {"ok": False, "error_type": "unknown_tool", "message": f"Unknown tool '{name}'. Available tools: {[t.name for t in self.registry.all()]}"}
        if spec.permission not in allowed_permissions:
            return {"ok": False, "error_type": "permission", "message": f"Tool '{name}' is not permitted in this stage."}
        try:
            args = spec.args_model.model_validate(raw_args)
        except ValidationError as exc:
            return {"ok": False, "error_type": "validation", "message": "Invalid tool arguments.", "details": exc.errors()}
        self.calls += 1
        started = time.perf_counter()
        try:
            result = spec.handler(args, self.state)
            result = {"ok": True, **result}
        except Exception as exc:
            result = {"ok": False, "error_type": "execution", "message": f"Tool execution failed: {type(exc).__name__}"}
        elapsed = round(time.perf_counter() - started, 4)
        self.logger.info("tool_call", extra={"tool": name, "elapsed": elapsed, "ok": result.get("ok")})
        return {**result, "tool": name, "elapsed_seconds": elapsed}
