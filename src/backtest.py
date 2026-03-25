import pandas as pd
from pathlib import Path
from datetime import datetime
import random

BASE = Path("data")


# =========================
# 清洗
# =========================
def clean_numbers(series):
    nums = []
    for x in series:
        if pd.isna(x):
            continue
        try:
            nums.append(int(x))
        except:
            continue
    return nums


# =========================
# 權重模型（跟 main 一樣）
# =========================
def build_weights(df, max_num, recent_n=200):
    df_recent = df.tail(recent_n)

    freq = {i: 0 for i in range(1, max_num + 1)}
    last_seen = {i: None for i in range(1, max_num + 1)}

    for idx, row in df_recent.iterrows():
        nums = clean_numbers(row[1:])
        for n in nums:
            freq[n] += 1
            last_seen[n] = idx

    weights = {}
    total_rows = len(df_recent)

    for n in range(1, max_num + 1):
        f = freq[n]

        if last_seen[n] is None:
            gap = total_rows
        else:
            gap = total_rows - last_seen[n]

        w = (f * 1.5) + (gap * 1.2)

        if w <= 0:
            w = 1

        weights[n] = w

    return weights


# =========================
# 抽號
# =========================
def weighted_pick(weights, k):
    nums = list(weights.keys())
    w = list(weights.values())

    if sum(w) == 0:
        return sorted(random.sample(nums, k))

    selected = set()

    while len(selected) < k:
        pick = random.choices(nums, weights=w, k=1)[0]
        selected.add(pick)

    return sorted(selected)


# =========================
# 預測
# =========================
def predict(df, game):
    if game == "539":
        return weighted_pick(build_weights(df, 39), 5)
    elif game == "649":
        return weighted_pick(build_weights(df, 49), 6)
    elif game == "power":
        main = weighted_pick(build_weights(df, 38), 6)
        special = random.randint(1, 8)
        return main + [special]


# =========================
# 回測
# =========================
def run_backtest(game, test_n=500):
    df = pd.read_csv(BASE / game / "draws.csv")

    results = []

    for i in range(len(df) - test_n, len(df) - 1):
        train_df = df.iloc[:i]
        actual = clean_numbers(df.iloc[i + 1][1:])

        pred = predict(train_df, game)

        if game == "power":
            pred_main = set(pred[:-1])
            actual_main = set(actual[:-1])
            hit = len(pred_main & actual_main)
        else:
            hit = len(set(pred) & set(actual))

        results.append({
            "index": i,
            "prediction": pred,
            "actual": actual,
            "hit": hit
        })

    return pd.DataFrame(results)


# =========================
# 統計
# =========================
def summarize(df):
    summary = {}

    summary["平均命中"] = round(df["hit"].mean(), 3)

    for i in range(0, df["hit"].max() + 1):
        summary[f"{i}中"] = (df["hit"] == i).sum()

    return pd.DataFrame([summary])


# =========================
# 主程式
# =========================
def main():
    print("===== 回測開始 =====")

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = BASE / f"backtest_{now}.xlsx"

    with pd.ExcelWriter(output) as writer:

        for game in ["539", "649", "power"]:
            print(f"\n[{game}] 回測中...")

            df_result = run_backtest(game, test_n=500)
            df_summary = summarize(df_result)

            df_result.to_excel(writer, sheet_name=f"{game}_detail", index=False)
            df_summary.to_excel(writer, sheet_name=f"{game}_summary", index=False)

            print(df_summary)

    print(f"\n📊 回測完成: {output}")


if __name__ == "__main__":
    main()