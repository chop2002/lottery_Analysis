import os
import pandas as pd

TABLE1_PATH = "data/539/query/539_table1_latest5.csv"
SEQUENCE_PATH = "data/539/sequence/539_sequences.csv"
OUTPUT_PATH = "data/539/query/539_weight_table.csv"


def build_539_weight_table():
    df_table1 = pd.read_csv(TABLE1_PATH, encoding="utf-8-sig")
    df_seq = pd.read_csv(SEQUENCE_PATH, encoding="utf-8-sig")

    df_seq["current_date"] = pd.to_datetime(df_seq["current_date"], errors="coerce")
    df_seq = df_seq.dropna(subset=["current_date"])

    latest_row = df_table1.tail(1).iloc[0]
    fields = ["n1", "n2", "n3", "n4", "n5"]

    result_rows = []

    # 第1列：最新一期
    latest_values_row = {"show_order": "latest_value"}
    for field in fields:
        latest_values_row[field] = int(latest_row[field])
    result_rows.append(latest_values_row)

    weighted_rank_map = {}
    unseen_map = {}
    max_unseen_len = 0

    full_value_set = set(range(1, 40))

    for field in fields:
        current_value = int(latest_row[field])

        subset = df_seq[
            (df_seq["field"] == field) & (df_seq["current_value"] == current_value)
        ].copy()

        subset = subset.sort_values("current_date").reset_index(drop=True)

        # 依時間由舊到新給權重：1,2,3,...,N
        subset["weight"] = range(1, len(subset) + 1)

        # 對 next_value 加總權重
        if not subset.empty:
            weighted_sum = (
                subset.groupby("next_value", as_index=False)["weight"]
                .sum()
                .sort_values(["weight", "next_value"], ascending=[False, True])
            )
            ranked_values = weighted_sum["next_value"].astype(int).tolist()
            appeared_values = set(ranked_values)
        else:
            ranked_values = []
            appeared_values = set()

        weighted_rank_map[field] = ranked_values

        unseen_values = sorted(list(full_value_set - appeared_values))
        unseen_map[field] = unseen_values
        max_unseen_len = max(max_unseen_len, len(unseen_values))

    # top1 ~ top5
    for rank_idx in range(5):
        row_data = {"show_order": f"top{rank_idx + 1}"}
        for field in fields:
            ranked_values = weighted_rank_map[field]
            if rank_idx < len(ranked_values):
                row_data[field] = ranked_values[rank_idx]
            else:
                row_data[field] = ""
        result_rows.append(row_data)

    # unseen
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

    print("✅ WEIGHT_TABLE 建立完成")
    print(f"輸出檔案：{OUTPUT_PATH}")
    print("-" * 60)
    print(df_out.head(12).to_string(index=False))
    print("-" * 60)


if __name__ == "__main__":
    build_539_weight_table()
