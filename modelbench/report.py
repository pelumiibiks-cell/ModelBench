"""Turns Result rows into the markdown tables docs/overview.md and the
published writeup actually quote - every number in the writeup should
trace back to running this against results/*.csv, not be retyped by hand.
"""

from __future__ import annotations

from modelbench.grading import CategorySummary, summarize_by_model, summarize_by_model_category
from modelbench.runner import Result


def model_summary_table(results: list[Result]) -> str:
    summaries = summarize_by_model(results)
    lines = [
        "| Model | Evaluated | Quota-blocked | Pass rate (of evaluated) | Total cost (USD) | Cost / passing task | Mean latency (ms) | Extraction failure rate |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in summaries:
        cost_per_pass = f"${s.cost_per_passing_task:.5f}" if s.cost_per_passing_task is not None else "n/a (0 passed)"
        lines.append(
            f"| {s.model} | {s.n_evaluated}/{s.n_cells} | {s.n_quota_blocked} | {s.pass_rate:.1%} | ${s.total_cost_usd:.5f} | "
            f"{cost_per_pass} | {s.mean_latency_ms:.0f} | {s.extraction_failure_rate:.1%} |"
        )
    return "\n".join(lines)


def category_table(results: list[Result]) -> str:
    summaries = summarize_by_model_category(results)
    by_category: dict[str, list[CategorySummary]] = {}
    for s in summaries:
        by_category.setdefault(s.category, []).append(s)

    header_models = sorted({s.model for s in summaries})
    lines = ["| Category | " + " | ".join(header_models) + " |", "|---|" + "---|" * len(header_models)]
    for category in sorted(by_category):
        row = [category]
        by_model = {s.model: s for s in by_category[category]}
        for model in header_models:
            s = by_model.get(model)
            if s is None or s.n_evaluated == 0:
                row.append("n/a (quota-blocked)")
            else:
                row.append(f"{s.pass_rate:.1%} ({s.n_evaluated}/{s.n_cells})")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)
