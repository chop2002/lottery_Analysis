import os
import pandas as pd

INPUT_PATH = "data/539/clean/539_history.csv"
OUTPUT_PATH = "data/539/sequence/539_sequences.csv"


def build_sequences():
    # 讀資料
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

    # 日期排序（確保由舊到新）
    df["draw_date"] = pd.to_datetime(df["draw_date"])
    df = df.sort_values("draw_date").reset_index(drop=True)

    # 只處理這些欄位
    fields = ["n1", "n2", "n3", "n4", "n5"]

    records = []

    # 對每一欄處理
    for field in fields:
        # 逐列掃描（重點）
        for i in range(len(df) - 1):
            current_value = df.loc[i, field]
            next_value = df.loc[i + 1, field]

            # 跳過空值
            if pd.isna(current_value) or pd.isna(next_value):
                continue

            records.append(
                {
                    "field": field,
                    "current_value": int(current_value),
                    "next_value": int(next_value),
                    "current_date": df.loc[i, "draw_date"].strftime("%Y-%m-%d"),
                    "next_date": df.loc[i + 1, "draw_date"].strftime("%Y-%m-%d"),
                }
            )

    # 轉成 DataFrame
    df_out = pd.DataFrame(records)

    # 建資料夾
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # 存檔（不做任何去重！）
    df_out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 建立完成（完整保留所有轉移）")
    print(f"輸出：{OUTPUT_PATH}")
    print(f"筆數：{len(df_out)}")


if __name__ == "__main__":
    build_sequences()
