# ModelBench results — run of 2026-09-04

Generated from `results/benchmark_raw.csv` (48 rows: 24 tasks x 2 models x 1 rep) via `modelbench/report.py`. Full narrative and caveats: [`../docs/overview.md`](../docs/overview.md).

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

`gemini-flash`'s 8 quota-blocked cells all returned the same error: `429 - Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.5-flash`. Every failure that isn't quota-blocked is a real, evaluated failure. See `benchmark_raw.csv`'s `provider_error`/`sandbox_error` columns for the specific cause per cell.
