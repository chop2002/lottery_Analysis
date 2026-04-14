import os
import pandas as pd

INPUT_PATH = "data/power/clean/power_history.csv"
OUTPUT_PATH = "data/power/query/power_table1_latest5.csv"


def build_power_table1_latest5():
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

    df["draw_date"] = pd.to_datetime(df["draw_date"], errors="coerce")
    df = df.dropna(subset=["draw_date"])
    df = df.sort_values("draw_date").reset_index(drop=True)

    latest_5 = df.tail(5).copy()
    latest_5 = latest_5[["draw_date", "n1", "n2", "n3", "n4", "n5", "n6", "sp"]]

    latest_5["draw_date"] = latest_5["draw_date"].dt.strftime("%Y-%m-%d")

    num_cols = ["n1", "n2", "n3", "n4", "n5", "n6", "sp"]
    for col in num_cols:
        latest_5[col] = pd.to_numeric(latest_5[col], errors="coerce").astype("Int64")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    latest_5.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 威力彩第1張表建立完成")
    print(f"輸出檔案：{OUTPUT_PATH}")
    print("-" * 60)
    print(latest_5.to_string(index=False))
    print("-" * 60)


if __name__ == "__main__":
    build_power_table1_latest5()
