"""
Модуль тестов для функций из task2.solution.

Покрывает тесты для:
- сбор всех страниц с категориями животных,
- асинхронного получения данных,
- парсинга и сохранения результатов.
"""

import asyncio
from collections import defaultdict
from unittest.mock import MagicMock, patch

import pytest
from task2.solution import (collect_all_pages, fetch, parse_all,
                            parse_and_save, save_to_csv_async)


@patch("task2.solution.requests.get")
@pytest.mark.animals
def test_collect_all_pages(mock_get):
    """
    Тестирует функцию collect_all_pages.

    Проверяет правильность сбора ссылок с нескольких страниц,
    включая наличие и отсутствие ссылки "Следующая страница".
    """
    html_page1 = """
    <a href="/w/index.php?title=Категория:
    Животные_по_алфавиту&pagefrom=Б" >Следующая страница</a>
    """
    html_page2 = """
    <!-- Нет ссылки "Следующая страница" -->
    """
    mock_resp1 = MagicMock()
    mock_resp1.text = html_page1
    mock_resp1.raise_for_status = lambda: None

    mock_resp2 = MagicMock()
    mock_resp2.text = html_page2
    mock_resp2.raise_for_status = lambda: None

    mock_get.side_effect = [mock_resp1, mock_resp2]

    urls = collect_all_pages()
    assert len(urls) == 2
    assert urls[0].endswith("Категория:Животные_по_алфавиту")
    assert "pagefrom=Б" in urls[1]


@pytest.mark.asyncio
@pytest.mark.animals
async def test_fetch():
    """
    Тестирует асинхронную функцию fetch.

    Проверяет, что функция корректно парсит HTML,
    и считает количество животных по первой букве.
    """
    html = """
    <div class="mw-category">
        <li><a title="Аист">Аист</a></li>
        <li><a title="Белка">Белка</a></li>
        <li><a title="Волк">Волк</a></li>
    </div>
    """

    class MockResponse:
        """
        Мок асинхронного HTTP-ответа.

        Реализует асинхронный контекстный менеджер и метод text().
        """

        async def text(self):
            """
            Асинхронно возвращает содержимое ответа.

            Returns:
                str: HTML или текстовый контент ответа.
            """
            return html

        async def __aenter__(self):
            """
            Асинхронный вход в контекстный менеджер.

            Позволяет использовать объект в конструкции async with.

            Returns:
                MockResponse: сам объект для работы внутри блока with.
            """
            return self

        async def __aexit__(self, exc_type, exc, tb):
            """
            Асинхронный выход из контекстного менеджера.

            Принимает информацию об исключении, если оно возникло,
            но не выполняет дополнительных действий.

            Args:
                exc_type (type): тип исключения.
                exc (Exception): объект исключения.
                tb (traceback): трассировка стека.
            """

    class MockSession:
        """
        Мок асинхронной сессии HTTP.

        Возвращает MockResponse при вызове get().
        """

        def get(self, url):
            """
            Возвращает мок-ответ для заданного URL.

            Параметры:
                url (str): URL запроса (игнорируется в моке).

            Возвращает:
                MockResponse: объект мок-ответа.
            """
            return MockResponse()

        async def __aenter__(self):
            """
            Асинхронный вход в контекстный менеджер.

            Позволяет использовать MockSession в конструкции async with.
            """
            return self

        async def __aexit__(self, exc_type, exc, tb):
            """
            Асинхронный выход из контекстного менеджера.

            Принимает параметры исключения,
            но не выполняет дополнительных действий.
            """

    session = MockSession()
    result = await fetch(session, "fake_url")
    assert result["А"] == 1
    assert result["Б"] == 1
    assert result["В"] == 1


# --- Тест parse_all с моками fetch ---


@pytest.mark.asyncio
@pytest.mark.animals
async def test_parse_all(monkeypatch):
    """
    Тестирует функцию parse_all с использованием мока fetch.

    Проверяет суммирование результатов с нескольких URL.
    """

    async def mock_fetch(session, url):
        return defaultdict(int, {"А": 2, "Б": 1})

    monkeypatch.setattr(
        "task2.solution.fetch", mock_fetch
    )

    urls = ["url1", "url2"]
    result = await parse_all(urls)
    assert result["А"] == 4  # 2 + 2
    assert result["Б"] == 2


@pytest.mark.asyncio
@pytest.mark.animals
async def test_save_to_csv_async(monkeypatch):
    """
    Тестирует асинхронную функцию save_to_csv_async.

    Проверяет корректность записи данных в CSV.
    """
    written_data = []

    class AsyncMockFile:
        """
        Мок асинхронного файлового объекта для записи.

        Реализует методы асинхронного контекстного менеджера и write().
        """

        async def write(self, data):
            """
            Асинхронно записывает данные.

            Добавляет переданные данные в список
            written_data для проверки в тестах.
            """
            written_data.append(data)

        async def __aenter__(self):
            """
            Асинхронный вход в контекстный менеджер.

            Возвращает сам объект для использования в async with.
            """
            return self

        async def __aexit__(self, exc_type, exc, tb):
            """
            Асинхронный выход из контекстного менеджера.

            Принимает параметры исключения,
            но не выполняет дополнительных действий.
            """

    def mock_open(filename, mode="r", encoding=None, newline=None):
        """
        Мок функции открытия файла для aiofiles.

        Игнорирует параметры и возвращает объект AsyncMockFile,
        имитирующий асинхронный файловый объект для записи в тестах.
        """
        return AsyncMockFile()

    monkeypatch.setattr("aiofiles.open", mock_open)

    data = {"А": 10, "Б": 5}
    await save_to_csv_async(data, filename="dummy.csv")

    assert "А,10\n" in written_data
    assert "Б,5\n" in written_data


@pytest.mark.asyncio
@pytest.mark.animals
async def test_parse_and_save(monkeypatch):
    """
    Тестирует функцию parse_and_save.

    Проверяет, что функция вызывается и завершается без ошибок,
    используя моки для parse_all и save_to_csv_async.
    """
    monkeypatch.setattr(
        "task2.solution.parse_all",
        lambda urls: asyncio.Future()
    )
    monkeypatch.setattr(
        "task2.solution.save_to_csv_async",
        lambda data: asyncio.Future()
    )

    future = asyncio.Future()
    future.set_result(defaultdict(int, {"А": 1}))
    monkeypatch.setattr(
        "task2.solution.parse_all",
        lambda urls: future
    )
    monkeypatch.setattr(
        "task2.solution.save_to_csv_async",
        lambda data: asyncio.sleep(0)
    )

    await parse_and_save(["url"])
