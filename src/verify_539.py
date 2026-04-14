from __future__ import annotations

import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "539"

PRED_FILE = DATA_DIR / "predictions.csv"
DRAW_FILE = DATA_DIR / "draws.csv"
DETAIL_FILE = DATA_DIR / "verification_details.csv"
SUMMARY_FILE = DATA_DIR / "verification_summary.csv"

PRED_NUM_COLS = ["n1", "n2", "n3", "n4", "n5"]
DRAW_NUM_COLS = ["n1", "n2", "n3", "n4", "n5"]


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
        "model", "group_id", "rank", "score", *PRED_NUM_COLS
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"predictions.csv 缺少欄位：{missing}")

    for c in PRED_NUM_COLS:
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
    required = ["draw_date", *DRAW_NUM_COLS]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"draws.csv 缺少欄位：{missing}")

    for c in DRAW_NUM_COLS:
        df[c] = df[c].apply(normalize_num)

    df["draw_date"] = pd.to_datetime(df["draw_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def calc_hit(pred_nums: list[str], draw_nums: list[str]) -> tuple[int, str]:
    hit_nums = sorted(set(pred_nums) & set(draw_nums), key=lambda x: int(x))
    return len(hit_nums), " ".join(hit_nums)


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
        pred_nums = [safe_num_str(row.get(f"{c}_pred", "")) for c in PRED_NUM_COLS]
        pred_nums = [x for x in pred_nums if x != ""]

        draw_nums = [safe_num_str(row.get(f"{c}_draw", "")) for c in DRAW_NUM_COLS]
        draw_nums = [x for x in draw_nums if x != ""]

        if len(draw_nums) == 5:
            hit_count, hit_numbers = calc_hit(pred_nums, draw_nums)
            is_verified = 1
            draw_nums_text = " ".join(draw_nums)
        else:
            hit_count = ""
            hit_numbers = ""
            is_verified = 0
            draw_nums_text = ""

        details.append({
            "predict_date": row["predict_date"],
            "target_draw_date": row["target_draw_date"],
            "lottery": row["lottery"],
            "batch_id": row["batch_id"],
            "model": row["model"],
            "group_id": row["group_id"],
            "rank": row["rank"],
            "score": row["score"],
            "pred_nums": " ".join(pred_nums),
            "draw_nums": draw_nums_text,
            "hit_count": hit_count,
            "hit_numbers": hit_numbers,
            "is_verified": is_verified,
        })

    return pd.DataFrame(details)


def build_summary(detail_df: pd.DataFrame) -> pd.DataFrame:
    verified = detail_df[detail_df["is_verified"] == 1].copy()
    if verified.empty:
        return pd.DataFrame(columns=[
            "model", "total_predictions", "avg_hits", "avg_score",
            "score_hit_corr", "rank1_avg_hits", "rank2_avg_hits", "rank3_avg_hits",
            "hit_ge_1", "hit_ge_2", "hit_ge_3", "hit_ge_4", "hit_ge_5"
        ])

    verified["hit_count"] = pd.to_numeric(verified["hit_count"], errors="coerce")
    verified["rank"] = pd.to_numeric(verified["rank"], errors="coerce")
    verified["score"] = pd.to_numeric(verified["score"], errors="coerce")

    summary_rows = []
    for model, g in verified.groupby("model"):
        total = len(g)
        score_corr = g[["score", "hit_count"]].corr().iloc[0, 1] if g["score"].notna().sum() >= 2 else None

        row = {
            "model": model,
            "total_predictions": total,
            "avg_hits": round(g["hit_count"].mean(), 4),
            "avg_score": round(g["score"].mean(), 4) if g["score"].notna().any() else None,
            "score_hit_corr": round(score_corr, 4) if pd.notna(score_corr) else None,
            "rank1_avg_hits": round(g.loc[g["rank"] == 1, "hit_count"].mean(), 4) if (g["rank"] == 1).any() else None,
            "rank2_avg_hits": round(g.loc[g["rank"] == 2, "hit_count"].mean(), 4) if (g["rank"] == 2).any() else None,
            "rank3_avg_hits": round(g.loc[g["rank"] == 3, "hit_count"].mean(), 4) if (g["rank"] == 3).any() else None,
            "hit_ge_1": round((g["hit_count"] >= 1).mean(), 4),
            "hit_ge_2": round((g["hit_count"] >= 2).mean(), 4),
            "hit_ge_3": round((g["hit_count"] >= 3).mean(), 4),
            "hit_ge_4": round((g["hit_count"] >= 4).mean(), 4),
            "hit_ge_5": round((g["hit_count"] >= 5).mean(), 4),
        }
        summary_rows.append(row)

    summary = pd.DataFrame(summary_rows).sort_values(
        by=["hit_ge_3", "hit_ge_2", "avg_hits"],
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

    print("✅ 539 自動驗證完成")
    print(f"明細輸出：{DETAIL_FILE}")
    print(f"統計輸出：{SUMMARY_FILE}")

    if not summary_df.empty:
        print("\n=== 模型命中率摘要 ===")
        print(summary_df.to_string(index=False))
    else:
        print("\n目前沒有可驗證的資料（可能 target_draw_date 尚未開獎）")


if __name__ == "__main__":
    main()