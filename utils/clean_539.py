import os
import pandas as pd

# ===== 路徑設定（相對於專案根目錄）=====
RAW_PATH = "data/539/raw/539_raw_pilio.csv"
OUT_PATH = "data/539/clean/539_history.csv"


def clean_539():
    # 1) 讀取 raw
    df = pd.read_csv(RAW_PATH, encoding="utf-8")

    # 2) 去掉空白欄（例如你那個空欄）
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # 3) 欄位重新命名（依你原始欄位）
    rename_map = {
        "期別": "draw_no",
        "開獎日期": "draw_date",
        "獎號1": "n1",
        "獎號2": "n2",
        "獎號3": "n3",
        "獎號4": "n4",
        "獎號5": "n5",
    }
    df = df.rename(columns=rename_map)

    # 4) 只保留需要欄位（防止多餘欄位混入）
    keep_cols = ["draw_date", "draw_no", "n1", "n2", "n3", "n4", "n5"]
    df = df[keep_cols]

    # 5) 日期格式統一 YYYY-MM-DD
    df["draw_date"] = pd.to_datetime(df["draw_date"], errors="coerce").dt.strftime(
        "%Y-%m-%d"
    )

    # 6) 號碼轉數字（避免 '01' 這種字串）
    num_cols = ["n1", "n2", "n3", "n4", "n5"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 7) 加來源欄
    df["source"] = "pilio"

    # 8) 去重（優先用期別）
    if "draw_no" in df.columns:
        df = df.drop_duplicates(subset=["draw_no"])
    else:
        df = df.drop_duplicates(subset=["draw_date"])

    # 9) 排序（由舊到新）
    df = df.sort_values(by="draw_date")

    # 10) 建立輸出資料夾（如果不存在）
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    # 11) 輸出
    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 清洗完成")
    print(f"輸出檔案：{OUT_PATH}")
    print(f"筆數：{len(df)}")


if __name__ == "__main__":
    clean_539()
