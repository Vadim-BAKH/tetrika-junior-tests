"""
Модуль для сбора, парсинга и сохранения данных о животных из Википедии.

Содержит функции для:
- последовательного сбора всех страниц категории животных,
- асинхронного получения и подсчёта количества животных по первой букве,
- сохранения результатов в CSV файл,
- объединения всех этапов в единый процесс.
"""

import asyncio
from collections import defaultdict
from typing import DefaultDict

import aiofiles
import aiohttp
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://ru.wikipedia.org"
START_URL = BASE_URL + "/w/index.php?title=Категория:Животные_по_алфавиту"


def collect_all_pages() -> list[str]:
    """
    Собирает все страницы категории животных по алфавиту.

    Выполняет последовательные HTTP-запросы к страницам категории,
    переходя по ссылке "Следующая страница", пока она существует.

    Returns:
        list[str]: Список URL всех страниц категории.
    """
    urls = [START_URL]
    url = START_URL
    while True:
        resp = requests.get(url, timeout=20)
        soup = BeautifulSoup(resp.text, "lxml")
        next_link = soup.find("a", string="Следующая страница")
        if next_link and "href" in next_link.attrs:
            next_url = BASE_URL + next_link["href"]
            urls.append(next_url)
            url = next_url
        else:
            break
    print(f"\n🔗 Найдено страниц: {len(urls)}\n")
    return urls


async def fetch(
        session: aiohttp.ClientSession, url: str
) -> DefaultDict[str, int]:
    """
    Асинхронно получает и парсит страницу с животными.

    Извлекает названия животных и подсчитывает количество по первой букве.

    Args:
        session (aiohttp.ClientSession): Асинхронная сессия HTTP.
        url (str): URL страницы для получения.

    Returns:
        collections.defaultdict[int]: Словарь с количеством
        животных по первой букве.
    """
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, "lxml")
        letters = defaultdict(int)
        for li in soup.select(".mw-category li"):
            name = li.get_text().strip()
            if name:
                first_letter = name[0].upper()
                letters[first_letter] += 1
        return letters


async def parse_all(urls: list[str]) -> DefaultDict[str, int]:
    """
    Асинхронно обрабатывает список URL, собирая статистику по всем страницам.

    Запускает параллельные задачи fetch для каждого URL и суммирует результаты.

    Args:
        urls (list[str]): Список URL страниц для обработки.

    Returns:
        collections.defaultdict[int]: Словарь с суммарным количеством
        животных по первой букве.
    """
    result = defaultdict(int)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        pages_data = await asyncio.gather(*tasks)
        for page in pages_data:
            for letter, count in page.items():
                result[letter] += count
    return result


async def save_to_csv_async(
        data: dict[str, int], filename: str = "beasts.csv"
) -> None:
    """
    Асинхронно сохраняет данные в CSV файл.

    Записывает пары "буква,количество" построчно в указанный файл.

    Args:
        data (dict[str, int]): Словарь с данными для сохранения.
        filename (str, optional): Имя файла для записи.
        По умолчанию "beasts.csv".
    """
    async with aiofiles.open(
            filename, mode="w", encoding="utf-8", newline=""
    ) as f:
        for letter in sorted(data.keys()):
            line = f"{letter},{data[letter]}\n"
            await f.write(line)
    print(f"\n📁 Данные сохранены в файл: {filename}")


def main() -> None:
    """
    Главная функция запуска сбора, обработки и сохранения данных.

    Собирает все страницы, запускает асинхронный парсинг
    и сохраняет результаты.
    """
    urls = collect_all_pages()
    asyncio.run(parse_and_save(urls))


async def parse_and_save(urls: list[str]) -> None:
    """
    Асинхронно выполняет полный цикл: парсинг всех страниц
     и сохранение в файл.

    Args:
        urls (list[str]): Список URL страниц для обработки.
    """
    data = await parse_all(urls)
    await save_to_csv_async(data)

    total = sum(data.values())
    print(f"\n📦 Всего уникальных животных: {total}\n")


if __name__ == "__main__":
    main()
