"""Deterministic aggregation of Result rows into per-model and
per-model/category summaries. No judge model involved anywhere in this
file - that's the whole point of grading on pytest pass/fail: the number
doesn't need a second model to vouch for it.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from modelbench.runner import Result


@dataclass
class ModelSummary:
    model: str
    n_cells: int
    n_evaluated: int
    n_quota_blocked: int
    pass_rate: float  # over evaluated cells only - quota-blocked cells excluded from the denominator
    total_cost_usd: float
    cost_per_passing_task: float | None
    mean_latency_ms: float
    extraction_failure_rate: float


@dataclass
class CategorySummary:
    model: str
    category: str
    n_cells: int
    n_evaluated: int
    pass_rate: float  # over evaluated cells only


def summarize_by_model(results: list[Result]) -> list[ModelSummary]:
    by_model: dict[str, list[Result]] = defaultdict(list)
    for r in results:
        by_model[r.model].append(r)

    summaries = []
    for model, rows in by_model.items():
        n = len(rows)
        evaluated = [r for r in rows if not r.quota_blocked]
        n_evaluated = len(evaluated)
        n_passed = sum(1 for r in evaluated if r.all_passed)
        total_cost = sum(r.cost_usd for r in rows)
        pass_rate = n_passed / n_evaluated if n_evaluated else 0.0
        cost_per_pass = (total_cost / n_passed) if n_passed else None
        mean_latency = sum(r.latency_ms for r in evaluated) / n_evaluated if n_evaluated else 0.0
        extraction_failures = sum(1 for r in evaluated if not r.extracted_ok)
        summaries.append(
            ModelSummary(
                model=model, n_cells=n, n_evaluated=n_evaluated, n_quota_blocked=n - n_evaluated,
                pass_rate=pass_rate, total_cost_usd=total_cost,
                cost_per_passing_task=cost_per_pass, mean_latency_ms=mean_latency,
                extraction_failure_rate=extraction_failures / n_evaluated if n_evaluated else 0.0,
            )
        )
    return sorted(summaries, key=lambda s: s.model)


def summarize_by_model_category(results: list[Result]) -> list[CategorySummary]:
    by_key: dict[tuple[str, str], list[Result]] = defaultdict(list)
    for r in results:
        by_key[(r.model, r.category)].append(r)

    summaries = []
    for (model, category), rows in by_key.items():
        n = len(rows)
        evaluated = [r for r in rows if not r.quota_blocked]
        n_evaluated = len(evaluated)
        n_passed = sum(1 for r in evaluated if r.all_passed)
        summaries.append(
            CategorySummary(
                model=model, category=category, n_cells=n, n_evaluated=n_evaluated,
                pass_rate=n_passed / n_evaluated if n_evaluated else 0.0,
            )
        )
    return sorted(summaries, key=lambda s: (s.category, s.model))


def find_overkill_categories(results: list[Result], cheap_model: str, expensive_model: str) -> list[str]:
    """Categories where the expensive model scores no better than the cheap
    one - the concrete, checkable version of "wasted money" the report
    leads with, not an assertion."""
    cheap = {s.category: s.pass_rate for s in summarize_by_model_category(results) if s.model == cheap_model}
    costly = {s.category: s.pass_rate for s in summarize_by_model_category(results) if s.model == expensive_model}
    return sorted(cat for cat in cheap if cat in costly and costly[cat] <= cheap[cat])
