import os
import pandas as pd

INPUT_PATH = "data/power/clean/power_history.csv"
OUTPUT_PATH = "data/power/sequence/power_sequences.csv"


def build_power_sequences():
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

    df["draw_date"] = pd.to_datetime(df["draw_date"], errors="coerce")
    df = df.dropna(subset=["draw_date"])
    df = df.sort_values("draw_date").reset_index(drop=True)

    fields = ["n1", "n2", "n3", "n4", "n5", "n6", "sp"]

    records = []

    for i in range(len(df) - 1):
        current_row = df.iloc[i]
        next_row = df.iloc[i + 1]

        for field in fields:
            current_value = current_row[field]
            next_value = next_row[field]

            if pd.notna(current_value) and pd.notna(next_value):
                records.append(
                    {
                        "field": field,
                        "current_value": int(current_value),
                        "next_value": int(next_value),
                        "current_date": current_row["draw_date"].strftime("%Y-%m-%d"),
                        "next_date": next_row["draw_date"].strftime("%Y-%m-%d"),
                    }
                )

    df_out = pd.DataFrame(records)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("✅ 威力彩 sequence 建立完成")
    print(f"輸出：{OUTPUT_PATH}")
    print(f"筆數：{len(df_out)}")
    print("-" * 60)
    print(df_out.head(10).to_string(index=False))
    print("-" * 60)


if __name__ == "__main__":
    build_power_sequences()
