from typing import Any, Callable, Literal

import pytest

from grimoire.processing import Processor


# Mock action functions for testing
def mock_action(a: int, b: int = 2) -> int:
    return a + b


def mock_action_no_return(a: int, b: int = 2):
    pass


def mock_action_with_error(a: int, b: int = 2) -> int:
    raise TypeError("Intentional Error")


@pytest.mark.parametrize(
    "action, required_kwargs, optional_kwargs, return_kwargs, expected_required, expected_optional, expected_return, expected_warning",
    [
        # Happy path
        (mock_action, None, None, None, {"a": int}, {"b": int}, int, False),
        # Edge case: no return annotation
        (mock_action_no_return, None, None, None, {"a": int}, {"b": int}, None, True),
        # Error case: action raises TypeError
        (mock_action_with_error, None, None, None, {"a": int}, {"b": int}, None, True),
        # Provided kwargs
        (
            mock_action,
            {"a": int},
            {"b": int},
            {"return": int},
            {"a": int},
            {"b": int},
            {"return": int},
            False,
        ),
    ],
    ids=[
        "happy_path",
        "no_return_annotation",
        "action_raises_type_error",
        "provided_kwargs",
    ],
)
def test_processor_init(
    action,
    required_kwargs,
    optional_kwargs,
    return_kwargs,
    expected_required,
    expected_optional,
    expected_return,
    expected_warning,
    caplog,
):

    # Act
    processor = Processor(action, required_kwargs, optional_kwargs, return_kwargs)

    # Assert
    assert processor.action == action
    assert processor.required_kwargs == expected_required
    assert processor.optional_kwargs == expected_optional
    assert processor.return_kwargs == expected_return
    if expected_warning:
        assert any(record.levelname == "WARNING" for record in caplog.records)
    else:
        assert all(record.levelname != "WARNING" for record in caplog.records)
