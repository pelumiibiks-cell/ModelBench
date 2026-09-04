"""Runs a candidate solution against a task's hidden pytest file, in a
subprocess so a candidate's infinite loop or crash can't take the whole
benchmark run down with it.

Scope note, stated plainly rather than implied: this is process and
wall-clock isolation (a timeout-bounded subprocess), not a network- or
filesystem-denied sandbox. That's an intentional scope call, not an
oversight - every task in this benchmark is self-authored and synthetic
(see docs/overview.md), so the candidate code being executed was never
untrusted input from outside this project. A benchmark grading real
third-party or user-submitted code would need real sandboxing (a container,
gVisor, or similar); this one doesn't have that threat model.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SandboxResult:
    ran: bool
    passed: int
    failed: int
    total: int
    output: str
    error: str | None = None

    @property
    def all_passed(self) -> bool:
        return self.ran and self.total > 0 and self.failed == 0


def run_against_tests(candidate_code: str, test_code: str, timeout_s: float) -> SandboxResult:
    with tempfile.TemporaryDirectory(prefix="modelbench_") as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "solution.py").write_text(candidate_code, encoding="utf-8")
        (tmp_path / "test_task.py").write_text(test_code, encoding="utf-8")

        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_task.py", "-q", "--no-header"],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(ran=False, passed=0, failed=0, total=0, output="", error=f"timed out after {timeout_s}s")

        output = proc.stdout + proc.stderr
        passed, failed, total = _parse_pytest_summary(output)
        # Exit code 1 with zero tests collected means the candidate code raised
        # at import/collection time (syntax error, wrong function name, etc.) -
        # a real failure, but distinguished from "tests ran and some failed" so
        # report.py can break out "didn't even run" separately.
        ran = proc.returncode in (0, 1) and total > 0
        return SandboxResult(ran=ran, passed=passed, failed=failed, total=total, output=output)


def _parse_pytest_summary(output: str) -> tuple[int, int, int]:
    """Parses pytest's own short summary line rather than re-deriving pass/fail
    from stdout formatting, since that line's wording is pytest's stable public
    contract, not an implementation detail this project would need to track."""
    passed = failed = 0
    for line in output.splitlines():
        line = line.strip()
        if " passed" in line or " failed" in line or " error" in line:
            for token in line.split(", "):
                token = token.strip()
                if token.endswith(" passed") or " passed" in token:
                    passed = _leading_int(token)
                elif token.endswith(" failed") or " failed" in token:
                    failed = _leading_int(token)
                elif token.endswith(" error") or token.endswith(" errors") or " error" in token:
                    failed += _leading_int(token)
    return passed, failed, passed + failed


def _leading_int(token: str) -> int:
    digits = ""
    for ch in token.strip():
        if ch.isdigit():
            digits += ch
        elif digits:
            break
    return int(digits) if digits else 0
