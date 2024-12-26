import argparse
import os
from typing import Any

from dotenv import find_dotenv, load_dotenv

from furl import furl

import requests

import validators


def shorten_link(token: str, link: str) -> str:
    url = "https://api.vk.ru/method/utils.getShortLink"
    headers = {"Authorization": f"Bearer {token}"}
    params: dict[str, Any] = {
        "url": link,
        "v": 5.199,
    }

    with requests.get(url=url, headers=headers, params=params, timeout=30) as response:
        response.raise_for_status()
        if "error" in response.text:
            raise ValueError("Произошла ошибка при формировании ссылки")
        return response.json()["response"]["short_url"]


def count_clicks(token: str, link: str) -> str:
    url = "https://api.vk.ru/method/utils.getLinkStats"
    key = furl(link).pathstr.strip("/")
    headers = {"Authorization": f"Bearer {token}"}
    params: dict[str, Any] = {
        "key": key,
        "v": 5.199,
    }

    with requests.get(url=url, headers=headers, params=params, timeout=30) as response:
        response.raise_for_status()
        if "error" in response.text:
            raise ValueError(f"Произошла ошибка при получении статистики переходов по ссылке: {link}")
        views = response.json()["response"]["stats"]
        return response.json()["response"]["stats"][0]["views"] if views else "0"


def is_shorten_link(token: str, link: str) -> bool:
    url = "https://api.vk.ru/method/utils.checkLink"
    headers = {"Authorization": f"Bearer {token}"}
    params: dict[str, Any] = {
        "url": link,
        "v": 5.199,
    }
    with requests.get(url=url, headers=headers, params=params, timeout=30) as response:
        response.raise_for_status()
        if "error" in response.text:
            raise ValueError(f"Произошла ошибка при проверке ссылки: {link}")
    return link != response.json()["response"]["link"]


def main() -> None:
    load_dotenv(find_dotenv())
    token = os.environ["VK_TOKEN"]

    parser = argparse.ArgumentParser(
        description="Получение короткой ссылки или получение статистики переходов для существующей",
    )
    parser.add_argument("link", help="Ссылка в формате: https://example.com")
    link = parser.parse_args().link

    try:
        if not validators.url(link):
            raise ValueError(f'Некорректная ссылка: "{link}"')
        if is_shorten_link(token, link):
            print(f"По ссылке {link} зафиксировано {count_clicks(token, link)} переход(ов)")  # noqa
        else:
            print(f"Сокращенная ссылка: {shorten_link(token, link)}")  # noqa
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.ConnectTimeout,
        ValueError,
    ) as error:
        print(str(error))  # noqa


if __name__ == "__main__":
    main()
