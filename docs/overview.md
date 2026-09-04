# ModelBench — full explanation

## The problem it answers

RouteIQ, a sibling project, decides which LLM tier a prompt should be routed to — cheap-and-fast versus expensive-and-strong — based on a utility function that weighs quality, cost, latency, and the risk of over- or under-powering the request. That routing logic is real and tested (34 tests, a 24-case labeled evaluation dataset), but it has never actually run a model. Every "generation" in RouteIQ's deployed evaluation is a deterministic `MockProvider`. So the question RouteIQ's whole design rests on — *is the cheap tier actually good enough for the tasks it gets routed to?* — has never been tested against a real model's real output.

ModelBench tests it. It sends 24 self-authored coding tasks to two real Gemini tiers (`gemini-flash` and `gemini-flash-lite`), runs each model's generated code against a hidden pytest file per task, and reports where the cheap tier holds up and where it doesn't — with cost and latency attached to every result, so "good enough" can be weighed against "how much did the gap cost."

## Why deterministic grading, not an LLM judge

A judge model scoring code correctness has the same weakness Malator's `judge_sanity_check.py` was built to catch: a judge that's never been shown a wrong answer might just be rubber-stamping everything as fine. Rather than build that risk into the primary metric, ModelBench grades on pytest pass/fail wherever a task's correctness is checkable that way — which is every task except the underspecified one. The result is a number that doesn't need a second model to vouch for it.

The one place a judge earns its keep is *readability*, which no test can grade (correct code can still be unreadable). That slice is small, clearly separated from the pass-rate numbers, and calibrated first — `modelbench calibrate-judge` runs the judge against three hand-built (good, bad) code pairs and refuses to certify itself if it can't tell them apart. Run live against `gemini-flash-lite`: the judge scored every "good" sample 1.00 and every "bad" one between 0.10 and 0.40 — a clean separation on all three cases, not a rubber stamp (`results/judge_calibration_results.json`).

## The task set

24 tasks, 7 categories, authored specifically for this project (see `scripts/generate_tasks.py` for how):

- **trivial (5), standard (7), hard (5)** — a genuine difficulty spread. Trivial tasks (sum a list, reverse a string) exist as a floor: any model that fails these has a pipeline problem, not a capability problem. Hard tasks (median of two sorted arrays in log time, regex matching with backtracking, Levenshtein distance) are where a real capability gap should show up.
- **adversarial_short_hard (2)** — short prompts that hide real difficulty (counting change-making combinations, next-permutation). A model that estimates difficulty by prompt length would underrate these.
- **adversarial_long_trivial (2)** — long, corporate-sounding prompts wrapped around a trivial task (compute a mean; filter strings by length). Tests whether verbosity inflates a model's apparent effort without inflating the actual task.
- **adversarial_keyword_easy (2)** — prompts stuffed with impressive-sounding keywords ("distributed, thread-safe, fault-tolerant...") around a task as simple as adding two numbers. Tests whether keyword density fools a difficulty estimate.
- **underspecified (1)** — no schema, no definition of "clean." Graded on whether the response makes a reasonable assumption and doesn't crash, not on an exact answer.

The adversarial-category instinct is a direct reuse of RouteIQ's own evaluation dataset design (`short-but-hard`, `long-but-trivial`, `keyword-heavy-but-easy` traps), which proved these categories catch real difficulty-estimation mistakes rather than testing anything contrived.

Every reference solution is checked, as part of this repo's own test suite, to actually pass its own task's hidden tests — 24 of the 46 tests in `pytest -q` are exactly this: if a task's own correct answer can't pass its own grading, every model would unfairly fail it regardless of capability, so this is checked before any model is ever run against it.

## Grading mechanics

