import os
import random
import pandas as pd
import sys

TABLE2_PATH = "data/649/query/649_table2_lookup.csv"
OUTPUT_PATH = "data/649/query/649_table3_predict.csv"


def build_649_table3_predict(test_time):
    df = pd.read_csv(TABLE2_PATH, encoding="utf-8-sig")

    fields_main = ["n1", "n2", "n3", "n4", "n5", "n6"]
    field_sp = "sp"

    # 只取 latest_value ~ top5
    pool_rows = df[
        df["show_order"].isin(["latest_value", "top1", "top2", "top3", "top4", "top5"])
    ].copy()

    pools = {}

    # 主號池
    for field in fields_main:
        values = pool_rows[field].dropna().tolist()

        clean_values = []
        seen = set()
        for v in values:
            iv = int(v)
            if iv not in seen:
                seen.add(iv)
                clean_values.append(iv)

        pools[field] = clean_values

    # sp 池（獨立）
    values_sp = pool_rows[field_sp].dropna().tolist()
    clean_sp = []
    seen_sp = set()
    for v in values_sp:
        iv = int(v)
        if iv not in seen_sp:
            seen_sp.add(iv)
            clean_sp.append(iv)

    pools[field_sp] = clean_sp

    # 保底檢查
    for field in fields_main:
        if not pools[field]:
            raise ValueError(f"{field} 候選池為空，無法產生預測")
    if not pools[field_sp]:
        raise ValueError("sp 候選池為空，無法產生預測")

    result_rows = []

    for _ in range(test_time):
        used_main = set()
        row = {"test_time": test_time}

        # n1~n6：同列不可重複
        for field in fields_main:
            available = [x for x in pools[field] if x not in used_main]

            if not available:
                row[field] = ""
            else:
                chosen = random.choice(available)
                row[field] = chosen
                used_main.add(chosen)

        # sp：獨立抽
        row[field_sp] = random.choice(pools[field_sp])

        result_rows.append(row)

    df_out = pd.DataFrame(result_rows)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 大樂透第3張表建立完成")
    print(f"輸出檔案：{OUTPUT_PATH}")
    print("-" * 60)
    print(df_out.to_string(index=False))
    print("-" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("請從 main_649.py 傳入 test_time")
    test_time = int(sys.argv[1])
    build_649_table3_predict(test_time)