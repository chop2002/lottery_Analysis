import re
from bs4 import BeautifulSoup


def parse_539_strategy_text(html_bytes):
    html = html_bytes.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    pattern = re.compile(
        r"(\d{4}/\d{2}/\d{2}).{0,80}?(\d{2})\D+(\d{2})\D+(\d{2})\D+(\d{2})\D+(\d{2})",
        re.S
    )

    results = []
    seen = set()

    for m in pattern.finditer(text):
        draw_date = m.group(1).replace("/", "-")
        nums = [int(m.group(i)) for i in range(2, 7)]
        key = (draw_date, tuple(nums))

        if key not in seen:
            seen.add(key)
            results.append({
                "draw_date": draw_date,
                "n1": nums[0],
                "n2": nums[1],
                "n3": nums[2],
                "n4": nums[3],
                "n5": nums[4],
            })

    return results


def parse_539(html_bytes):
    # 目前先用文字解析策略
    results = parse_539_strategy_text(html_bytes)

    if results:
        return results

    raise ValueError("539 解析失敗：所有策略都無法取得資料")