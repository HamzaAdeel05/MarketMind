from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    model: str
    fast_model: str
    run_budget_usd: float
    max_iterations: int
    max_tool_calls: int
    max_repair_rounds: int
    request_max_chars: int
    timeout_seconds: float
    max_retries: int
    use_openai: bool

    @classmethod
    def load(cls) -> "Settings":
        use_openai = _bool("USE_OPENAI", True)
        api_key = os.getenv("OPENAI_API_KEY")
        if use_openai and not api_key:
            raise RuntimeError("Missing required environment variable: OPENAI_API_KEY")
        return cls(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            fast_model=os.getenv("OPENAI_FAST_MODEL", "gpt-5.6-luna"),
            run_budget_usd=float(os.getenv("RUN_BUDGET_USD", "1.50")),
            max_iterations=int(os.getenv("MAX_ITERATIONS", "12")),
            max_tool_calls=int(os.getenv("MAX_TOOL_CALLS", "30")),
            max_repair_rounds=int(os.getenv("MAX_REPAIR_ROUNDS", "2")),
            request_max_chars=int(os.getenv("REQUEST_MAX_CHARS", "5000")),
            timeout_seconds=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "60")),
            max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3")),
            use_openai=use_openai,
        )