For each (task, model) pair: the task's prompt is sent with a system instruction asking for only a fenced Python code block, no commentary. `extract.py` pulls the first fenced block out of the response (or falls back to the raw text if the model skipped the fence). That code is written to a temp directory alongside the task's hidden test file and run via `pytest` in a subprocess with a per-task timeout — process and wall-clock isolation, not a network-denied sandbox, since every task here is self-authored and synthetic (see `sandbox.py`'s docstring for the explicit scope call).

## Results

Run against the live Gemini API, 1 repetition per cell (48 generations total). Raw per-cell data: `results/benchmark_raw.csv`.

**Headline finding: `gemini-flash`'s free tier hit a hard request cap partway through the run — this is itself the most operationally useful result, not a footnote.** 8 of 24 `gemini-flash` cells returned a 429 with `"Quota exceeded... limit: 20, model: gemini-3.5-flash"` — a flat daily cap of 20 free-tier requests. `gemini-flash-lite` completed all 24 cells with no such block. Those 8 cells (the entire `hard` and `underspecified` categories) were never evaluated and are excluded from `flash`'s pass rate below, not counted as failures — reported as `n/a (quota-blocked)` in the category table. Anyone deciding what to actually build against on a free Gemini key should know this going in: the pricier tier is close to unusable for anything beyond light manual testing without billing enabled, independent of how good the model itself is.

| Model | Evaluated | Quota-blocked | Pass rate (of evaluated) | Total cost (USD) | Cost / passing task | Mean latency (ms) |
|---|---|---|---|---|---|---|
| gemini-flash | 16/24 | 8 | 93.8% | $0.04042 | $0.00269 | 9315 |
| gemini-flash-lite | 24/24 | 0 | 95.8% | $0.01245 | $0.00054 | 9474 |

| Category | gemini-flash | gemini-flash-lite |
|---|---|---|
| trivial | 100.0% (5/5) | 100.0% (5/5) |
| standard | 100.0% (5/7) | 100.0% (7/7) |
| hard | n/a (quota-blocked) | 100.0% (5/5) |
| adversarial_short_hard | 100.0% (2/2) | 100.0% (2/2) |
| adversarial_long_trivial | 100.0% (2/2) | 100.0% (2/2) |
| adversarial_keyword_easy | 50.0% (2/2) | 50.0% (2/2) |
| underspecified | n/a (quota-blocked) | 100.0% (1/1) |

**On the tasks flash actually got to run, it did not earn its price.** Pass rate is statistically indistinguishable from flash-lite (93.8% vs 95.8%, on comparable small sample sizes), but flash costs roughly **5x more per passing task** ($0.00269 vs $0.00054). Nothing in this run's evaluated cells supports paying flash's price over flash-lite's for this task mix — the honest caveat is that flash's entire `hard`-tier result is unknown, since every one of those cells was quota-blocked before it could run, so this finding cannot yet say whether flash would have separated itself on the harder half of the task set. That's explicit unfinished business, not a result being claimed.

**The one task both models failed (`a05_keyword_heavy_easy`) illustrates exactly what its category is designed to catch.** The prompt buries a two-line add-two-numbers task under buzzwords ("distributed, thread-safe, asynchronous, fault-tolerant, horizontally-scalable microservice-ready..."). A follow-up diagnostic call on the same prompt (not the original graded cell — raw responses aren't currently persisted per cell, see Known limitations) shows the model responding by fabricating an entire mock distributed-systems framework around the addition: a singleton service registry, a circuit breaker with failure-threshold state, a semaphore-gated async execution pipeline, and a dedicated background event loop thread — all to add two numbers. That follow-up call happened to pass its tests, but code this elaborate for a task this trivial is inherently more fragile (thread startup timing, event-loop lifecycle) than a one-line implementation, which is a plausible, though not certain, explanation for why the original graded cell failed. Even when it works, it is a clear case of a model paying (in tokens, latency, and fragility) for imagined requirements the prompt's keywords implied but the actual spec never asked for — the concrete version of "wasted money" this whole project set out to find.

## Known limitations

- **Raw model responses are not persisted per cell.** `results/benchmark_raw.csv` records pass/fail, test counts, tokens, cost, and latency, but not the generated code itself, so root-causing a specific failed cell after the fact (as done above for `a05`, via a fresh call rather than the original one) is not always possible from the results file alone. A reasonable next step, not built here to keep this version's scope proportionate.
- **`gemini-flash`'s `hard` and `underspecified` categories are entirely unevaluated**, blocked by the free-tier daily cap described above. Re-running just those two categories against `flash` once the cap resets (a new day, or a billed key) would close the one real gap in this result set.
- **n=1 repetition per cell.** A single run distinguishes a real capability gap from one unlucky sample less reliably than the reject-inference project's 150-repetition Monte Carlo grid could. Increasing `--reps` is the direct fix, gated by the same free-tier quota this run just hit.

## What this does and doesn't tell you about RouteIQ

A finding here that flash-lite matches flash on some category is real evidence that a router shouldn't pay flash's price for that category — but it's evidence about Gemini's two tiers specifically, not a validation of RouteIQ's own utility function, since RouteIQ has never routed a real prompt to a real model. Closing that second gap — running RouteIQ's actual router against real provider calls — is explicit future work, not something this benchmark claims to have already done.
