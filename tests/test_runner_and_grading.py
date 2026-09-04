from modelbench.grading import find_overkill_categories, summarize_by_model, summarize_by_model_category
from modelbench.providers.offline import OfflineProvider
from modelbench.runner import run_cell, run_grid
from modelbench.tasks import Task

ADD_TASK = Task(
    id="test_add",
    category="trivial",
    prompt="Write a function that adds two numbers.",
    entry_point="add",
    reference_solution="def add(a, b):\n    return a + b\n",
    test_code="from solution import add\n\ndef test_add():\n    assert add(2, 3) == 5\n",
)


def test_run_cell_with_correct_offline_response_passes():
    provider = OfflineProvider(responses={"": "```python\ndef add(a, b):\n    return a + b\n```"})
    result = run_cell(ADD_TASK, provider, "stub-model", rep=0)
    assert result.all_passed
    assert result.provider_success


def test_run_cell_with_wrong_offline_response_fails():
    provider = OfflineProvider(responses={"": "```python\ndef add(a, b):\n    return a - b\n```"})
    result = run_cell(ADD_TASK, provider, "stub-model", rep=0)
    assert not result.all_passed


def test_run_cell_with_empty_response_does_not_crash():
    provider = OfflineProvider(default="")
    result = run_cell(ADD_TASK, provider, "stub-model", rep=0)
    assert not result.all_passed
    assert not result.provider_success


def test_run_grid_covers_every_task_model_rep_combination():
    good = OfflineProvider(name="good", responses={"": "```python\ndef add(a, b):\n    return a + b\n```"})
    bad = OfflineProvider(name="bad", responses={"": "```python\ndef add(a, b):\n    return a - b\n```"})
    results = run_grid([ADD_TASK], {"good": good, "bad": bad}, reps=2)
    assert len(results) == 1 * 2 * 2

    summaries = {s.model: s for s in summarize_by_model(results)}
    assert summaries["good"].pass_rate == 1.0
    assert summaries["bad"].pass_rate == 0.0


def test_summarize_by_model_category_breaks_down_correctly():
    good = OfflineProvider(name="good", responses={"": "```python\ndef add(a, b):\n    return a + b\n```"})
    results = run_grid([ADD_TASK], {"good": good}, reps=1)
    cat_summaries = summarize_by_model_category(results)
    assert len(cat_summaries) == 1
    assert cat_summaries[0].category == "trivial"
    assert cat_summaries[0].pass_rate == 1.0


def test_find_overkill_categories_flags_equal_performance():
    cheap = OfflineProvider(name="cheap", responses={"": "```python\ndef add(a, b):\n    return a + b\n```"})
    costly = OfflineProvider(name="costly", responses={"": "```python\ndef add(a, b):\n    return a + b\n```"})
    results = run_grid([ADD_TASK], {"cheap": cheap, "costly": costly}, reps=1)
    overkill = find_overkill_categories(results, cheap_model="cheap", expensive_model="costly")
    assert overkill == ["trivial"]


def test_find_overkill_categories_excludes_when_expensive_model_wins():
    cheap = OfflineProvider(name="cheap", responses={"": "```python\ndef add(a, b):\n    return a - b\n```"})
    costly = OfflineProvider(name="costly", responses={"": "```python\ndef add(a, b):\n    return a + b\n```"})
    results = run_grid([ADD_TASK], {"cheap": cheap, "costly": costly}, reps=1)
    overkill = find_overkill_categories(results, cheap_model="cheap", expensive_model="costly")
    assert overkill == []
