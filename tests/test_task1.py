"""Модуль тестов для функции sum_two из task1.solution."""

import pytest
from task1.solution import sum_two


@pytest.mark.type
def test_sum_two_correct_types():
    """
    Тестирует sum_two с корректными типами аргументов (int).

    Ожидается правильное суммирование.
    """
    assert sum_two(1, 2) == 3


@pytest.mark.type
def test_sum_two_incorrect_type():
    """
    Тестирует sum_two с некорректным типом аргумента (float).

    Ожидается возбуждение TypeError.
    """
    with pytest.raises(TypeError) as exc_info:
        sum_two(1, 2.4)
    assert "TypeError" in str(exc_info.value)
