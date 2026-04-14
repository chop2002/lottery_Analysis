from __future__ import annotations

from pathlib import Path
from datetime import datetime
import itertools
import random
import pandas as pd

from src.generate_best_combinations import generate_best_combinations
from src.main import build_weights, weighted_pick, clean_numbers


BASE = Path("data")
FINAL_PRED_PATH = BASE / "final_predictions.csv"


GAME_CONFIG = {
    "539": {"maxn": 39, "pick": 5, "special": False},
    "649": {"maxn": 49, "pick": 6, "special": False},
    "power": {"maxn": 38, "pick": 6, "special": True},
}


# =========================
# 讀資料
# =========================
def load_draws(game: str) -> pd.DataFrame:
    path = BASE / game / "draws.csv"
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案: {path}")
    return pd.read_csv(path)


# =========================
# 主模型（權重預測）
# =========================
def predict_base(df: pd.DataFrame, maxn: int, pick: int) -> list[int]:
    weights = build_weights(df, maxn)
    return weighted_pick(weights, pick)


# =========================
# 最強組合模型
# =========================
def get_best_combos(df: pd.DataFrame, maxn: int, pick: int) -> list[list[int]]:
    draws = []

    for _, row in df.iterrows():
        nums = clean_numbers(row[1:])
        nums = [n for n in nums if 1 <= n <= maxn]
        if len(nums) >= pick:
            draws.append(sorted(nums[:pick]))

    best_df, _ = generate_best_combinations(
        draws=draws,
        maxn=maxn,
        pick=pick,
        topn=8,
    )

    combos = []
    for _, r in best_df.iterrows():
        combo = [int(x) for x in str(r["numbers"]).split()]
        if len(combo) == pick:
            combos.append(combo)

    return combos


# =========================
# 融合模型
# =========================
def fuse_models(base_pred: list[int], best_combos: list[list[int]]) -> dict[int, float]:
    score: dict[int, float] = {}

    for n in base_pred:
        score[n] = score.get(n, 0.0) + 2.0

    combo_weights = [1.25, 1.15, 1.05, 1.00, 0.95, 0.90, 0.85, 0.80]
    for idx, combo in enumerate(best_combos):
        w = combo_weights[idx] if idx < len(combo_weights) else 0.75
        for n in combo:
            score[n] = score.get(n, 0.0) + w

    return score


