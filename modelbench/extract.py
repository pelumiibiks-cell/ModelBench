"""Pull a candidate solution's Python source out of a model's raw text
response. Models routinely wrap code in a fenced block with commentary
before/after it; a naive `exec(response_text)` would fail on that
commentary alone, before the solution is even judged on correctness.
"""

from __future__ import annotations

import re

_FENCE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)


def extract_code(text: str) -> str:
    """Returns the first fenced code block found, or the raw text stripped
    if no fence is present (some models answer with bare code, no fence,
    especially at high effort/low chattiness settings)."""
    match = _FENCE_RE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()
