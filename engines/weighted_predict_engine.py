import os
import random
import pandas as pd


def _get_pool(df: pd.DataFrame, field: str, prefix: str) -> list[int]:
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


def _choose_by_weight(
    common_pool: list[int],
    weight_only_pool: list[int],
    freq_only_pool: list[int],
    used: set[int] | None,
    weight_common: float,
    weight_weight_only: float,
    weight_freq_only: float,
):
    used = used or set()

    available_common = [x for x in common_pool if x not in used]
    available_weight = [x for x in weight_only_pool if x not in used]
    available_freq = [x for x in freq_only_pool if x not in used]

    buckets = []
    weights = []

    if available_common:
        buckets.append(available_common)
        weights.append(weight_common)
    if available_weight:
        buckets.append(available_weight)
        weights.append(weight_weight_only)
    if available_freq:
        buckets.append(available_freq)
        weights.append(weight_freq_only)

    if not buckets:
        return None

    chosen_bucket = random.choices(buckets, weights=weights, k=1)[0]
    return random.choice(chosen_bucket)


def build_weighted_predict(
    hybrid_table_path: str,
    output_path: str,
    test_time: int,
    main_fields: list[str],
    sp_field: str | None = None,
    weight_common: float = 0.6,
    weight_weight_only: float = 0.3,
    weight_freq_only: float = 0.1,
):
    df = pd.read_csv(hybrid_table_path, encoding="utf-8-sig")

    pools = {}

    for field in main_fields:
        pools[field] = {
            "common": _get_pool(df, field, "common_"),
            "weight_only": _get_pool(df, field, "weight_only_"),
            "freq_only": _get_pool(df, field, "freq_only_"),
        }

    if sp_field:
        pools[sp_field] = {
            "common": _get_pool(df, sp_field, "common_"),
            "weight_only": _get_pool(df, sp_field, "weight_only_"),
            "freq_only": _get_pool(df, sp_field, "freq_only_"),
        }

    result_rows = []

    for _ in range(test_time):
        used_main = set()
        row = {"test_time": test_time}

        for field in main_fields:
            chosen = _choose_by_weight(
                pools[field]["common"],
                pools[field]["weight_only"],
                pools[field]["freq_only"],
                used_main,
                weight_common,
                weight_weight_only,
                weight_freq_only,
            )
            row[field] = chosen if chosen is not None else ""
            if chosen is not None:
                used_main.add(chosen)

        if sp_field:
            chosen_sp = _choose_by_weight(
                pools[sp_field]["common"],
                pools[sp_field]["weight_only"],
                pools[sp_field]["freq_only"],
                None,
                weight_common,
                weight_weight_only,
                weight_freq_only,
            )
            row[sp_field] = chosen_sp if chosen_sp is not None else ""

        result_rows.append(row)

    df_out = pd.DataFrame(result_rows)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_out.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("✅ Weighted Predict 建立完成")
    print(f"輸出檔案：{output_path}")
    print("-" * 60)
    print(df_out.to_string(index=False))
    print("-" * 60)