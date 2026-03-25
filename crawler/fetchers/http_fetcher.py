import time
import requests


def fetch_html(url, headers=None, timeout=20, retries=3, sleep_sec=2):
    session = requests.Session()
    headers = headers or {"User-Agent": "Mozilla/5.0"}

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            res = session.get(url, headers=headers, timeout=timeout)
            res.raise_for_status()
            return res.content
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(sleep_sec)

    raise last_error