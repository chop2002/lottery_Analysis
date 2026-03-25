import os
import pandas as pd

RAW_PATH = "data/power/raw/power_raw.csv"
OUT_PATH = "data/power/clean/power_history.csv"


def clean_power():
    df = pd.read_csv(RAW_PATH, encoding="utf-8-sig")

    # 去掉空白欄 / Unnamed 欄
    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]
    df = df.loc[:, [str(col).strip() != "" for col in df.columns]]

    rename_map = {
        "期別": "draw_no",
        "開獎日期": "draw_date",
        "獎號1": "n1",
        "獎號2": "n2",
        "獎號3": "n3",
        "獎號4": "n4",
        "獎號5": "n5",
        "獎號6": "n6",
        "第二區": "sp",
    }

    df = df.rename(columns=rename_map)

    keep_cols = ["draw_date", "draw_no", "n1", "n2", "n3", "n4", "n5", "n6", "sp"]
    df = df[keep_cols]

    # 日期格式統一
    df["draw_date"] = pd.to_datetime(df["draw_date"], errors="coerce")
    df = df.dropna(subset=["draw_date"])
    df["draw_date"] = df["draw_date"].dt.strftime("%Y-%m-%d")

    # 數字欄轉數字，並轉成整數格式
    num_cols = ["n1", "n2", "n3", "n4", "n5", "n6", "sp"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # 期別保留為字串較穩
    df["draw_no"] = df["draw_no"].astype(str).str.strip()

    # 加來源欄
    df["source"] = "power_raw"

    # 去重
    df = df.drop_duplicates(subset=["draw_no"])

    # 排序
    df["draw_date_sort"] = pd.to_datetime(df["draw_date"], errors="coerce")
    df = (
        df.sort_values("draw_date_sort")
        .drop(columns=["draw_date_sort"])
        .reset_index(drop=True)
    )

    # 建資料夾
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    # 輸出
    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 威力彩清洗完成")
    print(f"輸出檔案：{OUT_PATH}")
    print(f"筆數：{len(df)}")
    print("-" * 60)
    print(df.head(5).to_string(index=False))
    print("-" * 60)


if __name__ == "__main__":
    clean_power()
