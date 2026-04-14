# src/generate_best_combinations.py
from __future__ import annotations

import argparse
import itertools
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


GAME_CONFIG = {
    "539": {
        "numbers": 39,
        "pick": 5,
        "aliases": ["539", "今彩539", "dailycash", "daily_cash"],
    },
    "649": {
        "numbers": 49,
        "pick": 6,
        "aliases": ["649", "大樂透", "lotto649", "lotto_649", "superlotto", "super_lotto"],
    },
    "power": {
        "numbers": 38,
        "pick": 6,
        "aliases": ["power", "威力彩"],
    },
}


@dataclass
class BacktestResult:
    total_tests: int
    avg_hits: float
    hit_distribution: Dict[int, int]
    best_case: int


def detect_game_column(df: pd.DataFrame) -> str | None:
    for c in ["game", "lottery", "type", "kind", "彩種", "遊戲名稱"]:
        if c in df.columns:
            return c
    return None


def detect_date_column(df: pd.DataFrame) -> str:
    for c in ["draw_date", "date", "開獎日期", "开奖日期"]:
        if c in df.columns:
            return c
    raise ValueError(f"找不到日期欄位，現有欄位: {list(df.columns)}")


def detect_number_columns(df: pd.DataFrame) -> List[str]:
    cols = []

    for c in df.columns:
        cl = str(c).lower()
        if cl in {
            "n1", "n2", "n3", "n4", "n5", "n6", "n7",
            "num1", "num2", "num3", "num4", "num5", "num6", "num7"
        }:
            cols.append(c)

    if not cols:
        for c in df.columns:
            s = str(c)
            if "獎號" in s or "號碼" in s or "号码" in s:
                cols.append(c)

    if not cols:
        raise ValueError(f"找不到號碼欄位，現有欄位: {list(df.columns)}")

    def key(x: str) -> int:
        digits = "".join(filter(str.isdigit, str(x)))
        return int(digits) if digits else 999

    return sorted(cols, key=key)


def normalize_game_name(name: str) -> str:
    s = str(name).strip().lower()
    for k, v in GAME_CONFIG.items():
        if s == k or s in [a.lower() for a in v["aliases"]]:
            return k
    return s


def load_draws(path: Path, fallback_game: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案: {path}")

    df = pd.read_csv(path, encoding="utf-8-sig")

    date_col = detect_date_column(df)
    num_cols = detect_number_columns(df)
    game_col = detect_game_column(df)

    df = df.copy()

    if game_col:
        df["_game"] = df[game_col].astype(str).map(normalize_game_name)
    else:
        df["_game"] = normalize_game_name(fallback_game)

    df["_date"] = pd.to_datetime(df[date_col], errors="coerce")

    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["_date"]).sort_values("_date").reset_index(drop=True)
    df.attrs["num_cols"] = num_cols
    return df


def get_game_draws(df: pd.DataFrame, game: str) -> pd.DataFrame:
    game = normalize_game_name(game)
    out = df[df["_game"] == game].copy()
    if out.empty:
        raise ValueError(f"資料裡找不到彩種: {game}")
    out.attrs["num_cols"] = df.attrs["num_cols"]
    return out


def row_to_numbers(row: pd.Series, cols: List[str], pick: int, maxn: int) -> List[int]:
    nums = []
    for c in cols:
        if pd.notna(row[c]):
            n = int(row[c])
            if 1 <= n <= maxn:
                nums.append(n)
    nums = sorted(set(nums))
    return nums[:pick]


def draws_to_list(df: pd.DataFrame, pick: int, maxn: int) -> List[List[int]]:
    cols = df.attrs["num_cols"]
    out = []
    for _, r in df.iterrows():
        nums = row_to_numbers(r, cols, pick, maxn)
        if len(nums) == pick:
            out.append(nums)
    return out


def minmax(s: pd.Series) -> pd.Series:
    mn = s.min()
    mx = s.max()
    if math.isclose(mn, mx):
        return pd.Series([0.5] * len(s), index=s.index)
    return (s - mn) / (mx - mn)


