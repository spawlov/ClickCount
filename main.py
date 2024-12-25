import os
from typing import Any

from dotenv import find_dotenv, load_dotenv

from furl import furl

import requests

import validators


load_dotenv(find_dotenv())


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
        return response.json()["response"]["stats"][0]["views"]


def is_shorten_link(link: str) -> bool:
    return furl(link).host == "vk.cc"


def main(link: str) -> str:
    token = os.getenv("TOKEN")
    link = link.strip()
    if not validators.url(link):
        return f'Некорректная ссылка: "{link}"'
    try:
        if not is_shorten_link(link):
            result_message = f"Сокращенная ссылка: {shorten_link(token, link)}"  # type: ignore
        else:
            result_message = f"По ссылке {link} зафиксировано {count_clicks(token, link)} переход(ов)"  # type: ignore
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.ConnectTimeout,
        ValueError,
    ) as error:
        return str(error)
    return result_message


if __name__ == "__main__":
    result = main(input("Введите ссылку: "))
    print(result)  # noqa
