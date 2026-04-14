import os
import pandas as pd

from crawler.fetchers.http_fetcher import fetch_html
from crawler.parsers.parser_539 import parse_539
from crawler.validators.lottery_validator import validate_539

HISTORY_PATH = "data/539/clean/539_history.csv"
SNAPSHOT_PATH = "crawler/snapshots/539_last.html"


def fetch_latest_539(limit=30):
    url = "https://www.pilio.idv.tw/lto539/list539APP.asp"

    # 抓原始 HTML
    html_bytes = fetch_html(url)

    # 存快照，方便之後查錯
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
    with open(SNAPSHOT_PATH, "wb") as f:
        f.write(html_bytes)

    # 解析
    rows = parse_539(html_bytes)

    # 驗證
    validate_539(rows)

    # 只取最新幾期
    rows = rows[:limit]

    # 補齊欄位格式，對接既有 history
    for row in rows:
        row["draw_no"] = ""
        row["source"] = "pilio"

    return rows


def update_539():
    if not os.path.exists(HISTORY_PATH):
        raise FileNotFoundError(f"找不到歷史資料檔：{HISTORY_PATH}")

    df_history = pd.read_csv(HISTORY_PATH, encoding="utf-8-sig")
    latest_rows = fetch_latest_539(limit=30)
    df_latest = pd.DataFrame(latest_rows)

    if df_latest.empty:
        print("沒有抓到最新資料，未更新。")
        return

    required_cols = ["draw_date", "draw_no", "n1", "n2", "n3", "n4", "n5", "source"]

    for col in required_cols:
        if col not in df_history.columns:
            df_history[col] = ""
        if col not in df_latest.columns:
            df_latest[col] = ""

    df_history = df_history[required_cols]
    df_latest = df_latest[required_cols]

    # 日期統一
    df_history["draw_date"] = pd.to_datetime(df_history["draw_date"], errors="coerce")
    df_latest["draw_date"] = pd.to_datetime(df_latest["draw_date"], errors="coerce")

    df_history = df_history.dropna(subset=["draw_date"])
    df_latest = df_latest.dropna(subset=["draw_date"])

    df_history["draw_date"] = df_history["draw_date"].dt.strftime("%Y-%m-%d")
    df_latest["draw_date"] = df_latest["draw_date"].dt.strftime("%Y-%m-%d")

    # 號碼欄轉數字
    num_cols = ["n1", "n2", "n3", "n4", "n5"]
    for col in num_cols:
        df_history[col] = pd.to_numeric(df_history[col], errors="coerce")
        df_latest[col] = pd.to_numeric(df_latest[col], errors="coerce")

    # 找新資料
    old_dates = set(df_history["draw_date"].astype(str))
    df_new = df_latest[~df_latest["draw_date"].astype(str).isin(old_dates)].copy()

    if df_new.empty:
        print("沒有新資料可更新。")
        print(f"目前總筆數：{len(df_history)}")
        return

    # 合併 + 去重 + 排序
    df_all = pd.concat([df_history, df_new], ignore_index=True)
    df_all = df_all.drop_duplicates(subset=["draw_date"], keep="first")
    df_all["draw_date"] = pd.to_datetime(df_all["draw_date"], errors="coerce")
    df_all = df_all.dropna(subset=["draw_date"])
    df_all = df_all.sort_values(by="draw_date")
    df_all["draw_date"] = df_all["draw_date"].dt.strftime("%Y-%m-%d")

    # 寫回
    df_all.to_csv(HISTORY_PATH, index=False, encoding="utf-8-sig")

    print("✅ 更新完成")
    print(f"新增筆數：{len(df_new)}")
    print(f"目前總筆數：{len(df_all)}")
    print("新增資料：")
    print(df_new.to_string(index=False))


if __name__ == "__main__":
    update_539()