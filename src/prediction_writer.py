from __future__ import annotations
from pathlib import Path
import pandas as pd


def normalize_num(x) -> str:
    if x is None or str(x).strip() == "":
        return ""
    try:
        return f"{int(float(x)):02d}"
    except Exception:
        s = str(x).strip()
        if s.isdigit():
            return f"{int(s):02d}"
        return s


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_predictions_csv(file_path: Path, df_new: pd.DataFrame, required_columns: list[str]) -> None:
    ensure_parent_dir(file_path)

    missing = [c for c in required_columns if c not in df_new.columns]
    if missing:
        raise ValueError(f"缺少必要欄位：{missing}")

    df_new = df_new.copy()

    # 日期標準化
    df_new["predict_date"] = pd.to_datetime(df_new["predict_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_new["target_draw_date"] = pd.to_datetime(df_new["target_draw_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # 文字欄位
    for c in ["lottery", "batch_id", "model", "group_id"]:
        if c in df_new.columns:
            df_new[c] = df_new[c].astype(str).str.strip()

    # 數值欄位
    if "rank" in df_new.columns:
        df_new["rank"] = pd.to_numeric(df_new["rank"], errors="coerce").astype("Int64")
    if "score" in df_new.columns:
        df_new["score"] = pd.to_numeric(df_new["score"], errors="coerce")

    # 號碼欄位補成兩位
    protected_cols = {
        "predict_date", "target_draw_date", "lottery", "batch_id",
        "model", "group_id", "rank", "score"
    }
    for c in df_new.columns:
        if c not in protected_cols:
            df_new[c] = df_new[c].apply(normalize_num)

    # 補齊欄位順序
    df_new = df_new[required_columns]

    if file_path.exists():
        df_old = pd.read_csv(file_path, dtype=str).fillna("")
        df_old = df_old.reindex(columns=required_columns, fill_value="")
        df_all = pd.concat([df_old, df_new.astype(str)], ignore_index=True)
    else:
        df_all = df_new.astype(str)

    # 去除完全重複紀錄
    df_all = df_all.drop_duplicates()

    df_all.to_csv(file_path, index=False, encoding="utf-8-sig")