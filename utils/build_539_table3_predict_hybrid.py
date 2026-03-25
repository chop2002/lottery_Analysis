import os
import random
import pandas as pd
import sys

TABLE4_PATH = "data/539/query/539_table4_hybrid.csv"
OUTPUT_PATH = "data/539/query/539_table3_predict_hybrid.csv"


def get_pool(df, field, prefix):
    rows = df[df["show_order"].str.startswith(prefix, na=False)]
    vals = rows[field].dropna().tolist()
    result = []
    seen = set()

    for v in vals:
        s = str(v).strip()
        if s == "":
            continue
        iv = int(v)
        if iv not in seen:
            seen.add(iv)
            result.append(iv)

    return result


def build_539_table3_predict_hybrid(test_time):
    df = pd.read_csv(TABLE4_PATH, encoding="utf-8-sig")

    fields = ["n1", "n2", "n3", "n4", "n5"]
    pools = {}

    for field in fields:
        common_pool = get_pool(df, field, "common_")
        weight_only_pool = get_pool(df, field, "weight_only_")
        freq_only_pool = get_pool(df, field, "freq_only_")

        pools[field] = {
            "common": common_pool,
            "weight_only": weight_only_pool,
            "freq_only": freq_only_pool,
        }

    result_rows = []

    for _ in range(test_time):
        used = set()
        row = {"test_time": test_time}

        for field in fields:
            chosen = None

            # 1. 先從 common 抽
            available_common = [x for x in pools[field]["common"] if x not in used]
            if available_common:
                chosen = random.choice(available_common)
            else:
                # 2. 補 weight_only
                available_weight = [x for x in pools[field]["weight_only"] if x not in used]
                if available_weight:
                    chosen = random.choice(available_weight)
                else:
                    # 3. 最後補 freq_only
                    available_freq = [x for x in pools[field]["freq_only"] if x not in used]
                    if available_freq:
                        chosen = random.choice(available_freq)

            row[field] = chosen if chosen is not None else ""
            if chosen is not None:
                used.add(chosen)

        result_rows.append(row)

    df_out = pd.DataFrame(result_rows)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 539 HYBRID 預測表建立完成")
    print(f"輸出檔案：{OUTPUT_PATH}")
    print("-" * 60)
    print(df_out.to_string(index=False))
    print("-" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("請從 main.py 傳入 test_time")
    test_time = int(sys.argv[1])
    build_539_table3_predict_hybrid(test_time)