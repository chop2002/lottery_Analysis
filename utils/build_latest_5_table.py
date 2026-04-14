import os
import pandas as pd

INPUT_PATH = "data/539/clean/539_history.csv"
OUTPUT_PATH = "data/539/query/latest_5_draws.csv"


def build_latest_5_table():
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

    # 日期轉格式後排序
    df["draw_date"] = pd.to_datetime(df["draw_date"], errors="coerce")
    df = df.dropna(subset=["draw_date"])
    df = df.sort_values("draw_date").reset_index(drop=True)

    # 取最後5期
    latest_5 = df.tail(5).copy()

    # 只保留你要的欄位
    latest_5 = latest_5[["draw_date", "n1", "n2", "n3", "n4", "n5"]]

    # 輸出欄位名稱改成 date
    latest_5 = latest_5.rename(columns={"draw_date": "date"})

    # 日期格式統一
    latest_5["date"] = latest_5["date"].dt.strftime("%Y-%m-%d")

    # 建資料夾
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # 存檔
    latest_5.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 第1張表建立完成")
    print(f"輸出：{OUTPUT_PATH}")
    print(latest_5.to_string(index=False))


if __name__ == "__main__":
    build_latest_5_table()
