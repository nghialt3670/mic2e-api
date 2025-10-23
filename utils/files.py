import requests


def download_file_to_bytes(url: str) -> bytes:
    response = requests.get(url)
    return response.content
