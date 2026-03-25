from __future__ import annotations

from pathlib import Path
from datetime import datetime
import pandas as pd

from src.main import clean_numbers


BASE = Path("data")
FINAL_PRED_PATH = BASE / "final_predictions.csv"
VERIFY_XLSX_PATH = BASE / f"final_verify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

GAME_CONFIG = {
    "539": {"pick": 5, "special": False},
    "649": {"pick": 6, "special": False},
    "power": {"pick": 6, "special": True},
}


# =========================
# 讀檔
# =========================
def load_final_predictions() -> pd.DataFrame:
    if not FINAL_PRED_PATH.exists():
        raise FileNotFoundError(f"找不到檔案: {FINAL_PRED_PATH}")
    return pd.read_csv(FINAL_PRED_PATH)


def load_draws(game: str) -> pd.DataFrame:
    path = BASE / game / "draws.csv"
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案: {path}")
    return pd.read_csv(path)


# =========================
# 取得最新開獎
# =========================
def get_latest_draw_info(game: str) -> dict:
    cfg = GAME_CONFIG[game]
    df = load_draws(game)
    row = df.iloc[-1]

    draw_date = None
    for col in ["draw_date", "date", "開獎日期", "开奖日期"]:
        if col in df.columns:
            try:
                draw_date = pd.to_datetime(row[col]).strftime("%Y/%m/%d")
            except Exception:
                draw_date = str(row[col])
            break

    nums = clean_numbers(row)
    if cfg["special"]:
        draw_nums = nums[:cfg["pick"]]
        special = nums[cfg["pick"]] if len(nums) > cfg["pick"] else None
    else:
        draw_nums = nums[:cfg["pick"]]
        special = None

    return {
        "draw_date": draw_date,
        "draw_numbers": draw_nums,
        "draw_special": special,
    }


# =========================
# 取某彩種最新一批預測
# =========================
def get_latest_prediction_batch(preds: pd.DataFrame, game: str) -> pd.DataFrame:
    one_game = preds[preds["game"].astype(str).str.lower() == game.lower()].copy()
    if one_game.empty:
        return pd.DataFrame()

    one_game["dt"] = pd.to_datetime(
        one_game["date"].astype(str) + " " + one_game["time"].astype(str),
        errors="coerce",
    )

    latest_dt = one_game["dt"].max()
    batch = one_game[one_game["dt"] == latest_dt].copy()
    batch = batch.sort_values("set_no").reset_index(drop=True)
    return batch


# =========================
# 驗證單一彩種
# =========================
def verify_game(preds: pd.DataFrame, game: str) -> pd.DataFrame:
    cfg = GAME_CONFIG[game]
    batch = get_latest_prediction_batch(preds, game)
    if batch.empty:
        return pd.DataFrame()

    draw_info = get_latest_draw_info(game)
    draw_set = set(draw_info["draw_numbers"])
    draw_special = draw_info["draw_special"]

    rows = []
    for _, row in batch.iterrows():
        pred_nums = []
        for col in ["n1", "n2", "n3", "n4", "n5", "n6"]:
            if col in batch.columns and pd.notna(row.get(col)):
                pred_nums.append(int(row[col]))

        pred_nums = pred_nums[:cfg["pick"]]
        pred_set = set(pred_nums)

        main_hit = len(pred_set & draw_set)

        pred_special = None
        special_hit = None
        if cfg["special"]:
            pred_special = int(row["special"]) if pd.notna(row.get("special")) else None
            special_hit = int(pred_special == draw_special) if pred_special is not None and draw_special is not None else 0

        rows.append({
            "prediction_date": row["date"],
            "prediction_time": row["time"],
            "game": game,
            "set_no": int(row["set_no"]),
            "pred_numbers": " ".join(f"{n:02d}" for n in pred_nums),
            "pred_special": pred_special,
            "draw_date": draw_info["draw_date"],
            "draw_numbers": " ".join(f"{n:02d}" for n in draw_info["draw_numbers"]),
            "draw_special": draw_special,
            "main_hit": main_hit,
            "special_hit": special_hit,
            "total_hit_note": (
                f"{main_hit}+{special_hit}"
                if cfg["special"]
                else str(main_hit)
            ),
        })

    return pd.DataFrame(rows)


# =========================
# 摘要
# =========================
def build_summary(detail_df: pd.DataFrame) -> pd.DataFrame:
    if detail_df.empty:
        return pd.DataFrame(columns=["game", "sets", "best_main_hit", "avg_main_hit", "special_hit_count"])

    grp = detail_df.groupby("game", dropna=False)
    summary = grp.agg(
        sets=("set_no", "count"),
        best_main_hit=("main_hit", "max"),
        avg_main_hit=("main_hit", "mean"),
    ).reset_index()

    if "special_hit" in detail_df.columns:
        sp = grp["special_hit"].sum(min_count=1).reset_index(name="special_hit_count")
        summary = summary.merge(sp, on="game", how="left")
    else:
        summary["special_hit_count"] = None

    summary["avg_main_hit"] = summary["avg_main_hit"].round(4)
    return summary


# =========================
# 輸出 Excel
# =========================
def export_verify_excel(detail_df: pd.DataFrame, summary_df: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="summary", index=False)
        detail_df.to_excel(writer, sheet_name="detail", index=False)


# =========================
# 主流程
# =========================
def main():
    print("===== 驗證最終選號引擎 =====")

    preds = load_final_predictions()

    detail_frames = []
    for game in ["539", "649", "power"]:
        df = verify_game(preds, game)
        if not df.empty:
            detail_frames.append(df)

    if not detail_frames:
        print("沒有可驗證的最終預測資料")
        return

    detail_df = pd.concat(detail_frames, ignore_index=True)
    summary_df = build_summary(detail_df)

    print("\n===== 驗證結果 =====")
    for _, row in detail_df.iterrows():
        if row["game"] == "power":
            print(
                f"[{row['game']}][第{int(row['set_no'])}組] "
                f"預測: {row['pred_numbers']} + {int(row['pred_special']):02d} | "
                f"開獎: {row['draw_numbers']} + {int(row['draw_special']):02d} | "
                f"命中: {row['main_hit']}+{int(row['special_hit'])}"
            )
        else:
            print(
                f"[{row['game']}][第{int(row['set_no'])}組] "
                f"預測: {row['pred_numbers']} | "
                f"開獎: {row['draw_numbers']} | "
                f"命中: {row['main_hit']}"
            )

    export_verify_excel(detail_df, summary_df, VERIFY_XLSX_PATH)

    print(f"\n📊 已輸出: {VERIFY_XLSX_PATH}")
    print("\n===== 完成 =====")


if __name__ == "__main__":
    main()