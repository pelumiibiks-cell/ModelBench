from modelbench.extract import extract_code


def test_extracts_fenced_python_block():
    text = "Here is the code:\n```python\ndef f():\n    return 1\n```\nDone."
    assert extract_code(text) == "def f():\n    return 1"


def test_extracts_bare_fence_without_language_tag():
    text = "```\ndef f():\n    return 1\n```"
    assert extract_code(text) == "def f():\n    return 1"


def test_falls_back_to_raw_text_when_no_fence():
    text = "def f():\n    return 1"
    assert extract_code(text) == "def f():\n    return 1"


def test_picks_first_fence_when_multiple_present():
    text = "```python\ndef first():\n    pass\n```\nsome text\n```python\ndef second():\n    pass\n```"
    assert "def first" in extract_code(text)
    assert "def second" not in extract_code(text)
