"""LLM-judge layer for the small slice of tasks where pass/fail alone can't
capture quality (e.g. "refactor this for readability" - no test can grade
readability). Deliberately not used for correctness anywhere else in this
project: grading.py's pass rate never depends on a judge call.

Includes a calibration check modeled directly on Malator's
judge_sanity_check.py: hand-built (good, bad) code pairs fed straight to
the judge, bypassing the benchmark entirely, specifically to confirm the
judge can actually tell them apart before any real judged score is trusted.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from pydantic import BaseModel

from modelbench.providers.gemini import GeminiProvider

JUDGE_SYSTEM = (
    "You are a strict code reviewer scoring a single Python function for "
    "readability and quality, not correctness (assume it is correct). "
    "Score 0.0 (unreadable: bad names, no structure, deeply nested) to 1.0 "
    "(clear, well-named, appropriately simple for the task). Respond with "
    "ONLY a JSON object matching the given schema, no other text."
)


class JudgeScore(BaseModel):
    score: float
    reasoning: str


def judge_quality(judge_provider: GeminiProvider, code: str, task_prompt: str) -> JudgeScore:
    prompt = (
        f"Task the code was written for:\n{task_prompt}\n\n"
        f"Candidate code:\n```python\n{code}\n```\n\n"
        f"Respond with JSON: {{\"score\": <0.0-1.0>, \"reasoning\": \"<one sentence>\"}}"
    )
    result = judge_provider.generate(prompt, system=JUDGE_SYSTEM)
    if not result.success or not result.text:
        raise RuntimeError(f"judge call failed: {result.error}")
    text = result.text.strip()
    # tolerate a stray fence even though the system prompt asks for none
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    data = json.loads(text)
    return JudgeScore(**data)


@dataclass
class CalibrationCase:
    id: str
    task_prompt: str
    good_code: str
    bad_code: str


CALIBRATION_CASES: list[CalibrationCase] = [
    CalibrationCase(
        id="cal01_naming",
        task_prompt="Write a function that returns the average of a list of numbers.",
        good_code=(
            "def average(numbers: list[float]) -> float:\n"
            "    return sum(numbers) / len(numbers)\n"
        ),
        bad_code=(
            "def f(x):\n"
            "    a=0\n"
            "    b=0\n"
            "    for c in x:\n"
            "        a=a+c\n"
            "        b=b+1\n"
            "    return a/b\n"
        ),
    ),
    CalibrationCase(
        id="cal02_nesting",
        task_prompt="Write a function that returns True if a number is a positive even number, False otherwise.",
        good_code=(
            "def is_positive_even(n: int) -> bool:\n"
            "    return n > 0 and n % 2 == 0\n"
        ),
        bad_code=(
            "def check(n):\n"
            "    if n>0:\n"
            "        if n%2==0:\n"
            "            return True\n"
            "        else:\n"
            "            return False\n"
            "    else:\n"
            "        return False\n"
        ),
    ),
    CalibrationCase(
        id="cal03_structure",
        task_prompt="Write a function that removes duplicate items from a list while preserving order.",
        good_code=(
            "def deduplicate(items: list) -> list:\n"
            "    seen = set()\n"
            "    result = []\n"
            "    for item in items:\n"
            "        if item not in seen:\n"
            "            seen.add(item)\n"
            "            result.append(item)\n"
            "    return result\n"
        ),
        bad_code=(
            "def d(l):\n"
            "    r=[]\n"
            "    for i in range(len(l)):\n"
            "        ok=True\n"
            "        for j in range(i):\n"
            "            if l[j]==l[i]:\n"
            "                ok=False\n"
            "        if ok==True:\n"
            "            r.append(l[i])\n"
            "    return r\n"
        ),
    ),
]


def run_calibration(judge_provider: GeminiProvider) -> list[dict]:
    """Returns one row per case with both scores, so a human can eyeball
    whether the judge actually separates good from bad before the real
    quality-scored slice of the benchmark is trusted."""
    rows = []
    for case in CALIBRATION_CASES:
        good = judge_quality(judge_provider, case.good_code, case.task_prompt)
        bad = judge_quality(judge_provider, case.bad_code, case.task_prompt)
        rows.append(
            {
                "id": case.id,
                "good_score": good.score,
                "bad_score": bad.score,
                "separated": good.score > bad.score,
                "good_reasoning": good.reasoning,
                "bad_reasoning": bad.reasoning,
            }
        )
    return rows
