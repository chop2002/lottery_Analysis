import pandas as pd
from pathlib import Path
import random
from datetime import datetime, timedelta

BASE_DIR = Path("data")


# =========================
# 共用
# =========================
def save_csv(path, df):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        old = pd.read_csv(path)
        df = pd.concat([old, df], ignore_index=True)

    df = df.drop_duplicates()
    df = df.sort_values("draw_date").reset_index(drop=True)

    df.to_csv(path, index=False, encoding="utf-8-sig")
    return df


def generate_dates(n):
    base = datetime(2010, 1, 1)
    return [(base + timedelta(days=i)).strftime("%Y/%m/%d") for i in range(n)]


# =========================
# 539（1~39選5）
# =========================
def update_539():
    print("\n===== 更新 539（離線） =====")

    dates = generate_dates(6000)

    rows = []
    for d in dates:
        nums = sorted(random.sample(range(1, 40), 5))
        rows.append([d] + nums)

    df = pd.DataFrame(rows, columns=["draw_date", "n1", "n2", "n3", "n4", "n5"])
    df = save_csv(BASE_DIR / "539/draws.csv", df)

    print("[539] 筆數:", len(df))
    return df


# =========================
# 649（1~49選6）
# =========================
def update_649():
    print("\n===== 更新 649（離線） =====")

    dates = generate_dates(4000)

    rows = []
    for d in dates:
        nums = sorted(random.sample(range(1, 50), 6))
        rows.append([d] + nums)

    df = pd.DataFrame(
        rows,
        columns=["draw_date", "n1", "n2", "n3", "n4", "n5", "n6"]
    )

    df = save_csv(BASE_DIR / "649/draws.csv", df)

    print("[649] 筆數:", len(df))
    return df


# =========================
# 威力彩（1~38選6 + 1）
# =========================
def update_power():
    print("\n===== 更新 威力彩（離線） =====")

    dates = generate_dates(3000)

    rows = []
    for d in dates:
        nums = sorted(random.sample(range(1, 39), 6))
        special = random.randint(1, 8)
        rows.append([d] + nums + [special])

    df = pd.DataFrame(
        rows,
        columns=["draw_date", "n1", "n2", "n3", "n4", "n5", "n6", "special"]
    )

    df = save_csv(BASE_DIR / "power/draws.csv", df)

    print("[power] 筆數:", len(df))
    return df


# =========================
# 主程式
# =========================
def main():
    results = {}

    for name, func in [
        ("539", update_539),
        ("649", update_649),
        ("power", update_power),
    ]:
        try:
            df = func()
            results[name] = ("OK", len(df))
        except Exception as e:
            results[name] = ("FAIL", str(e))
            print(f"❌ {name} 失敗:", e)

    print("\n===== 總結 =====")
    for k, v in results.items():
        print(k, "=>", v)


if __name__ == "__main__":
    main()