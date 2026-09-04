"""modelbench run [--reps N] [--out PATH]
modelbench calibrate-judge
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from modelbench.config import RESULTS_DIR, REGISTRY, get_gemini_api_key
from modelbench.judge import run_calibration
from modelbench.providers.gemini import GeminiProvider
from modelbench.report import category_table, model_summary_table
from modelbench.runner import run_grid, write_results_csv
from modelbench.tasks import load_tasks


def cmd_run(args: argparse.Namespace) -> int:
    api_key = get_gemini_api_key()
    if not api_key:
        print("No GEMINI_API_KEY set. Add it to .env.", file=sys.stderr)
        return 1

    tasks = load_tasks()
    providers = {name: GeminiProvider(profile, api_key) for name, profile in REGISTRY.items()}

    total = len(tasks) * len(providers) * args.reps
    print(f"Running {len(tasks)} tasks x {len(providers)} models x {args.reps} rep(s) = {total} generations...", flush=True)

    def _progress(done: int, total: int, result) -> None:
        mark = "PASS" if result.all_passed else "FAIL"
        print(f"[{done}/{total}] {result.task_id} x {result.model} rep{result.rep}: {mark} "
              f"({result.tests_passed}/{result.tests_total} tests, {result.latency_ms:.0f}ms)", flush=True)

    results = run_grid(tasks, providers, reps=args.reps, on_cell_done=_progress)

    out_path = Path(args.out) if args.out else RESULTS_DIR / "benchmark_raw.csv"
    write_results_csv(results, out_path)
    print(f"Wrote {len(results)} rows to {out_path}")

    print("\n" + model_summary_table(results))
    print("\n" + category_table(results))
    return 0


def cmd_calibrate_judge(args: argparse.Namespace) -> int:
    api_key = get_gemini_api_key()
    if not api_key:
        print("No GEMINI_API_KEY set. Add it to .env.", file=sys.stderr)
        return 1

    judge_provider = GeminiProvider(REGISTRY["gemini-flash-lite"], api_key)
    rows = run_calibration(judge_provider)

    out_path = RESULTS_DIR / "judge_calibration_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    all_separated = all(r["separated"] for r in rows)
    for r in rows:
        mark = "OK" if r["separated"] else "FAILED TO SEPARATE"
        print(f"{r['id']}: good={r['good_score']:.2f} bad={r['bad_score']:.2f}  [{mark}]")
    print(f"\nWrote {out_path}")
    if not all_separated:
        print("\nWARNING: judge did not separate good/bad on every case. "
              "Do not trust the quality-scored slice until this is fixed.", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="modelbench")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run the full task x model grid against the live Gemini API.")
    p_run.add_argument("--reps", type=int, default=1, help="Repetitions per (task, model) cell.")
    p_run.add_argument("--out", default=None, help="Output CSV path (default: results/benchmark_raw.csv).")
    p_run.set_defaults(func=cmd_run)

    p_cal = sub.add_parser("calibrate-judge", help="Sanity-check the LLM judge before trusting the quality-scored slice.")
    p_cal.set_defaults(func=cmd_calibrate_judge)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
