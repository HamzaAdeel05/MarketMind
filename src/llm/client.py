import random
import time
from typing import Any

from openai import OpenAI

from src.config import Settings
from src.llm.usage import UsageRecord, UsageTracker

# Keep pricing in one place and treat it as an estimate. Update before submission.
PRICE_PER_MILLION = {
    "gpt-5.6-luna": (0.20, 1.20),
}

class LLMClient:
    def __init__(self, settings: Settings, usage: UsageTracker, logger) -> None:
        self.settings = settings
        self.usage = usage
        self.logger = logger
        self.client = OpenAI(api_key=settings.api_key, timeout=settings.timeout_seconds) if settings.use_openai else None

    def text(self, *, run_id: str, stage: str, system: str, user: str, model: str | None = None) -> str:
        if not self.settings.use_openai:
            raise RuntimeError("OpenAI is disabled; this stage requires an API call")
        chosen = model or self.settings.model
        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries + 1):
            try:
                response = self.client.responses.create(model=chosen, instructions=system, input=user)
                usage = getattr(response, "usage", None)
                input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
                output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
                in_price, out_price = PRICE_PER_MILLION.get(chosen, (0.0, 0.0))
                cost = input_tokens / 1_000_000 * in_price + output_tokens / 1_000_000 * out_price
                self.usage.add(UsageRecord(run_id, stage, chosen, input_tokens, output_tokens, cost))
                self.logger.info("model_call", extra={"stage": stage, "model": chosen, "input_tokens": input_tokens, "output_tokens": output_tokens})
                return response.output_text
            except Exception as exc:
                last_error = exc
                if attempt >= self.settings.max_retries:
                    break
                delay = min(8.0, (2 ** attempt) + random.random())
                time.sleep(delay)
        raise RuntimeError(f"LLM call failed after bounded retries: {type(last_error).__name__}") from last_error
