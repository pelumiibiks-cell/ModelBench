"""Executes every (task, model, repetition) cell, grades it, and returns one
Result row per cell - the shape Monte Carlo grid pattern is structurally
borrowed from reject-inference's experiment.py (a Scenario per grid cell,
pruned rather than exhaustive), not copied literally, since this grid has
no cells to prune - every task runs against every model.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from modelbench.extract import extract_code
from modelbench.providers.base import ModelProvider
from modelbench.sandbox import run_against_tests
from modelbench.tasks import Task

SYSTEM_PROMPT = (
    "You are a careful Python programmer. Respond with ONLY a single fenced "
    "python code block implementing exactly what is asked. No explanation "
    "before or after the code block."
)


def build_prompt(task: Task) -> str:
    return (
        f"{task.prompt}\n\n"
        f"Implement a function named `{task.entry_point}` that satisfies the "
        f"specification above. Respond with only the code."
    )


@dataclass
class Result:
    task_id: str
    category: str
    model: str
    rep: int
    extracted_ok: bool
    ran: bool
    tests_passed: int
    tests_failed: int
    tests_total: int
    all_passed: bool
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    provider_success: bool
    provider_error: str | None
    sandbox_error: str | None

    @property
    def quota_blocked(self) -> bool:
        """True when this cell was never actually evaluated because the
        provider rejected the call with a 429/quota error - distinct from a
        model genuinely generating wrong or broken code. Confirmed necessary
        the hard way: gemini-flash's free tier caps at a flat 20 requests
        (message: "limit: 20, model: gemini-3.5-flash"), and a cell blocked
        by that cap must not be counted as a capability failure in
        grading.py's pass rate."""
        return bool(self.provider_error) and ("429" in self.provider_error or "quota" in self.provider_error.lower())


def run_cell(task: Task, provider: ModelProvider, model_name: str, rep: int) -> Result:
    prompt = build_prompt(task)
    gen = provider.generate(prompt, system=SYSTEM_PROMPT)
    cost = provider.estimate_cost(gen.input_tokens, gen.output_tokens)

    if not gen.success or not gen.text:
        return Result(
            task_id=task.id, category=task.category, model=model_name, rep=rep,
            extracted_ok=False, ran=False, tests_passed=0, tests_failed=0, tests_total=0,
            all_passed=False, input_tokens=gen.input_tokens, output_tokens=gen.output_tokens,
            cost_usd=cost, latency_ms=gen.latency_ms, provider_success=gen.success,
            provider_error=gen.error, sandbox_error=None,
        )

    code = extract_code(gen.text)
    sandbox = run_against_tests(code, task.test_code, task.timeout_s)

    return Result(
        task_id=task.id, category=task.category, model=model_name, rep=rep,
        extracted_ok=bool(code.strip()), ran=sandbox.ran,
        tests_passed=sandbox.passed, tests_failed=sandbox.failed, tests_total=sandbox.total,
        all_passed=sandbox.all_passed, input_tokens=gen.input_tokens, output_tokens=gen.output_tokens,
        cost_usd=cost, latency_ms=gen.latency_ms, provider_success=gen.success, provider_error=gen.error,
        sandbox_error=sandbox.error,
    )


def run_grid(
    tasks: list[Task],
    providers: dict[str, ModelProvider],
    reps: int = 1,
    on_cell_done=None,
) -> list[Result]:
    results: list[Result] = []
    total = len(tasks) * len(providers) * reps
    done = 0
    for task in tasks:
        for model_name, provider in providers.items():
            for rep in range(reps):
                result = run_cell(task, provider, model_name, rep)
                results.append(result)
                done += 1
                if on_cell_done:
                    on_cell_done(done, total, result)
    return results


def write_results_csv(results: list[Result], path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(asdict(results[0]).keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))
