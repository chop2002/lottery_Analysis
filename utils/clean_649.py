import os
import pandas as pd

RAW_PATH = "data/649/raw/649_raw.csv"
OUT_PATH = "data/649/clean/649_history.csv"


def clean_649():
    df = pd.read_csv(RAW_PATH, encoding="utf-8-sig")

    df.columns = df.columns.astype(str).str.strip()

    # 去掉空白欄 / Unnamed 欄
    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed", na=False)]
    df = df.loc[:, [str(col).strip() != "" for col in df.columns]]

    print("原始欄位：")
    print(list(df.columns))
    print("-" * 60)

    rename_candidates = {
        "draw_no": ["期別", "期數", "期號", "term"],
        "draw_date": ["開獎日期", "日期", "開獎日", "date"],
        "n1": ["獎號1", "號碼1", "第一個號碼", "n1"],
        "n2": ["獎號2", "號碼2", "第二個號碼", "n2"],
        "n3": ["獎號3", "號碼3", "第三個號碼", "n3"],
        "n4": ["獎號4", "號碼4", "第四個號碼", "n4"],
        "n5": ["獎號5", "號碼5", "第五個號碼", "n5"],
        "n6": ["獎號6", "號碼6", "第六個號碼", "n6"],
        "sp": ["特別號", "特獎號", "特別球", "第二區", "sp"],
    }

    rename_map = {}
    current_cols = set(df.columns)

    for target, candidates in rename_candidates.items():
        for c in candidates:
            if c in current_cols:
                rename_map[c] = target
                break

    df = df.rename(columns=rename_map)

    print("轉換後欄位：")
    print(list(df.columns))
    print("-" * 60)

    required_cols = ["draw_date", "draw_no", "n1", "n2", "n3", "n4", "n5", "n6", "sp"]
    missing_cols = [c for c in required_cols if c not in df.columns]

    if missing_cols:
        print("缺少必要欄位：", missing_cols)
        raise KeyError(f"缺少必要欄位：{missing_cols}")

    df = df[required_cols].copy()

    # 日期格式
    df["draw_date"] = pd.to_datetime(df["draw_date"], errors="coerce")
    df = df.dropna(subset=["draw_date"])
    df["draw_date"] = df["draw_date"].dt.strftime("%Y-%m-%d")

    # 數字欄轉整數
    num_cols = ["n1", "n2", "n3", "n4", "n5", "n6", "sp"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # 期別保留字串
    df["draw_no"] = df["draw_no"].astype(str).str.strip()

    # 用完整開獎內容去重
    df = df.drop_duplicates(
        subset=["draw_date", "draw_no", "n1", "n2", "n3", "n4", "n5", "n6", "sp"]
    )

    # 排序
    df["draw_date_sort"] = pd.to_datetime(df["draw_date"], errors="coerce")
    df = (
        df.sort_values(["draw_date_sort", "draw_no"])
        .drop(columns=["draw_date_sort"])
        .reset_index(drop=True)
    )

    # 加來源欄
    df["source"] = "649_raw"

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 大樂透 clean 完成")
    print(f"輸出檔案：{OUT_PATH}")
    print(f"筆數：{len(df)}")
    print("-" * 60)
    print(df.head(10).to_string(index=False))
    print("-" * 60)


if __name__ == "__main__":
    clean_649()
