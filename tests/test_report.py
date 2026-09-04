from modelbench.providers.offline import OfflineProvider
from modelbench.report import category_table, model_summary_table
from modelbench.runner import run_grid
from modelbench.tasks import Task

ADD_TASK = Task(
    id="test_add",
    category="trivial",
    prompt="Write a function that adds two numbers.",
    entry_point="add",
    reference_solution="def add(a, b):\n    return a + b\n",
    test_code="from solution import add\n\ndef test_add():\n    assert add(2, 3) == 5\n",
)


def test_model_summary_table_contains_model_names_and_pass_rate():
    good = OfflineProvider(name="good-model", responses={"": "```python\ndef add(a, b):\n    return a + b\n```"})
    results = run_grid([ADD_TASK], {"good-model": good}, reps=1)
    table = model_summary_table(results)
    assert "good-model" in table
    assert "100.0%" in table


def test_category_table_contains_category_name():
    good = OfflineProvider(name="good-model", responses={"": "```python\ndef add(a, b):\n    return a + b\n```"})
    results = run_grid([ADD_TASK], {"good-model": good}, reps=1)
    table = category_table(results)
    assert "trivial" in table
    assert "good-model" in table
