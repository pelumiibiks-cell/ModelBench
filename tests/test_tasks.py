import pytest

from modelbench.sandbox import run_against_tests
from modelbench.tasks import CATEGORIES, load_tasks


def test_loads_all_task_files():
    tasks = load_tasks()
    assert len(tasks) >= 20


def test_every_task_has_a_valid_category():
    for task in load_tasks():
        assert task.category in CATEGORIES


def test_task_ids_are_unique():
    tasks = load_tasks()
    ids = [t.id for t in tasks]
    assert len(ids) == len(set(ids))


def test_every_category_has_at_least_one_task():
    tasks = load_tasks()
    present = {t.category for t in tasks}
    assert present == set(CATEGORIES)


@pytest.mark.parametrize("task", load_tasks(), ids=lambda t: t.id)
def test_reference_solution_passes_its_own_hidden_tests(task):
    """The load-bearing check: if a task's own reference solution can't pass
    the hidden tests it's graded against, the task is broken and every
    model would unfairly fail it, regardless of how good the model is."""
    result = run_against_tests(task.reference_solution, task.test_code, task.timeout_s)
    assert result.ran, f"{task.id}: reference solution did not run cleanly: {result.output}"
    assert result.all_passed, f"{task.id}: reference solution failed its own tests:\n{result.output}"
