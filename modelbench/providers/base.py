"""Provider-agnostic generation interface, shaped to match RouteIQ's
ModelProvider (`adaptive-model-router/app/`) so a second provider - a real
Anthropic or OpenAI adapter - can be added later without touching runner.py
or grading.py, whenever a billed key exists to test it against.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class GenerationResult:
    model: str
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    success: bool
    error: str | None = None


class ModelProvider(Protocol):
    def generate(self, prompt: str, *, system: str | None = None) -> GenerationResult: ...

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float: ...
