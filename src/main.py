# src/main.py
from __future__ import annotations

import pandas as pd
from pathlib import Path
from datetime import datetime
import random

from src.generate_best_combinations import run as run_best_combinations

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
        except Exception:
            continue
    return nums


# =========================
# 讀取
# =========================
def load_draws(game):
    path = BASE / game / "draws.csv"
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案: {path}")
    return pd.read_csv(path)


# =========================
# 權重模型
# =========================
def build_weights(df, max_num, recent_n=200):
    df_recent = df.tail(recent_n).reset_index(drop=True)

    freq = {i: 0 for i in range(1, max_num + 1)}
    last_seen = {i: None for i in range(1, max_num + 1)}

    for idx, row in df_recent.iterrows():
        nums = clean_numbers(row[1:])
        for n in nums:
            if 1 <= n <= max_num:
                freq[n] += 1
                last_seen[n] = idx

    weights = {}
    total_rows = len(df_recent)

    for n in range(1, max_num + 1):
        f = freq[n]

        if last_seen[n] is None:
            gap = total_rows
        else:
            gap = total_rows - 1 - last_seen[n]

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
def predict_539(df):
    return weighted_pick(build_weights(df, 39), 5)


def predict_649(df):
    return weighted_pick(build_weights(df, 49), 6)


def predict_power(df):
    main = weighted_pick(build_weights(df, 38), 6)
    special = random.randint(1, 8)
    return main + [special]


# =========================
# 儲存預測（含時間）
# =========================
def save_prediction(game, numbers):
    path = BASE / game / "predictions.csv"

    now = datetime.now()
    date = now.strftime("%Y/%m/%d")
    time = now.strftime("%H:%M:%S")

    cols = ["date", "time"] + [f"n{i}" for i in range(1, len(numbers) + 1)]
    df_new = pd.DataFrame([[date, time] + numbers], columns=cols)

    if path.exists():
        old = pd.read_csv(path)
        df_new = pd.concat([old, df_new], ignore_index=True)

    df_new.to_csv(path, index=False, encoding="utf-8-sig")
    return df_new.iloc[-1]


# =========================
# 驗證
# =========================
def verify(game):
    draws = load_draws(game)

    pred_path = BASE / game / "predictions.csv"
    if not pred_path.exists():
        raise FileNotFoundError(f"找不到檔案: {pred_path}")

    preds = pd.read_csv(pred_path)

    draw_row = draws.iloc[-1]
    pred_row = preds.iloc[-1]

    if game == "power":
        draw_nums = set(clean_numbers(draw_row[1:7]))
        pred_nums = set(clean_numbers(pred_row[2:8]))
    else:
        draw_nums = set(clean_numbers(draw_row[1:]))
        pred_nums = set(clean_numbers(pred_row[2:]))

    hit = len(draw_nums & pred_nums)

    return hit, sorted(draw_nums), sorted(pred_nums)


# =========================
# Excel（預測摘要）
# =========================
def export_excel(results):
    now = datetime.now()
    filename = now.strftime("report_%Y%m%d_%H%M%S.xlsx")
    path = BASE / filename

    df = pd.DataFrame(results, columns=["game", "prediction", "draw", "hit"])
    df.insert(0, "time", now.strftime("%H:%M:%S"))
    df.insert(0, "date", now.strftime("%Y/%m/%d"))

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False, sheet_name="report")

    print(f"\n📊 已輸出: {path}")
    return path


# =========================
# 執行最強組合
# =========================
def run_best_reports(ts: str):
    print("\n===== 最強組合開始 =====")

    run_best_combinations(
        game="539",
        csv="data/539/draws.csv",
        top=8,
        output=f"data/best_539_{ts}.xlsx",
    )

    run_best_combinations(
        game="649",
        csv="data/649/draws.csv",
        top=8,
        output=f"data/best_649_{ts}.xlsx",
    )

    run_best_combinations(
        game="power",
        csv="data/power/draws.csv",
        top=8,
        output=f"data/best_power_{ts}.xlsx",
    )

    print("\n===== 最強組合完成 =====")


# =========================
# 單一彩種流程
# =========================
def run_prediction_for_game(game, predict_func):
    df = load_draws(game)
    pred = predict_func(df)
    save_prediction(game, pred)
    hit, draw_nums, pred_nums = verify(game)

    print(f"\n[{game}]")
    print("預測:", pred_nums)
    print("開獎:", draw_nums)
    print("命中:", hit)

    return [game, pred_nums, draw_nums, hit]


# =========================
# 主流程
# =========================
def main():
    print("===== 預測系統開始 =====")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []

    results.append(run_prediction_for_game("539", predict_539))
    results.append(run_prediction_for_game("649", predict_649))
    results.append(run_prediction_for_game("power", predict_power))

    export_excel(results)
    run_best_reports(ts)

    print("\n===== 完成 =====")


if __name__ == "__main__":
    main()