def compute_features(draws: List[List[int]], maxn: int) -> pd.DataFrame:
    nums = list(range(1, maxn + 1))
    total_draws = len(draws)

    freq15 = {n: 0 for n in nums}
    freq30 = {n: 0 for n in nums}
    freq100 = {n: 0 for n in nums}
    freq_all = {n: 0 for n in nums}
    gap = {n: total_draws for n in nums}

    recent15 = draws[-15:] if len(draws) >= 15 else draws
    recent30 = draws[-30:] if len(draws) >= 30 else draws
    recent100 = draws[-100:] if len(draws) >= 100 else draws

    for d in draws:
        for n in d:
            freq_all[n] += 1

    for d in recent15:
        for n in d:
            freq15[n] += 1

    for d in recent30:
        for n in d:
            freq30[n] += 1

    for d in recent100:
        for n in d:
            freq100[n] += 1

    for n in nums:
        for i in range(len(draws) - 1, -1, -1):
            if n in draws[i]:
                gap[n] = len(draws) - 1 - i
                break

    rows = []
    for n in nums:
        momentum = (
            freq15[n] / max(1, len(recent15))
            - freq100[n] / max(1, len(recent100))
        )
        rows.append({
            "number": n,
            "freq_15": freq15[n],
            "freq_30": freq30[n],
            "freq_100": freq100[n],
            "freq_all": freq_all[n],
            "gap": gap[n],
            "momentum": momentum,
        })

    feat = pd.DataFrame(rows)
    feat["freq15_s"] = minmax(feat["freq_15"])
    feat["freq30_s"] = minmax(feat["freq_30"])
    feat["freq100_s"] = minmax(feat["freq_100"])
    feat["gap_s"] = minmax(feat["gap"])
    feat["momentum_s"] = minmax(feat["momentum"])

    feat["single_score"] = (
        feat["freq30_s"] * 0.38
        + feat["freq100_s"] * 0.27
        + feat["gap_s"] * 0.20
        + feat["momentum_s"] * 0.15
    )

    feat = feat.sort_values(
        ["single_score", "freq_30", "freq_100", "gap"],
        ascending=False
    ).reset_index(drop=True)

    return feat


def pair_scores(draws: List[List[int]]) -> Dict[Tuple[int, int], float]:
    d: Dict[Tuple[int, int], int] = {}

    recent = draws[-150:] if len(draws) >= 150 else draws
    for draw in recent:
        for a, b in itertools.combinations(sorted(draw), 2):
            k = (a, b)
            d[k] = d.get(k, 0) + 1

    m = max(d.values()) if d else 1
    return {k: v / m for k, v in d.items()}


def odd_even_bonus(combo: Tuple[int, ...]) -> float:
    odd = sum(1 for n in combo if n % 2 == 1)
    even = len(combo) - odd
    diff = abs(odd - even)

    if diff == 0:
        return 1.0
    if diff == 1:
        return 0.7
    if diff == 2:
        return 0.35
    return 0.0


