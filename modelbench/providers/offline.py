"""A scripted, zero-cost provider for testing the grading pipeline without
spending real tokens - same role as ChessLens's --offline mode. Returns a
fixed response (or one looked up by prompt substring) rather than calling
any API.
"""

from __future__ import annotations

from modelbench.providers.base import GenerationResult


class OfflineProvider:
    def __init__(self, name: str = "offline-stub", responses: dict[str, str] | None = None, default: str = "") -> None:
        self.name = name
        self._responses = responses or {}
        self._default = default

    def generate(self, prompt: str, *, system: str | None = None) -> GenerationResult:
        text = self._default
        for key, value in self._responses.items():
            if key in prompt:
                text = value
                break
        return GenerationResult(
            model=self.name, text=text,
            input_tokens=len(prompt.split()), output_tokens=len(text.split()),
            latency_ms=0.0, success=bool(text), error=None if text else "no scripted response matched",
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return 0.0
