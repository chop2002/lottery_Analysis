import pandas as pd

INPUT_PATH = "data/539/sequence/539_sequences.csv"


def normalize_field(field_name):
    field_name = field_name.strip().lower()

    if field_name in ["1", "2", "3", "4", "5"]:
        return f"n{field_name}"

    if field_name in ["n1", "n2", "n3", "n4", "n5"]:
        return field_name

    return None


def query_sequence(field_name, current_value):
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

    field_name = normalize_field(field_name)
    if field_name is None:
        print("欄位輸入錯誤，請輸入 1~5 或 n1~n5")
        return

    result = df[
        (df["field"] == field_name) & (df["current_value"] == current_value)
    ].copy()

    if result.empty:
        print(f"查無資料：{field_name} = {current_value}")
        return

    print(f"查詢條件：{field_name} = {current_value}")
    print(f"共找到 {len(result)} 筆轉移資料")
    print("-" * 60)

    for _, row in result.iterrows():
        print(
            f"{row['current_date']}  {field_name}={row['current_value']} "
            f"-> 下一期 {row['next_date']} {field_name}={row['next_value']}"
        )

    print("-" * 60)
    print("下一期值序列（依歷史順序）：")
    print(",".join(result["next_value"].astype(int).astype(str).tolist()))


if __name__ == "__main__":
    field_name = input("請輸入欄位（1~5 或 n1~n5）：").strip()
    current_value = int(input("請輸入號碼：").strip())

    query_sequence(field_name, current_value)
