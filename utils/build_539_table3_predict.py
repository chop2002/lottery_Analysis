import os
import random
import pandas as pd
import sys

TABLE2_PATH = "data/539/query/539_table2_lookup.csv"
OUTPUT_PATH = "data/539/query/539_table3_predict.csv"


def build_539_table3_predict(test_time):
    df = pd.read_csv(TABLE2_PATH, encoding="utf-8-sig")

    fields = ["n1", "n2", "n3", "n4", "n5"]

    pool_rows = df[df["show_order"].isin(
        ["latest_value", "top1", "top2", "top3", "top4", "top5"]
    )].copy()

    pools = {}
    for field in fields:
        values = pool_rows[field].dropna().tolist()

        clean_values = []
        seen = set()
        for v in values:
            iv = int(v)
            if iv not in seen:
                seen.add(iv)
                clean_values.append(iv)

        pools[field] = clean_values

    result_rows = []

    for _ in range(test_time):
        used = set()
        row = {"test_time": test_time}

        for field in fields:
            available = [x for x in pools[field] if x not in used]

            if not available:
                row[field] = ""
            else:
                chosen = random.choice(available)
                row[field] = chosen
                used.add(chosen)

        result_rows.append(row)

    df_out = pd.DataFrame(result_rows)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 第3張表建立完成")
    print(f"輸出檔案：{OUTPUT_PATH}")
    print("-" * 60)
    print(df_out.to_string(index=False))
    print("-" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("請從 main.py 傳入 test_time")
    test_time = int(sys.argv[1])
    build_539_table3_predict(test_time)