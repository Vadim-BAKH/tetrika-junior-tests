"""
Модуль для вычисления суммарного времени пересечения.

Считает интервалы присутствия ученика и учителя в рамках урока.
Функция appearance принимает словарь с интервалами урока, ученика и учителя,
обрабатывает интервалы, объединяет пересечения и возвращает общее время,
в течение которого ученик и учитель одновременно присутствовали на уроке.
"""


def process_intervals(
    raw_intervals: list[int], lesson_start: int, lesson_end: int
) -> list[tuple[int, int]]:
    """
    Обрабатывает сырые интервалы.

    Обрезает по времени урока, сортирует и объединяет пересечения.
    Args:
        raw_intervals (list[int]):
        Список временных меток начала и конца интервалов.
        lesson_start (int): Время начала урока.
        lesson_end (int): Время окончания урока.

    Returns:
        list[tuple[int, int]]: Список объединённых интервалов (start, end).
    """
    processed = []
    for i_ind in range(0, len(raw_intervals), 2):
        start = max(raw_intervals[i_ind], lesson_start)
        end = min(raw_intervals[i_ind + 1], lesson_end)
        if start < end:
            processed.append((start, end))

    processed.sort()
    merged = []
    for interval in processed:
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], interval[1]))
    return merged


def appearance(intervals: dict[str, list[int]]) -> int:
    """
    Вычисляет суммарное время пересечения интервалов
    ученика и учителя в пределах урока.

    Args:
        intervals (dict[str, list[int]]):
        Словарь с ключами 'lesson', 'pupil', 'tutor',
            где каждый ключ содержит список временных
            меток начала и конца интервалов.
    Returns:
        int: Общее время пересечения интервалов
        ученика и учителя, ограниченное временем урока.
    """
    lesson_start, lesson_end = intervals["lesson"]

    pupil = process_intervals(intervals["pupil"], lesson_start, lesson_end)
    tutor = process_intervals(intervals["tutor"], lesson_start, lesson_end)

    total = 0
    p_idx = t_idx = 0

    while p_idx < len(pupil) and t_idx < len(tutor):
        p_start, p_end = pupil[p_idx]
        t_start, t_end = tutor[t_idx]

        overlap_start = max(p_start, t_start)
        overlap_end = min(p_end, t_end)

        if overlap_start < overlap_end:
            total += overlap_end - overlap_start

        if p_end < t_end:
            p_idx += 1
        else:
            t_idx += 1

    return total


tests = [
    {
        "intervals": {
            "lesson": [1594663200, 1594666800],
            "pupil": [
                1594663340,
                1594663389,
                1594663390,
                1594663395,
                1594663396,
                1594666472,
            ],
            "tutor": [1594663290, 1594663430, 1594663443, 1594666473],
        },
        "answer": 3117,
    },
    {
        "intervals": {
            "lesson": [1594702800, 1594706400],
            "pupil": [
                1594702789,
                1594704500,
                1594702807,
                1594704542,
                1594704512,
                1594704513,
                1594704564,
                1594705150,
                1594704581,
                1594704582,
                1594704734,
                1594705009,
                1594705095,
                1594705096,
                1594705106,
                1594706480,
                1594705158,
                1594705773,
                1594705849,
                1594706480,
                1594706500,
                1594706875,
                1594706502,
                1594706503,
                1594706524,
                1594706524,
                1594706579,
                1594706641,
            ],
            "tutor": [
                1594700035,
                1594700364,
                1594702749,
                1594705148,
                1594705149,
                1594706463,
            ],
        },
        "answer": 3577,
    },
    {
        "intervals": {
            "lesson": [1594692000, 1594695600],
            "pupil": [1594692033, 1594696347],
            "tutor": [1594692017, 1594692066, 1594692068, 1594696341],
        },
        "answer": 3565,
    },
]

if __name__ == "__main__":
    for i, test in enumerate(tests):
        test_answer = appearance(test["intervals"])
        assert test_answer == test["answer"], (
            f"Error on test case {i},"
            f" got {test_answer},"
            f' expected {test["answer"]}'
        )
