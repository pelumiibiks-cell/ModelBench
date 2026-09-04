"""Gemini provider adapter via the google-genai SDK's Interactions API
(client.interactions.create, NOT the older client.models.generate_content).

Usage field names and the system-prompt kwarg are taken from QAura's
llm/gemini.py, which confirmed both against a live call
(`qaura doctor`, 2026-08-30, google-genai 2.20.0): the real usage object
exposes `total_input_tokens`/`total_output_tokens`, not `input_tokens`/
`output_tokens`, and the system-prompt kwarg is `system_instruction`, not
`instructions`. Older/newer SDK versions are tolerated via a fallback name
list rather than a hard assumption.
"""

from __future__ import annotations

import time
from time import perf_counter

from modelbench.config import ModelProfile
from modelbench.providers.base import GenerationResult

_MAX_RETRIES = 2
_RETRY_BACKOFF_SECONDS = 1.0
# Without this, a stalled connection to the Gemini API blocks generate()
# indefinitely - confirmed the hard way: a first real run with no client
# timeout hung for hours on a single call with no error, no output, and
# no way to tell it apart from "still working" until it was killed by hand.
_REQUEST_TIMEOUT_MS = 60_000


class GeminiProvider:
    def __init__(self, profile: ModelProfile, api_key: str | None) -> None:
        self.profile = profile
        self._api_key = api_key
        self._client = None

    def _client_or_raise(self):
        if not self._api_key:
            raise RuntimeError(
                f"No GEMINI_API_KEY set - GeminiProvider cannot call {self.profile.api_model_id}."
            )
        if self._client is None:
            from google import genai

            try:
                from google.genai import types

                http_options = types.HttpOptions(timeout=_REQUEST_TIMEOUT_MS)
                self._client = genai.Client(api_key=self._api_key, http_options=http_options)
            except Exception:
                # Defensive, same call QAura's gemini.py makes: a future SDK
                # version changing this shape shouldn't break client
                # construction, just skip setting an explicit timeout.
                self._client = genai.Client(api_key=self._api_key)
        return self._client

    def generate(self, prompt: str, *, system: str | None = None) -> GenerationResult:
        client = self._client_or_raise()
        kwargs: dict = {"input": prompt}
        if system:
            kwargs["system_instruction"] = system

        start = perf_counter()
        last_error: Exception | None = None
        interaction = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                interaction = client.interactions.create(model=self.profile.api_model_id, **kwargs)
                break
            except Exception as exc:  # noqa: BLE001 - the SDK's error hierarchy for this surface isn't publicly stable to catch narrowly
                last_error = exc
                if attempt == _MAX_RETRIES:
                    latency_ms = (perf_counter() - start) * 1000
                    return GenerationResult(
                        model=self.profile.name, text="", input_tokens=0, output_tokens=0,
                        latency_ms=round(latency_ms, 1), success=False, error=str(exc),
                    )
                time.sleep(_RETRY_BACKOFF_SECONDS * (2**attempt))
        latency_ms = (perf_counter() - start) * 1000

        text = getattr(interaction, "output_text", "") or ""
        input_tokens, output_tokens = _extract_usage(interaction)

        return GenerationResult(
            model=self.profile.name, text=text,
            input_tokens=input_tokens, output_tokens=output_tokens,
            latency_ms=round(latency_ms, 1), success=bool(text), error=None if text else "empty response",
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return input_tokens * self.profile.cost_per_input_token + output_tokens * self.profile.cost_per_output_token


def _extract_usage(interaction) -> tuple[int, int]:
    raw_usage = getattr(interaction, "usage", None)
    if raw_usage is None:
        return 0, 0

    def _get(*names: str) -> int:
        for name in names:
            v = getattr(raw_usage, name, None)
            if isinstance(v, int):
                return v
        return 0

    input_tokens = _get("total_input_tokens", "input_tokens", "prompt_tokens")
    output_tokens = _get("total_output_tokens", "output_tokens", "completion_tokens")
    return input_tokens, output_tokens
