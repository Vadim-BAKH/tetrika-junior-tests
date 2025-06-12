"""
Модуль с декоратором strict для строгой проверки типов аргументов функций.

Декоратор strict проверяет типы аргументов функции на основе аннотаций
и выбрасывает TypeError при несовпадении типов.
"""

import inspect
from functools import wraps
from typing import Callable


def strict(func) -> Callable:
    """
    Декоратор, проверяющий типы аргументов функции согласно её аннотациям.

    При вызове функции проверяет, что типы переданных аргументов совпадают
    с ожидаемыми типами, указанными в аннотациях. Если тип не совпадает,
    возбуждает исключение TypeError.

    Args:
        func (callable): Функция, к которой применяется декоратор.

    Returns:
        callable: Обёрнутая функция с проверкой типов.
    """
    sig = inspect.signature(func)
    annotations = func.__annotations__

    @wraps(func)
    def wrapper(*args, **kwargs) -> object:
        some = sig.bind(*args, **kwargs)
        some.apply_defaults()
        for name, value in some.arguments.items():
            if name in annotations:
                expected_type = annotations[name]
                if not isinstance(value, expected_type):
                    raise TypeError("TypeError")
        return func(*args, **kwargs)

    return wrapper


@strict
def sum_two(a: int, b: int) -> int:
    """
    Складывает два целочисленных аргумента.

    Args:
        a (int): Первый слагаемый.
        b (int): Второй слагаемый.

    Returns:
        int: Сумма a и b.

    Raises:
        TypeError: Если типы аргументов не int.
    """
    return a + b


if __name__ == "__main__":
    print(sum_two(1, 2))  # >>> 3
    try:
        print(sum_two(1, 2.4))  # >>> TypeError
    except TypeError as ter:
        print(ter)
