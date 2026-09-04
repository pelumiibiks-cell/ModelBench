"""Task definitions and loading. Each task lives as one YAML file under
tasks/, with the model-facing prompt kept strictly separate from the hidden
pytest file it's graded against - the same split ChessLens's
Explanation/verify_explanation uses: the thing being judged never sees the
check.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from modelbench.config import TASKS_DIR

# Categories exist to keep the difficulty spread honest and checkable, not
# as decoration - report.py breaks results down by category, and the
# adversarial ones exist specifically because RouteIQ's own evaluation
# dataset proved short-but-hard / long-but-trivial traps catch routing
# mistakes that a flat task list would hide.
CATEGORIES = (
    "trivial",
    "standard",
    "hard",
    "adversarial_short_hard",
    "adversarial_long_trivial",
    "adversarial_keyword_easy",
    "underspecified",
)


@dataclass(frozen=True)
class Task:
    id: str
    category: str
    prompt: str
    entry_point: str
    reference_solution: str
    test_code: str
    timeout_s: float = 10.0

    def __post_init__(self) -> None:
        if self.category not in CATEGORIES:
            raise ValueError(f"task {self.id!r}: unknown category {self.category!r}, expected one of {CATEGORIES}")


def _load_one(path: Path) -> Task:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = {"id", "category", "prompt", "entry_point", "reference_solution", "test_code"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"{path}: missing required field(s) {sorted(missing)}")
    return Task(
        id=data["id"],
        category=data["category"],
        prompt=data["prompt"].strip(),
        entry_point=data["entry_point"],
        reference_solution=data["reference_solution"],
        test_code=data["test_code"],
        timeout_s=float(data.get("timeout_s", 10.0)),
    )


def load_tasks(tasks_dir: Path | str | None = None) -> list[Task]:
    directory = Path(tasks_dir) if tasks_dir else TASKS_DIR
    paths = sorted(directory.glob("*.yaml"))
    tasks = [_load_one(p) for p in paths]
    ids = [t.id for t in tasks]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise ValueError(f"duplicate task id(s) found: {sorted(duplicates)}")
    return tasks
