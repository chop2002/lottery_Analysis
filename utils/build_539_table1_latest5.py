import os
import pandas as pd

INPUT_PATH = "data/539/clean/539_history.csv"
OUTPUT_PATH = "data/539/query/539_table1_latest5.csv"


def build_table1_latest5():
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

    # 確保日期可排序
    df["draw_date"] = pd.to_datetime(df["draw_date"], errors="coerce")
    df = df.dropna(subset=["draw_date"])

    # 依日期由舊到新排序
    df = df.sort_values("draw_date").reset_index(drop=True)

    # 取最後 5 期
    latest_5 = df.tail(5).copy()

    # 只保留你要的欄位
    latest_5 = latest_5[["draw_date", "n1", "n2", "n3", "n4", "n5"]]

    # 日期格式固定
    latest_5["draw_date"] = latest_5["draw_date"].dt.strftime("%Y-%m-%d")

    # 數字欄轉整數
    num_cols = ["n1", "n2", "n3", "n4", "n5"]
    for col in num_cols:
        latest_5[col] = pd.to_numeric(latest_5[col], errors="coerce").astype("Int64")

    # 建資料夾
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # 輸出 CSV
    latest_5.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 第1張表建立完成")
    print(f"輸出檔案：{OUTPUT_PATH}")
    print("-" * 60)
    print(latest_5.to_string(index=False))
    print("-" * 60)


if __name__ == "__main__":
    build_table1_latest5()