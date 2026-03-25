import os
import pandas as pd


def _get_top_list(df: pd.DataFrame, field: str, top_n: int = 5) -> list[int]:
    rows = df[df["show_order"].isin([f"top{i}" for i in range(1, top_n + 1)])].copy()
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


def build_hybrid_table(
    table2_path: str,
    weight_table_path: str,
    output_path: str,
    fields: list[str],
):
    df_freq = pd.read_csv(table2_path, encoding="utf-8-sig")
    df_weight = pd.read_csv(weight_table_path, encoding="utf-8-sig")

    result_rows = []

    # latest_value
    latest_row = {"show_order": "latest_value"}
    for field in fields:
        latest_val = df_freq.loc[df_freq["show_order"] == "latest_value", field].iloc[0]
        latest_row[field] = int(latest_val)
    result_rows.append(latest_row)

    common_map = {}
    weight_only_map = {}
    freq_only_map = {}

    max_common = 0
    max_weight_only = 0
    max_freq_only = 0

    for field in fields:
        freq_top = _get_top_list(df_freq, field)
        weight_top = _get_top_list(df_weight, field)

        common = [x for x in freq_top if x in weight_top]
        weight_only = [x for x in weight_top if x not in freq_top]
        freq_only = [x for x in freq_top if x not in weight_top]

        common_map[field] = common
        weight_only_map[field] = weight_only
        freq_only_map[field] = freq_only

        max_common = max(max_common, len(common))
        max_weight_only = max(max_weight_only, len(weight_only))
        max_freq_only = max(max_freq_only, len(freq_only))

    # common
    for i in range(max_common):
        row = {"show_order": f"common_{i + 1}"}
        for field in fields:
            row[field] = common_map[field][i] if i < len(common_map[field]) else ""
        result_rows.append(row)

    # weight_only
    for i in range(max_weight_only):
        row = {"show_order": f"weight_only_{i + 1}"}
        for field in fields:
            row[field] = weight_only_map[field][i] if i < len(weight_only_map[field]) else ""
        result_rows.append(row)

    # freq_only
    for i in range(max_freq_only):
        row = {"show_order": f"freq_only_{i + 1}"}
        for field in fields:
            row[field] = freq_only_map[field][i] if i < len(freq_only_map[field]) else ""
        result_rows.append(row)

    df_out = pd.DataFrame(result_rows)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_out.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("✅ HYBRID_TABLE 建立完成")
    print(f"輸出檔案：{output_path}")
    print("-" * 60)
    print(df_out.to_string(index=False))
    print("-" * 60)