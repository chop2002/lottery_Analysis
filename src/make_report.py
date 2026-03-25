from __future__ import annotations
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_539_DIR = BASE_DIR / "data" / "539"
DATA_POWER_DIR = BASE_DIR / "data" / "power"
DATA_649_DIR = BASE_DIR / "data" / "649"
REPORT_DIR = BASE_DIR / "data" / "reports"

FILE_539_DETAIL = DATA_539_DIR / "verification_details.csv"
FILE_539_SUMMARY = DATA_539_DIR / "verification_summary.csv"

FILE_POWER_DETAIL = DATA_POWER_DIR / "verification_details.csv"
FILE_POWER_SUMMARY = DATA_POWER_DIR / "verification_summary.csv"

FILE_649_DETAIL = DATA_649_DIR / "verification_details.csv"
FILE_649_SUMMARY = DATA_649_DIR / "verification_summary.csv"

REPORT_TXT = REPORT_DIR / "report_latest.txt"

REPORT_539_CSV = REPORT_DIR / "report_539_summary.csv"
REPORT_POWER_CSV = REPORT_DIR / "report_power_summary.csv"
REPORT_649_CSV = REPORT_DIR / "report_649_summary.csv"

REPORT_539_RANK_CSV = REPORT_DIR / "report_539_rank_stats.csv"
REPORT_539_SCORE_CSV = REPORT_DIR / "report_539_score_band_stats.csv"
REPORT_539_BATCH_CSV = REPORT_DIR / "report_539_batch_stats.csv"

REPORT_POWER_RANK_CSV = REPORT_DIR / "report_power_rank_stats.csv"
REPORT_POWER_SCORE_CSV = REPORT_DIR / "report_power_score_band_stats.csv"
REPORT_POWER_BATCH_CSV = REPORT_DIR / "report_power_batch_stats.csv"

REPORT_649_RANK_CSV = REPORT_DIR / "report_649_rank_stats.csv"
REPORT_649_SCORE_CSV = REPORT_DIR / "report_649_score_band_stats.csv"
REPORT_649_BATCH_CSV = REPORT_DIR / "report_649_batch_stats.csv"


def load_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str).fillna("")


def safe_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def qcut_safe(series: pd.Series, max_q: int = 4):
    s = pd.to_numeric(series, errors="coerce")
    s = s[s.notna()]
    if s.empty:
        return None
    nuniq = s.nunique()
    if nuniq < 2:
        return None
    q = min(max_q, nuniq)
    return pd.qcut(series, q=q, duplicates="drop")


# ========= 539 =========

def make_539_recent_stats(detail_df: pd.DataFrame, n: int) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()

    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["target_draw_date"] = pd.to_datetime(df["target_draw_date"], errors="coerce")
    df["hit_count"] = pd.to_numeric(df["hit_count"], errors="coerce")
    df = df.sort_values(["model", "target_draw_date", "group_id"])

    rows = []
    for model, g in df.groupby("model"):
        g = g.tail(n)
        rows.append({
            "model": model,
            f"recent_{n}_count": len(g),
            f"recent_{n}_avg_hits": round(g["hit_count"].mean(), 4),
            f"recent_{n}_hit_ge_2": round((g["hit_count"] >= 2).mean(), 4),
            f"recent_{n}_hit_ge_3": round((g["hit_count"] >= 3).mean(), 4),
            f"recent_{n}_hit_ge_4": round((g["hit_count"] >= 4).mean(), 4),
        })
    return pd.DataFrame(rows)


def make_539_rank_stats(detail_df: pd.DataFrame) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()
    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
    df["hit_count"] = pd.to_numeric(df["hit_count"], errors="coerce")

    rows = []
    for (model, rank), g in df.groupby(["model", "rank"], dropna=True):
        rows.append({
            "model": model,
            "rank": int(rank),
            "count": len(g),
            "avg_hits": round(g["hit_count"].mean(), 4),
            "hit_ge_2": round((g["hit_count"] >= 2).mean(), 4),
            "hit_ge_3": round((g["hit_count"] >= 3).mean(), 4),
        })
    return pd.DataFrame(rows).sort_values(["model", "rank"]).reset_index(drop=True)


def make_539_score_band_stats(detail_df: pd.DataFrame) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()
    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["hit_count"] = pd.to_numeric(df["hit_count"], errors="coerce")
    df = df[df["score"].notna()].copy()
    if df.empty:
        return pd.DataFrame()

    score_band = qcut_safe(df["score"])
    if score_band is None:
        return pd.DataFrame()
    df["score_band"] = score_band

    rows = []
    for (model, band), g in df.groupby(["model", "score_band"]):
        rows.append({
            "model": model,
            "score_band": str(band),
            "count": len(g),
            "avg_hits": round(g["hit_count"].mean(), 4),
            "hit_ge_2": round((g["hit_count"] >= 2).mean(), 4),
            "hit_ge_3": round((g["hit_count"] >= 3).mean(), 4),
        })
    return pd.DataFrame(rows).sort_values(["model", "score_band"]).reset_index(drop=True)