def zone_bonus(combo: Tuple[int, ...], maxn: int) -> float:
    zone_count = 4 if maxn <= 39 else 5
    zone_size = math.ceil(maxn / zone_count)
    zones = set((n - 1) // zone_size for n in combo)
    used = len(zones)
    if used >= zone_count:
        return 1.0
    return used / zone_count


def tail_bonus(combo: Tuple[int, ...]) -> float:
    tail_unique = len(set(n % 10 for n in combo)) / len(combo)
    return tail_unique


def consecutive_penalty(combo: Tuple[int, ...]) -> float:
    combo = sorted(combo)
    run = 0
    for i in range(1, len(combo)):
        if combo[i] == combo[i - 1] + 1:
            run += 1

    if run == 0:
        return 0.0
    if run == 1:
        return 0.08
    if run == 2:
        return 0.18
    return 0.30


def duplicate_penalty(combo: Tuple[int, ...], history: set[Tuple[int, ...]]) -> float:
    return 1.0 if tuple(sorted(combo)) in history else 0.0


def combo_pair_score(combo: Tuple[int, ...], pair_map: Dict[Tuple[int, int], float]) -> float:
    vals = []
    for a, b in itertools.combinations(sorted(combo), 2):
        vals.append(pair_map.get((a, b), 0.0))
    if not vals:
        return 0.0
    return sum(vals) / len(vals)


def score_combo(
    combo: Tuple[int, ...],
    score_map: Dict[int, float],
    pair_map: Dict[Tuple[int, int], float],
    history: set[Tuple[int, ...]],
    maxn: int,
) -> float:
    s = sum(score_map[n] for n in combo) / len(combo)
    pair = combo_pair_score(combo, pair_map)
    oe = odd_even_bonus(combo)
    zone = zone_bonus(combo, maxn)
    tails = tail_bonus(combo)
    cons_pen = consecutive_penalty(combo)
    dup_pen = duplicate_penalty(combo, history)

    score = (
        s * 0.55
        + pair * 0.15
        + oe * 0.10
        + zone * 0.10
        + tails * 0.05
        - cons_pen * 0.05
        - dup_pen * 0.40
    )
    return round(score, 6)


def build_candidate_pool(features: pd.DataFrame, pick: int, maxn: int) -> List[int]:
    top_k = 18 if maxn > 39 else 15

    top_numbers = features["number"].head(top_k).tolist()
    cold_bonus = features.sort_values("gap", ascending=False)["number"].head(5).tolist()

    pool = []
    for n in top_numbers + cold_bonus:
        if n not in pool:
            pool.append(n)

    need = max(pick + 4, min(len(features), top_k + 3))
    if len(pool) < need:
        for n in features["number"].tolist():
            if n not in pool:
                pool.append(n)
            if len(pool) >= need:
                break

    return sorted(pool)


def generate_best_combinations(
    draws: List[List[int]],
    maxn: int,
    pick: int,
    topn: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if len(draws) < 30:
        raise ValueError("歷史資料太少，至少需要 30 期以上")

    feat = compute_features(draws, maxn)
    score_map = dict(zip(feat["number"], feat["single_score"]))
    pair_map = pair_scores(draws)
    history = {tuple(sorted(d)) for d in draws}

    pool = build_candidate_pool(feat, pick, maxn)

    rows = []
    for combo in itertools.combinations(pool, pick):
        sc = score_combo(combo, score_map, pair_map, history, maxn)
        rows.append({
            "numbers": " ".join(f"{x:02d}" for x in combo),
            "score": sc,
            "odd_count": sum(1 for x in combo if x % 2 == 1),
            "even_count": sum(1 for x in combo if x % 2 == 0),
            "zone_score": round(zone_bonus(combo, maxn), 4),
            "pair_score": round(combo_pair_score(combo, pair_map), 4),
            "tail_score": round(tail_bonus(combo), 4),
            "consecutive_penalty": round(consecutive_penalty(combo), 4),
            "is_historical_duplicate": int(tuple(sorted(combo)) in history),
        })

    combo_df = pd.DataFrame(rows).sort_values(
        ["score", "pair_score", "zone_score", "tail_score"],
        ascending=False
    ).reset_index(drop=True)

    selected = []
    selected_sets = []
    used: Dict[int, int] = {}

    for _, row in combo_df.iterrows():
        combo = tuple(int(x) for x in row["numbers"].split())
        combo_set = set(combo)

        if any(used.get(n, 0) >= 3 for n in combo):
            continue

        too_similar = False
        for prev in selected_sets:
            if len(combo_set & prev) >= pick - 1:
                too_similar = True
                break

        if too_similar:
            continue

        selected.append(row)
        selected_sets.append(combo_set)
        for n in combo:
            used[n] = used.get(n, 0) + 1

        if len(selected) >= topn:
            break

    best_df = pd.DataFrame(selected).reset_index(drop=True)
    if not best_df.empty:
        best_df.insert(0, "rank", range(1, len(best_df) + 1))

    return best_df, feat


def backtest_best_combo_strategy(
    draws: List[List[int]],
    maxn: int,
    pick: int,
    lookback: int = 120,
    test_periods: int = 30,
) -> BacktestResult:
    if len(draws) < lookback + test_periods + 5:
        test_periods = max(5, len(draws) - lookback - 5)

    hit_dist: Dict[int, int] = {}
    total_hits = 0
    tests = 0
    best_case = 0

    start_index = max(lookback, len(draws) - test_periods)

    for i in range(start_index, len(draws)):
        history = draws[:i]
        if len(history) < lookback:
            continue

        try:
            best_df, _ = generate_best_combinations(
                draws=history,
                maxn=maxn,
                pick=pick,
                topn=1,
            )
        except Exception:
            continue

        if best_df.empty:
            continue

        pred = [int(x) for x in best_df.iloc[0]["numbers"].split()]
        actual = set(draws[i])
        hits = len(set(pred) & actual)

        hit_dist[hits] = hit_dist.get(hits, 0) + 1
        total_hits += hits
        best_case = max(best_case, hits)
        tests += 1

    avg_hits = total_hits / tests if tests else 0.0

    return BacktestResult(
        total_tests=tests,
        avg_hits=round(avg_hits, 4),
        hit_distribution=dict(sorted(hit_dist.items())),
        best_case=best_case,
    )


def save_results(
    out_path: Path,
    game: str,
    best_df: pd.DataFrame,
    features_df: pd.DataFrame,
    backtest: BacktestResult,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    summary_rows = [
        ["game", game],
        ["total_tests", backtest.total_tests],
        ["avg_hits", backtest.avg_hits],
        ["best_case", backtest.best_case],
        ["hit_distribution", str(backtest.hit_distribution)],
    ]
    summary_df = pd.DataFrame(summary_rows, columns=["item", "value"])

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="summary", index=False)
        best_df.to_excel(writer, sheet_name="best_combinations", index=False)
        features_df.to_excel(writer, sheet_name="number_features", index=False)


def run(game: str, csv: str, top: int, output: str | None) -> None:
    game = normalize_game_name(game)
    if game not in GAME_CONFIG:
        raise ValueError(f"不支援的彩種: {game}")

    p = Path(csv)
    if not p.exists():
        alt = Path(f"data/{game}/draws.csv")
        if alt.exists():
            print(f"⚠️ 自動改用: {alt}")
            p = alt
        else:
            raise FileNotFoundError(f"找不到檔案: {csv}")

    cfg = GAME_CONFIG[game]

    df = load_draws(p, game)
    df = get_game_draws(df, game)

    draws = draws_to_list(df, cfg["pick"], cfg["numbers"])

    best_df, features_df = generate_best_combinations(
        draws=draws,
        maxn=cfg["numbers"],
        pick=cfg["pick"],
        topn=top,
    )

    backtest = backtest_best_combo_strategy(
        draws=draws,
        maxn=cfg["numbers"],
        pick=cfg["pick"],
        lookback=120,
        test_periods=30,
    )

    print(f"\n===== {game} 最強組合 =====")
    for _, row in best_df.iterrows():
        print(f"[{int(row['rank'])}] {row['numbers']}  score={row['score']:.4f}")

    print("\n===== 回測摘要 =====")
    print(f"測試期數: {backtest.total_tests}")
    print(f"平均命中: {backtest.avg_hits}")
    print(f"最佳命中: {backtest.best_case}")
    print(f"命中分佈: {backtest.hit_distribution}")

    if output:
        save_results(Path(output), game, best_df, features_df, backtest)
        print(f"\n📊 已輸出: {output}")


def main() -> None:
    p = argparse.ArgumentParser(description="產生最強彩票組合")
    p.add_argument("--game", required=True, help="539 / 649 / power")
    p.add_argument("--csv", default="data/draws.csv", help="draws.csv 路徑")
    p.add_argument("--top", type=int, default=8, help="輸出幾組")
    p.add_argument("--output", default=None, help="輸出 xlsx 路徑")
    args = p.parse_args()

    run(args.game, args.csv, args.top, args.output)


if __name__ == "__main__":
    main()