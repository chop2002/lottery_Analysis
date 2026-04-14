import os
import pandas as pd
from collections import Counter

TABLE1_PATH = "data/539/query/539_table1_latest5.csv"
SEQUENCE_PATH = "data/539/sequence/539_sequences.csv"
OUTPUT_PATH = "data/539/query/539_table2_lookup.csv"


def build_539_table2_lookup():
    df_table1 = pd.read_csv(TABLE1_PATH, encoding="utf-8-sig")
    df_seq = pd.read_csv(SEQUENCE_PATH, encoding="utf-8-sig")

    # 取第1張表最後1列 = 最新一期
    latest_row = df_table1.tail(1).iloc[0]

    fields = ["n1", "n2", "n3", "n4", "n5"]
    result_rows = []

    # 第1列：最新一期數值
    latest_values_row = {"show_order": "latest_value"}
    for field in fields:
        latest_values_row[field] = int(latest_row[field])
    result_rows.append(latest_values_row)

    # 先把每一欄的 next_value 全抓出來
    next_values_map = {}

    for field in fields:
        current_value = int(latest_row[field])

        subset = df_seq[
            (df_seq["field"] == field) & (df_seq["current_value"] == current_value)
        ].copy()

        next_values = subset["next_value"].dropna().astype(int).tolist()
        next_values_map[field] = next_values

    # 第2~6列：top1~top5
    for rank_idx in range(5):
        row_data = {"show_order": f"top{rank_idx + 1}"}

        for field in fields:
            counts = Counter(next_values_map[field])
            ranked_values = counts.most_common()

            if rank_idx < len(ranked_values):
                row_data[field] = ranked_values[rank_idx][0]
            else:
                row_data[field] = ""

        result_rows.append(row_data)

    # 第7列開始：unseen 全部值
    full_value_set = set(range(1, 40))
    unseen_map = {}
    max_unseen_len = 0

    for field in fields:
        appeared_values = set(next_values_map[field])
        unseen_values = sorted(list(full_value_set - appeared_values))
        unseen_map[field] = unseen_values
        if len(unseen_values) > max_unseen_len:
            max_unseen_len = len(unseen_values)

    for i in range(max_unseen_len):
        row_data = {"show_order": f"unseen_{i + 1}"}

        for field in fields:
            if i < len(unseen_map[field]):
                row_data[field] = unseen_map[field][i]
            else:
                row_data[field] = ""

        result_rows.append(row_data)

    df_out = pd.DataFrame(result_rows)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 第2張表建立完成")
    print(f"輸出檔案：{OUTPUT_PATH}")
    print("-" * 60)
    print(df_out.head(12).to_string(index=False))
    print("-" * 60)


if __name__ == "__main__":
    build_539_table2_lookup()
