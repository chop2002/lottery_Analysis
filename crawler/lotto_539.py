import re
import requests
from bs4 import BeautifulSoup


def fetch_539(limit=10):
    url = "https://www.pilio.idv.tw/lto539/list539APP.asp"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers, timeout=20)
    res.raise_for_status()

    html = res.content.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    pattern = re.compile(
        r"(\d{4}/\d{2}/\d{2}).{0,80}?(\d{2})\D+(\d{2})\D+(\d{2})\D+(\d{2})\D+(\d{2})",
        re.S,
    )

    results = []
    for m in pattern.finditer(text):
        date_text = m.group(1)
        nums = [m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)]
        results.append((date_text, nums))

    unique_results = []
    seen = set()
    for date_text, nums in results:
        key = (date_text, tuple(nums))
        if key not in seen:
            seen.add(key)
            unique_results.append((date_text, nums))

    return unique_results[:limit]