# =========================
# 組合評分
# =========================
def final_combo_score(combo: tuple[int, ...], score_map: dict[int, float], pick: int) -> float:
    base = sum(score_map.get(n, 0.0) for n in combo)

    odd = sum(1 for x in combo if x % 2 == 1)
    even = pick - odd
    diff = abs(odd - even)

    odd_even_bonus = 0.0
    if diff == 0:
        odd_even_bonus = 1.0
    elif diff == 1:
        odd_even_bonus = 0.7
    elif diff == 2:
        odd_even_bonus = 0.3

    zone = len(set((n - 1) // 10 for n in combo))
    zone_bonus = zone * 0.6

    tails = len(set(n % 10 for n in combo))
    tail_bonus = tails * 0.35

    consecutive = 0
    sc = sorted(combo)
    for i in range(1, len(sc)):
        if sc[i] == sc[i - 1] + 1:
            consecutive += 1
    consecutive_penalty = consecutive * 0.35

    return round(base + odd_even_bonus + zone_bonus + tail_bonus - consecutive_penalty, 6)


# =========================
# 推薦排序
# =========================
def rank_final_sets(final_sets: list[list[int]], score_map: dict[int, float], pick: int) -> list[dict]:
    ranked = []

    for combo in final_sets:
        combo_tuple = tuple(combo)
        total_score = final_combo_score(combo_tuple, score_map, pick)

        ranked.append({
            "numbers": list(combo),
            "score": total_score,
        })

    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)
    return ranked


# =========================
# 最終組合（4組 + 優化）
# =========================
def build_final_sets(score_map: dict[int, float], pick: int, target: int = 4) -> list[list[int]]:
    nums_sorted = sorted(score_map.items(), key=lambda x: (-x[1], x[0]))
    pool_size = max(18, pick * 3)
    pool = [n for n, _ in nums_sorted[:pool_size]]

    scored_combos = []
    for combo in itertools.combinations(pool, pick):
        scored_combos.append((combo, final_combo_score(combo, score_map, pick)))

    scored_combos.sort(key=lambda x: x[1], reverse=True)

    results: list[list[int]] = []
    used: dict[int, int] = {}

    for combo, _ in scored_combos:
        combo_set = set(combo)

        if any(len(combo_set & set(r)) >= pick - 1 for r in results):
            continue

        if any(used.get(n, 0) >= 3 for n in combo):
            continue

        odd = sum(1 for x in combo if x % 2 == 1)
        even = pick - odd
        if abs(odd - even) > 3:
            continue

        zone = len(set((n - 1) // 10 for n in combo))
        if zone < 3:
            continue

        tails = len(set(n % 10 for n in combo))
        if tails < max(3, pick - 2):
            continue

        results.append(list(combo))
        for n in combo:
            used[n] = used.get(n, 0) + 1

        if len(results) >= target:
            break

    if len(results) < target:
        for combo, _ in scored_combos:
            if list(combo) not in results:
                results.append(list(combo))
            if len(results) >= target:
                break

    return results[:target]


# =========================
# 威力彩第二區
# =========================
def predict_power_special(df: pd.DataFrame) -> int:
    freq = {i: 0 for i in range(1, 9)}

    for _, row in df.tail(120).iterrows():
        nums = clean_numbers(row)
        if not nums:
            continue
        special = nums[-1]
        if 1 <= special <= 8:
            freq[special] += 1

    nums = list(freq.keys())
    weights = [freq[n] + 1 for n in nums]

    return random.choices(nums, weights=weights, k=1)[0]


# =========================
# 儲存最終預測
# =========================
def save_final_predictions(
    game: str,
    final_sets: list[list[int]],
    special: int | None = None,
) -> pd.DataFrame:
    now = datetime.now()
    date_str = now.strftime("%Y/%m/%d")
    time_str = now.strftime("%H:%M:%S")

    rows = []
    for idx, nums in enumerate(final_sets, start=1):
        row = {
            "date": date_str,
            "time": time_str,
            "game": game,
            "set_no": idx,
            "n1": nums[0] if len(nums) > 0 else None,
            "n2": nums[1] if len(nums) > 1 else None,
            "n3": nums[2] if len(nums) > 2 else None,
            "n4": nums[3] if len(nums) > 3 else None,
            "n5": nums[4] if len(nums) > 4 else None,
            "n6": nums[5] if len(nums) > 5 else None,
            "special": special if game == "power" else None,
        }
        rows.append(row)

    df_new = pd.DataFrame(rows)

    if FINAL_PRED_PATH.exists():
        old = pd.read_csv(FINAL_PRED_PATH)
        df_all = pd.concat([old, df_new], ignore_index=True)
    else:
        df_all = df_new.copy()

    FINAL_PRED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_all.to_csv(FINAL_PRED_PATH, index=False, encoding="utf-8-sig")
    return df_new


# =========================
# 執行單一彩種
# =========================
def run_final(game: str, save: bool = True) -> tuple[list[list[int]], int | None]:
    if game not in GAME_CONFIG:
        raise ValueError(f"不支援的彩種: {game}")

    maxn = GAME_CONFIG[game]["maxn"]
    pick = GAME_CONFIG[game]["pick"]

    df = load_draws(game)

    base_pred = predict_base(df, maxn, pick)
    best_combos = get_best_combos(df, maxn, pick)
    score_map = fuse_models(base_pred, best_combos)
    final_sets = build_final_sets(score_map, pick, target=4)
    ranked_sets = rank_final_sets(final_sets, score_map, pick)

    special = None
    if game == "power":
        special = predict_power_special(df)

    print(f"\n===== {game} 最終組合 =====")
    for i, s in enumerate(final_sets, 1):
        print(f"[{i}] {' '.join(f'{x:02d}' for x in s)}")

    print(f"\n===== {game} 推薦排序 =====")
    for i, item in enumerate(ranked_sets, 1):
        nums = item["numbers"]
        print(f"推薦{i}: {' '.join(f'{x:02d}' for x in nums)}  score={item['score']:.4f}")

    if special is not None:
        print(f"特別號: {special:02d}")

    if save:
        save_final_predictions(game, final_sets, special)

    return final_sets, special


# =========================
# 主程式
# =========================
def main():
    print("===== 最終選號引擎 =====")

    run_final("539", save=True)
    run_final("649", save=True)
    run_final("power", save=True)

    print(f"\n📁 已儲存: {FINAL_PRED_PATH}")
    print("\n===== 完成 =====")


if __name__ == "__main__":
    main()