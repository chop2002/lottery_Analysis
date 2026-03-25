from __future__ import annotations

import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "power"

PRED_FILE = DATA_DIR / "predictions.csv"
DRAW_FILE = DATA_DIR / "draws.csv"
DETAIL_FILE = DATA_DIR / "verification_details.csv"
SUMMARY_FILE = DATA_DIR / "verification_summary.csv"

ZONE1_COLS = ["p1", "p2", "p3", "p4", "p5", "p6"]
ZONE2_COL = "special_no"


def normalize_num(x) -> str:
    if pd.isna(x):
        return ""
    try:
        return f"{int(x):02d}"
    except Exception:
        s = str(x).strip()
        if s == "" or s.lower() == "nan":
            return ""
        if s.isdigit():
            return f"{int(s):02d}"
        return s


def safe_num_str(x) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    if s == "" or s.lower() == "nan":
        return ""
    return normalize_num(x)


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案：{path}")
    return pd.read_csv(path, dtype=str).fillna("")


def prepare_predictions(df: pd.DataFrame) -> pd.DataFrame:
    required = [
        "predict_date", "target_draw_date", "lottery", "batch_id",
        "model", "group_id", "rank", "score",
        *ZONE1_COLS, ZONE2_COL
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"predictions.csv 缺少欄位：{missing}")

    for c in ZONE1_COLS + [ZONE2_COL]:
        df[c] = df[c].apply(normalize_num)

    df["predict_date"] = pd.to_datetime(df["predict_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["target_draw_date"] = pd.to_datetime(df["target_draw_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["lottery"] = df["lottery"].astype(str).str.strip()
    df["batch_id"] = df["batch_id"].astype(str).str.strip()
    df["model"] = df["model"].astype(str).str.strip()
    df["group_id"] = df["group_id"].astype(str).str.strip()
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    return df


def prepare_draws(df: pd.DataFrame) -> pd.DataFrame:
    required = ["draw_date", *ZONE1_COLS, ZONE2_COL]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"draws.csv 缺少欄位：{missing}")

    for c in ZONE1_COLS + [ZONE2_COL]:
        df[c] = df[c].apply(normalize_num)

    df["draw_date"] = pd.to_datetime(df["draw_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def calc_zone1_hit(pred_nums: list[str], draw_nums: list[str]) -> tuple[int, str]:
    hit_nums = sorted(set(pred_nums) & set(draw_nums), key=lambda x: int(x))
    return len(hit_nums), " ".join(hit_nums)


def get_prize_tier(zone1_hit: int, zone2_hit: int) -> str:
    if zone1_hit == 6 and zone2_hit == 1:
        return "頭獎"
    if zone1_hit == 6 and zone2_hit == 0:
        return "貳獎"
    if zone1_hit == 5 and zone2_hit == 1:
        return "參獎"
    if zone1_hit == 5 and zone2_hit == 0:
        return "肆獎"
    if zone1_hit == 4 and zone2_hit == 1:
        return "伍獎"
    if zone1_hit == 4 and zone2_hit == 0:
        return "陸獎"
    if zone1_hit == 3 and zone2_hit == 1:
        return "柒獎"
    if (zone1_hit == 2 and zone2_hit == 1) or (zone1_hit == 3 and zone2_hit == 0):
        return "普獎"
    return "未中獎"


def build_verification_details(pred_df: pd.DataFrame, draw_df: pd.DataFrame) -> pd.DataFrame:
    merged = pred_df.merge(
        draw_df,
        left_on="target_draw_date",
        right_on="draw_date",
        how="left",
        suffixes=("_pred", "_draw")
    )

    details = []
    for _, row in merged.iterrows():
        pred_zone1 = [safe_num_str(row.get(f"{c}_pred", "")) for c in ZONE1_COLS]
        pred_zone1 = [x for x in pred_zone1 if x != ""]

        draw_zone1 = [safe_num_str(row.get(f"{c}_draw", "")) for c in ZONE1_COLS]
        draw_zone1 = [x for x in draw_zone1 if x != ""]

        pred_zone2 = safe_num_str(row.get(f"{ZONE2_COL}_pred", ""))
        draw_zone2 = safe_num_str(row.get(f"{ZONE2_COL}_draw", ""))

        if len(draw_zone1) == 6 and draw_zone2 != "":
            zone1_hit, zone1_hit_numbers = calc_zone1_hit(pred_zone1, draw_zone1)
            zone2_hit = 1 if pred_zone2 == draw_zone2 else 0
            prize_tier = get_prize_tier(zone1_hit, zone2_hit)
            is_verified = 1
            draw_zone1_text = " ".join(draw_zone1)
        else:
            zone1_hit = ""
            zone1_hit_numbers = ""
            zone2_hit = ""
            prize_tier = ""
            is_verified = 0
            draw_zone1_text = ""
            draw_zone2 = ""

        details.append({
            "predict_date": row["predict_date"],
            "target_draw_date": row["target_draw_date"],
            "lottery": row["lottery"],
            "batch_id": row["batch_id"],
            "model": row["model"],
            "group_id": row["group_id"],
            "rank": row["rank"],
            "score": row["score"],
            "pred_zone1": " ".join(pred_zone1),
            "pred_zone2": pred_zone2,
            "draw_zone1": draw_zone1_text,
            "draw_zone2": draw_zone2,
            "zone1_hit_count": zone1_hit,
            "zone1_hit_numbers": zone1_hit_numbers,
            "zone2_hit": zone2_hit,
            "prize_tier": prize_tier,
            "is_verified": is_verified,
        })

    return pd.DataFrame(details)


def build_summary(detail_df: pd.DataFrame) -> pd.DataFrame:
    verified = detail_df[detail_df["is_verified"] == 1].copy()
    if verified.empty:
        return pd.DataFrame(columns=[
            "model", "total_predictions", "avg_zone1_hits", "avg_score", "score_hit_corr",
            "zone2_hit_rate", "rank1_avg_zone1_hits", "rank2_avg_zone1_hits", "rank3_avg_zone1_hits",
            "hit_zone1_ge_1", "hit_zone1_ge_2", "hit_zone1_ge_3",
            "hit_zone1_ge_4", "hit_zone1_ge_5", "hit_zone1_ge_6",
            "both_zone1_zone2_hit_rate",
            "prize_top", "prize_second", "prize_third", "prize_fourth",
            "prize_fifth", "prize_sixth", "prize_seventh", "prize_general"
        ])

    verified["zone1_hit_count"] = pd.to_numeric(verified["zone1_hit_count"], errors="coerce")
    verified["zone2_hit"] = pd.to_numeric(verified["zone2_hit"], errors="coerce")
    verified["rank"] = pd.to_numeric(verified["rank"], errors="coerce")
    verified["score"] = pd.to_numeric(verified["score"], errors="coerce")

    prize_map = {
        "頭獎": "prize_top",
        "貳獎": "prize_second",
        "參獎": "prize_third",
        "肆獎": "prize_fourth",
        "伍獎": "prize_fifth",
        "陸獎": "prize_sixth",
        "柒獎": "prize_seventh",
        "普獎": "prize_general",
    }

    rows = []
    for model, g in verified.groupby("model"):
        total = len(g)
        score_corr = g[["score", "zone1_hit_count"]].corr().iloc[0, 1] if g["score"].notna().sum() >= 2 else None

        row = {
            "model": model,
            "total_predictions": total,
            "avg_zone1_hits": round(g["zone1_hit_count"].mean(), 4),
            "avg_score": round(g["score"].mean(), 4) if g["score"].notna().any() else None,
            "score_hit_corr": round(score_corr, 4) if pd.notna(score_corr) else None,
            "zone2_hit_rate": round(g["zone2_hit"].mean(), 4),
            "rank1_avg_zone1_hits": round(g.loc[g["rank"] == 1, "zone1_hit_count"].mean(), 4) if (g["rank"] == 1).any() else None,
            "rank2_avg_zone1_hits": round(g.loc[g["rank"] == 2, "zone1_hit_count"].mean(), 4) if (g["rank"] == 2).any() else None,
            "rank3_avg_zone1_hits": round(g.loc[g["rank"] == 3, "zone1_hit_count"].mean(), 4) if (g["rank"] == 3).any() else None,
            "hit_zone1_ge_1": round((g["zone1_hit_count"] >= 1).mean(), 4),
            "hit_zone1_ge_2": round((g["zone1_hit_count"] >= 2).mean(), 4),
            "hit_zone1_ge_3": round((g["zone1_hit_count"] >= 3).mean(), 4),
            "hit_zone1_ge_4": round((g["zone1_hit_count"] >= 4).mean(), 4),
            "hit_zone1_ge_5": round((g["zone1_hit_count"] >= 5).mean(), 4),
            "hit_zone1_ge_6": round((g["zone1_hit_count"] >= 6).mean(), 4),
            "both_zone1_zone2_hit_rate": round(((g["zone1_hit_count"] >= 1) & (g["zone2_hit"] == 1)).mean(), 4),
        }

        counts = g["prize_tier"].value_counts()
        for prize_name, col_name in prize_map.items():
            row[col_name] = int(counts.get(prize_name, 0))

        rows.append(row)

    summary = pd.DataFrame(rows).sort_values(
        by=["prize_general", "hit_zone1_ge_3", "avg_zone1_hits", "zone2_hit_rate"],
        ascending=False
    ).reset_index(drop=True)

    return summary


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    pred_df = prepare_predictions(load_csv(PRED_FILE))
    draw_df = prepare_draws(load_csv(DRAW_FILE))

    detail_df = build_verification_details(pred_df, draw_df)
    summary_df = build_summary(detail_df)

    detail_df.to_csv(DETAIL_FILE, index=False, encoding="utf-8-sig")
    summary_df.to_csv(SUMMARY_FILE, index=False, encoding="utf-8-sig")

    print("✅ 威力彩自動驗證完成")
    print(f"明細輸出：{DETAIL_FILE}")
    print(f"統計輸出：{SUMMARY_FILE}")

    if not summary_df.empty:
        print("\n=== 威力彩模型命中率摘要 ===")
        print(summary_df.to_string(index=False))
    else:
        print("\n目前沒有可驗證的威力彩資料（可能 target_draw_date 尚未開獎）")


if __name__ == "__main__":
    main()