"""Environment loading and registry of the two Gemini tiers in scope.

No third-party .env library is used, same call as ChessLens's config.py -
the KEY=VALUE parser below covers what .env.example actually needs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = PROJECT_ROOT / "tasks"
RESULTS_DIR = PROJECT_ROOT / "results"


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def load_env(env_file: Path | str | None = None) -> None:
    path = Path(env_file) if env_file else Path(os.environ.get("MODELBENCH_ENV_FILE", PROJECT_ROOT / ".env"))
    for key, value in _parse_env_file(path).items():
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class ModelProfile:
    name: str
    provider: str
    api_model_id: str
    # USD per token, from the public Gemini API price list at build time -
    # see docs/overview.md for the source and date checked.
    cost_per_input_token: float
    cost_per_output_token: float


REGISTRY: dict[str, ModelProfile] = {
    "gemini-flash": ModelProfile(
        name="gemini-flash",
        provider="google",
        api_model_id="gemini-3.5-flash",
        cost_per_input_token=1.50 / 1_000_000,
        cost_per_output_token=9.00 / 1_000_000,
    ),
    "gemini-flash-lite": ModelProfile(
        name="gemini-flash-lite",
        provider="google",
        api_model_id="gemini-3.5-flash-lite",
        cost_per_input_token=0.30 / 1_000_000,
        cost_per_output_token=2.50 / 1_000_000,
    ),
}


def get_gemini_api_key(env_file: Path | str | None = None) -> str | None:
    load_env(env_file)
    return os.environ.get("GEMINI_API_KEY") or None
