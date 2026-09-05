# ModelBench

A coding-task benchmark for Gemini models: 24 self-authored tasks, each graded deterministically by running the model's own generated code against a hidden pytest file, not by asking another model to judge it. It answers one question with evidence instead of assumption: **is the cheap tier good enough for a given class of coding task, or does it cost more in failed output than it saves in per-call price?**

Built to close a real gap in a sibling project, [RouteIQ](https://github.com/pelumiibiks-cell/RouteIQ), which routes prompts to the model it thinks is cheapest-sufficient but never actually runs one. Its evaluation is entirely against a `MockProvider`. This benchmark executes real models against real tasks and grades the output for real.

Plain-language walkthrough, full results, and every caveat: [`docs/overview.md`](docs/overview.md).

**Headline result from the first real run:** `gemini-flash`'s free tier hit a hard 20-request daily cap partway through (8/24 cells never evaluated), while `gemini-flash-lite` completed the full grid. On the cells `flash` did complete, its pass rate was statistically indistinguishable from `flash-lite`'s (93.8% vs 95.8%) at roughly **5x the cost per passing task**. `flash`'s entire `hard` category is unevaluated, so this can't yet say whether the pricier tier separates itself on harder work. See `docs/overview.md` for the full breakdown, the quota-blocked accounting, and what's still open.

## What it does

For every (task, model) pair: sends the task's spec to the model, extracts the returned Python function from its response, runs it in a timeout-bounded subprocess against that task's hidden test file, and records pass/fail plus token counts, cost, and latency. No task's hidden tests are ever shown to the model being graded, the same split [ChessLens](https://github.com/pelumiibiks-cell/ChessLens)'s `Explanation`/`verify_explanation` uses, where the thing being judged never sees the check.

24 tasks span 7 categories, not a flat difficulty curve:

- **trivial** (5), **standard** (7), **hard** (5): a real difficulty spread, not a flat set.
- **adversarial_short_hard** (2), **adversarial_long_trivial** (2), **adversarial_keyword_easy** (2): tasks that look easy by length or keyword density but require real reasoning, and vice versa. The instinct here is borrowed from [RouteIQ's own evaluation dataset](https://github.com/pelumiibiks-cell/RouteIQ), which found these traps catch real routing mistakes a flat task list would hide.
- **underspecified** (1): a task with no schema and no definition of "correct," graded on whether the response makes a reasonable assumption and doesn't crash, not on an exact-match answer.

A small, separate LLM-judge layer exists for the one thing pass/fail can't grade, code *readability*, not correctness, and it ships with its own calibration check (`modelbench calibrate-judge`) before any judged score is trusted, the same discipline [Malator](https://github.com/pelumiibiks-cell/Clinical-RAG-Agent)'s `judge_sanity_check.py` used after noticing its own judge had never once scored a real answer below 1.0.

## Install

```bash
pip install -e ".[dev]"
cp .env.example .env   # add your GEMINI_API_KEY
pytest -q              # 46 tests, including every task's reference solution against its own hidden tests
```

## Run it

```bash
modelbench run --reps 1              # full 24-task x 2-model grid, writes results/benchmark_raw.csv
modelbench calibrate-judge           # sanity-check the judge before trusting the quality-scored slice
```

## Scope, stated plainly

- **Gemini only**: `gemini-flash` vs `gemini-flash-lite`. No Anthropic/OpenAI comparison in this version; the provider interface is shaped to match RouteIQ's `ModelProvider` specifically so a second provider slots in later without a rewrite, but v1 ships and is written up on what's actually available.
- **Self-authored tasks only**: every task, reference solution, and hidden test in `tasks/` was written for this project. No HumanEval/MBPP problems are reused, verbatim or paraphrased.
- **Process/timeout sandboxing, not network-denial sandboxing.** Candidate code runs in a subprocess with a wall-clock timeout, which is the right scope for grading self-authored synthetic tasks with no untrusted external input. See `modelbench/sandbox.py`'s docstring for the explicit boundary.

## Tech stack

Python 3.11+, `google-genai` (Interactions API, `client.interactions.create`, not the older `generate_content`), Pydantic for the judge's structured output, PyYAML for the task files, pytest as both the dev tool and the grading mechanism.

## Project structure

```
modelbench/
  config.py       Gemini model registry (pricing, API model ids) and .env loading
  providers/      GeminiProvider (live) and OfflineProvider (zero-cost, for testing the pipeline itself)
  tasks.py        Task dataclass + YAML loader
  extract.py      Pulls a candidate solution's code out of a model's raw text response
  sandbox.py      Runs candidate code against a task's hidden tests in a subprocess
  runner.py       The task x model x rep grid
  grading.py      Deterministic pass-rate aggregation, no judge involved
  judge.py        The separate, calibrated LLM-judge layer for the quality-scored slice
  report.py       Results -> the markdown tables this README and docs/overview.md quote
tasks/*.yaml      The 24 task definitions (prompt, entry point, reference solution, hidden tests)
scripts/generate_tasks.py   How the task YAML files were authored; re-run after editing a task
```