def make_539_batch_stats(detail_df: pd.DataFrame) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()
    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["hit_count"] = pd.to_numeric(df["hit_count"], errors="coerce")

    rows = []
    for (batch_id, model), g in df.groupby(["batch_id", "model"]):
        rows.append({
            "batch_id": batch_id,
            "model": model,
            "count": len(g),
            "avg_hits": round(g["hit_count"].mean(), 4),
            "hit_ge_2": round((g["hit_count"] >= 2).mean(), 4),
            "hit_ge_3": round((g["hit_count"] >= 3).mean(), 4),
        })
    return pd.DataFrame(rows).sort_values(["batch_id", "model"]).reset_index(drop=True)


def merge_539_report(summary_df: pd.DataFrame, detail_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    summary_df = safe_numeric(summary_df, [
        "total_predictions", "avg_hits", "avg_score", "score_hit_corr",
        "rank1_avg_hits", "rank2_avg_hits", "rank3_avg_hits",
        "hit_ge_1", "hit_ge_2", "hit_ge_3", "hit_ge_4", "hit_ge_5"
    ])
    recent10 = make_539_recent_stats(detail_df, 10)
    recent30 = make_539_recent_stats(detail_df, 30)

    result = summary_df.merge(recent10, on="model", how="left")
    result = result.merge(recent30, on="model", how="left")
    result = result.sort_values(by=["hit_ge_3", "hit_ge_2", "avg_hits"], ascending=False).reset_index(drop=True)
    result["model_rank"] = result.index + 1
    cols = ["model_rank"] + [c for c in result.columns if c != "model_rank"]
    return result[cols]


# ========= power =========

def make_power_recent_stats(detail_df: pd.DataFrame, n: int) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()

    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["target_draw_date"] = pd.to_datetime(df["target_draw_date"], errors="coerce")
    df["zone1_hit_count"] = pd.to_numeric(df["zone1_hit_count"], errors="coerce")
    df["zone2_hit"] = pd.to_numeric(df["zone2_hit"], errors="coerce")
    df = df.sort_values(["model", "target_draw_date", "group_id"])

    rows = []
    for model, g in df.groupby("model"):
        g = g.tail(n)
        rows.append({
            "model": model,
            f"recent_{n}_count": len(g),
            f"recent_{n}_avg_zone1_hits": round(g["zone1_hit_count"].mean(), 4),
            f"recent_{n}_zone2_hit_rate": round(g["zone2_hit"].mean(), 4),
            f"recent_{n}_hit_zone1_ge_2": round((g["zone1_hit_count"] >= 2).mean(), 4),
            f"recent_{n}_hit_zone1_ge_3": round((g["zone1_hit_count"] >= 3).mean(), 4),
            f"recent_{n}_hit_zone1_ge_4": round((g["zone1_hit_count"] >= 4).mean(), 4),
        })
    return pd.DataFrame(rows)


def make_power_rank_stats(detail_df: pd.DataFrame) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()
    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
    df["zone1_hit_count"] = pd.to_numeric(df["zone1_hit_count"], errors="coerce")

    rows = []
    for (model, rank), g in df.groupby(["model", "rank"], dropna=True):
        rows.append({
            "model": model,
            "rank": int(rank),
            "count": len(g),
            "avg_zone1_hits": round(g["zone1_hit_count"].mean(), 4),
            "hit_zone1_ge_2": round((g["zone1_hit_count"] >= 2).mean(), 4),
            "hit_zone1_ge_3": round((g["zone1_hit_count"] >= 3).mean(), 4),
        })
    return pd.DataFrame(rows).sort_values(["model", "rank"]).reset_index(drop=True)


def make_power_score_band_stats(detail_df: pd.DataFrame) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()
    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["zone1_hit_count"] = pd.to_numeric(df["zone1_hit_count"], errors="coerce")
    df = df[df["score"].notna()].copy()
    if df.empty:
        return pd.DataFrame()

    score_band = qcut_safe(df["score"])
    if score_band is None:
        return pd.DataFrame()
    df["score_band"] = score_band

    rows = []
    for (model, band), g in df.groupby(["model", "score_band"]):
        rows.append({
            "model": model,
            "score_band": str(band),
            "count": len(g),
            "avg_zone1_hits": round(g["zone1_hit_count"].mean(), 4),
            "hit_zone1_ge_2": round((g["zone1_hit_count"] >= 2).mean(), 4),
            "hit_zone1_ge_3": round((g["zone1_hit_count"] >= 3).mean(), 4),
        })
    return pd.DataFrame(rows).sort_values(["model", "score_band"]).reset_index(drop=True)


def make_power_batch_stats(detail_df: pd.DataFrame) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()
    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["zone1_hit_count"] = pd.to_numeric(df["zone1_hit_count"], errors="coerce")

    rows = []
    for (batch_id, model), g in df.groupby(["batch_id", "model"]):
        rows.append({
            "batch_id": batch_id,
            "model": model,
            "count": len(g),
            "avg_zone1_hits": round(g["zone1_hit_count"].mean(), 4),
            "hit_zone1_ge_2": round((g["zone1_hit_count"] >= 2).mean(), 4),
            "hit_zone1_ge_3": round((g["zone1_hit_count"] >= 3).mean(), 4),
        })
    return pd.DataFrame(rows).sort_values(["batch_id", "model"]).reset_index(drop=True)


def merge_power_report(summary_df: pd.DataFrame, detail_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    summary_df = safe_numeric(summary_df, [
        "total_predictions", "avg_zone1_hits", "avg_score", "score_hit_corr",
        "zone2_hit_rate", "rank1_avg_zone1_hits", "rank2_avg_zone1_hits", "rank3_avg_zone1_hits",
        "hit_zone1_ge_1", "hit_zone1_ge_2", "hit_zone1_ge_3",
        "hit_zone1_ge_4", "hit_zone1_ge_5", "hit_zone1_ge_6",
        "both_zone1_zone2_hit_rate",
        "prize_top", "prize_second", "prize_third", "prize_fourth",
        "prize_fifth", "prize_sixth", "prize_seventh", "prize_general"
    ])

    recent10 = make_power_recent_stats(detail_df, 10)
    recent30 = make_power_recent_stats(detail_df, 30)

    result = summary_df.merge(recent10, on="model", how="left")
    result = result.merge(recent30, on="model", how="left")
    result = result.sort_values(by=["prize_general", "hit_zone1_ge_3", "avg_zone1_hits", "zone2_hit_rate"], ascending=False).reset_index(drop=True)
    result["model_rank"] = result.index + 1
    cols = ["model_rank"] + [c for c in result.columns if c != "model_rank"]
    return result[cols]


# ========= 649 =========

def make_649_recent_stats(detail_df: pd.DataFrame, n: int) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()

    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["target_draw_date"] = pd.to_datetime(df["target_draw_date"], errors="coerce")
    df["main_hit_count"] = pd.to_numeric(df["main_hit_count"], errors="coerce")
    df["special_hit"] = pd.to_numeric(df["special_hit"], errors="coerce")
    df = df.sort_values(["model", "target_draw_date", "group_id"])

    rows = []
    for model, g in df.groupby("model"):
        g = g.tail(n)
        rows.append({
            "model": model,
            f"recent_{n}_count": len(g),
            f"recent_{n}_avg_main_hits": round(g["main_hit_count"].mean(), 4),
            f"recent_{n}_special_hit_rate": round(g["special_hit"].mean(), 4),
            f"recent_{n}_hit_main_ge_2": round((g["main_hit_count"] >= 2).mean(), 4),
            f"recent_{n}_hit_main_ge_3": round((g["main_hit_count"] >= 3).mean(), 4),
            f"recent_{n}_hit_main_ge_4": round((g["main_hit_count"] >= 4).mean(), 4),
        })
    return pd.DataFrame(rows)


def make_649_rank_stats(detail_df: pd.DataFrame) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()
    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
    df["main_hit_count"] = pd.to_numeric(df["main_hit_count"], errors="coerce")

    rows = []
    for (model, rank), g in df.groupby(["model", "rank"], dropna=True):
        rows.append({
            "model": model,
            "rank": int(rank),
            "count": len(g),
            "avg_main_hits": round(g["main_hit_count"].mean(), 4),
            "hit_main_ge_2": round((g["main_hit_count"] >= 2).mean(), 4),
            "hit_main_ge_3": round((g["main_hit_count"] >= 3).mean(), 4),
        })
    return pd.DataFrame(rows).sort_values(["model", "rank"]).reset_index(drop=True)


def make_649_score_band_stats(detail_df: pd.DataFrame) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()
    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["main_hit_count"] = pd.to_numeric(df["main_hit_count"], errors="coerce")
    df = df[df["score"].notna()].copy()
    if df.empty:
        return pd.DataFrame()

    score_band = qcut_safe(df["score"])
    if score_band is None:
        return pd.DataFrame()
    df["score_band"] = score_band

    rows = []
    for (model, band), g in df.groupby(["model", "score_band"]):
        rows.append({
            "model": model,
            "score_band": str(band),
            "count": len(g),
            "avg_main_hits": round(g["main_hit_count"].mean(), 4),
            "hit_main_ge_2": round((g["main_hit_count"] >= 2).mean(), 4),
            "hit_main_ge_3": round((g["main_hit_count"] >= 3).mean(), 4),
        })
    return pd.DataFrame(rows).sort_values(["model", "score_band"]).reset_index(drop=True)


def make_649_batch_stats(detail_df: pd.DataFrame) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame()
    df = detail_df[detail_df["is_verified"].astype(str) == "1"].copy()
    if df.empty:
        return pd.DataFrame()

    df["main_hit_count"] = pd.to_numeric(df["main_hit_count"], errors="coerce")

    rows = []
    for (batch_id, model), g in df.groupby(["batch_id", "model"]):
        rows.append({
            "batch_id": batch_id,
            "model": model,
            "count": len(g),
            "avg_main_hits": round(g["main_hit_count"].mean(), 4),
            "hit_main_ge_2": round((g["main_hit_count"] >= 2).mean(), 4),
            "hit_main_ge_3": round((g["main_hit_count"] >= 3).mean(), 4),
        })
    return pd.DataFrame(rows).sort_values(["batch_id", "model"]).reset_index(drop=True)


def merge_649_report(summary_df: pd.DataFrame, detail_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    summary_df = safe_numeric(summary_df, [
        "total_predictions", "avg_main_hits", "avg_score", "score_hit_corr",
        "special_hit_rate", "rank1_avg_main_hits", "rank2_avg_main_hits", "rank3_avg_main_hits",
        "hit_main_ge_1", "hit_main_ge_2", "hit_main_ge_3",
        "hit_main_ge_4", "hit_main_ge_5", "hit_main_ge_6",
        "both_main_special_hit_rate",
        "prize_top", "prize_second", "prize_third", "prize_fourth",
        "prize_fifth", "prize_sixth", "prize_seventh"
    ])

    recent10 = make_649_recent_stats(detail_df, 10)
    recent30 = make_649_recent_stats(detail_df, 30)

    result = summary_df.merge(recent10, on="model", how="left")
    result = result.merge(recent30, on="model", how="left")
    result = result.sort_values(by=["prize_seventh", "hit_main_ge_3", "avg_main_hits", "special_hit_rate"], ascending=False).reset_index(drop=True)
    result["model_rank"] = result.index + 1
    cols = ["model_rank"] + [c for c in result.columns if c != "model_rank"]
    return result[cols]


# ========= 文字報表 =========

def build_text_report(report_539: pd.DataFrame, report_power: pd.DataFrame, report_649: pd.DataFrame) -> str:
    lines = []
    lines.append("===== 自動驗證命中率報表 =====")
    lines.append("")

    lines.append("【539】")
    if report_539.empty:
        lines.append("目前無可用資料")
    else:
        top = report_539.iloc[0]
        lines.append(f"最佳模型：{top['model']}")
        lines.append(f"總預測組數：{top['total_predictions']}")
        lines.append(f"平均命中數：{top['avg_hits']}")
        lines.append(f"平均分數：{top.get('avg_score', '')}")
        lines.append(f"分數/命中相關：{top.get('score_hit_corr', '')}")
        lines.append(f"命中2碼以上比率：{top['hit_ge_2']}")
        lines.append(f"命中3碼以上比率：{top['hit_ge_3']}")
        lines.append(f"Rank1平均命中：{top.get('rank1_avg_hits', '')}")
        lines.append(f"最近10組平均命中：{top.get('recent_10_avg_hits', '')}")
        lines.append(f"最近30組平均命中：{top.get('recent_30_avg_hits', '')}")

    lines.append("")
    lines.append("【威力彩】")
    if report_power.empty:
        lines.append("目前無可用資料")
    else:
        top = report_power.iloc[0]
        lines.append(f"最佳模型：{top['model']}")
        lines.append(f"總預測組數：{top['total_predictions']}")
        lines.append(f"第一區平均命中數：{top['avg_zone1_hits']}")
        lines.append(f"平均分數：{top.get('avg_score', '')}")
        lines.append(f"分數/命中相關：{top.get('score_hit_corr', '')}")
        lines.append(f"第二區命中率：{top['zone2_hit_rate']}")
        lines.append(f"第一區命中3碼以上比率：{top['hit_zone1_ge_3']}")
        lines.append(f"普獎次數：{top.get('prize_general', '')}")
        lines.append(f"Rank1第一區平均命中：{top.get('rank1_avg_zone1_hits', '')}")
        lines.append(f"最近10組第一區平均命中：{top.get('recent_10_avg_zone1_hits', '')}")
        lines.append(f"最近30組第一區平均命中：{top.get('recent_30_avg_zone1_hits', '')}")

    lines.append("")
    lines.append("【649】")
    if report_649.empty:
        lines.append("目前無可用資料")
    else:
        top = report_649.iloc[0]
        lines.append(f"最佳模型：{top['model']}")
        lines.append(f"總預測組數：{top['total_predictions']}")
        lines.append(f"主號平均命中數：{top['avg_main_hits']}")
        lines.append(f"平均分數：{top.get('avg_score', '')}")
        lines.append(f"分數/命中相關：{top.get('score_hit_corr', '')}")
        lines.append(f"特別號命中率：{top['special_hit_rate']}")
        lines.append(f"主號命中3碼以上比率：{top['hit_main_ge_3']}")
        lines.append(f"柒獎次數：{top.get('prize_seventh', '')}")
        lines.append(f"Rank1主號平均命中：{top.get('rank1_avg_main_hits', '')}")
        lines.append(f"最近10組主號平均命中：{top.get('recent_10_avg_main_hits', '')}")
        lines.append(f"最近30組主號平均命中：{top.get('recent_30_avg_main_hits', '')}")

    lines.append("")
    lines.append("===== 報表結束 =====")
    return "\n".join(lines)


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    detail_539 = load_csv_if_exists(FILE_539_DETAIL)
    summary_539 = load_csv_if_exists(FILE_539_SUMMARY)

    detail_power = load_csv_if_exists(FILE_POWER_DETAIL)
    summary_power = load_csv_if_exists(FILE_POWER_SUMMARY)

    detail_649 = load_csv_if_exists(FILE_649_DETAIL)
    summary_649 = load_csv_if_exists(FILE_649_SUMMARY)

    report_539 = merge_539_report(summary_539, detail_539)
    report_power = merge_power_report(summary_power, detail_power)
    report_649 = merge_649_report(summary_649, detail_649)

    rank_539 = make_539_rank_stats(detail_539)
    score_539 = make_539_score_band_stats(detail_539)
    batch_539 = make_539_batch_stats(detail_539)

    rank_power = make_power_rank_stats(detail_power)
    score_power = make_power_score_band_stats(detail_power)
    batch_power = make_power_batch_stats(detail_power)

    rank_649 = make_649_rank_stats(detail_649)
    score_649 = make_649_score_band_stats(detail_649)
    batch_649 = make_649_batch_stats(detail_649)

    report_539.to_csv(REPORT_539_CSV, index=False, encoding="utf-8-sig")
    report_power.to_csv(REPORT_POWER_CSV, index=False, encoding="utf-8-sig")
    report_649.to_csv(REPORT_649_CSV, index=False, encoding="utf-8-sig")

    rank_539.to_csv(REPORT_539_RANK_CSV, index=False, encoding="utf-8-sig")
    score_539.to_csv(REPORT_539_SCORE_CSV, index=False, encoding="utf-8-sig")
    batch_539.to_csv(REPORT_539_BATCH_CSV, index=False, encoding="utf-8-sig")

    rank_power.to_csv(REPORT_POWER_RANK_CSV, index=False, encoding="utf-8-sig")
    score_power.to_csv(REPORT_POWER_SCORE_CSV, index=False, encoding="utf-8-sig")
    batch_power.to_csv(REPORT_POWER_BATCH_CSV, index=False, encoding="utf-8-sig")

    rank_649.to_csv(REPORT_649_RANK_CSV, index=False, encoding="utf-8-sig")
    score_649.to_csv(REPORT_649_SCORE_CSV, index=False, encoding="utf-8-sig")
    batch_649.to_csv(REPORT_649_BATCH_CSV, index=False, encoding="utf-8-sig")

    report_text = build_text_report(report_539, report_power, report_649)
    REPORT_TXT.write_text(report_text, encoding="utf-8")

    print("✅ 自動報表輸出完成")
    print(f"文字報表：{REPORT_TXT}")
    print(f"539 報表：{REPORT_539_CSV}")
    print(f"威力彩報表：{REPORT_POWER_CSV}")
    print(f"649 報表：{REPORT_649_CSV}")
    print("\n" + report_text)


if __name__ == "__main__":
    main()