import logging
import os
import sys

import requests

from config import REMOTE_DIR, REMOTE_FILENAME, SOURCE_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s INFO %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

YADISK_API = "https://cloud-api.yandex.net/v1/disk/resources"


def download_file(url: str) -> bytes:
    logging.info("Скачивание файла...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    logging.info("Скачано %d байт.", len(response.content))
    return response.content


def ensure_dir_exists(token: str, remote_dir: str) -> None:
    headers = {"Authorization": f"OAuth {token}"}
    response = requests.put(
        YADISK_API,
        headers=headers,
        params={"path": remote_dir},
        timeout=30,
    )
    if response.status_code not in (201, 409):
        response.raise_for_status()


def upload_to_yadisk(content: bytes, token: str, remote_dir: str, filename: str) -> None:
    logging.info("Загрузка на Яндекс.Диск...")
    headers = {"Authorization": f"OAuth {token}"}
    remote_path = f"{remote_dir}/{filename}"

    response = requests.get(
        f"{YADISK_API}/upload",
        headers=headers,
        params={"path": remote_path, "overwrite": "true"},
        timeout=30,
    )
    response.raise_for_status()
    upload_url = response.json()["href"]

    put_response = requests.put(upload_url, data=content, timeout=60)
    put_response.raise_for_status()
    logging.info("Готово.")


if __name__ == "__main__":
    token = os.environ.get("YANDEX_TOKEN")
    if not token:
        logging.error("Переменная окружения YANDEX_TOKEN не задана.")
        sys.exit(1)

    file_content = download_file(SOURCE_URL)
    ensure_dir_exists(token, REMOTE_DIR)
    upload_to_yadisk(file_content, token, REMOTE_DIR, REMOTE_FILENAME)
