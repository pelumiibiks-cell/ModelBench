from modelbench.sandbox import run_against_tests

TEST_CODE = (
    "from solution import add\n\n"
    "def test_add():\n"
    "    assert add(2, 3) == 5\n\n"
    "def test_add_negative():\n"
    "    assert add(-1, 1) == 0\n"
)


def test_correct_solution_passes_all():
    code = "def add(a, b):\n    return a + b\n"
    result = run_against_tests(code, TEST_CODE, timeout_s=10)
    assert result.ran
    assert result.all_passed
    assert result.total == 2
    assert result.failed == 0


def test_wrong_solution_fails():
    code = "def add(a, b):\n    return a - b\n"
    result = run_against_tests(code, TEST_CODE, timeout_s=10)
    assert result.ran
    assert not result.all_passed
    assert result.failed >= 1


def test_syntax_error_does_not_crash_the_runner():
    code = "def add(a, b:\n    return a + b\n"  # missing closing paren
    result = run_against_tests(code, TEST_CODE, timeout_s=10)
    assert not result.all_passed


def test_wrong_function_name_fails_cleanly():
    code = "def plus(a, b):\n    return a + b\n"
    result = run_against_tests(code, TEST_CODE, timeout_s=10)
    assert not result.all_passed


def test_infinite_loop_times_out_instead_of_hanging():
    code = "def add(a, b):\n    while True:\n        pass\n"
    result = run_against_tests(code, TEST_CODE, timeout_s=2)
    assert not result.ran
    assert result.error is not None
    assert "timed out" in result.error
