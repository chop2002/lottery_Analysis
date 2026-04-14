from datetime import datetime


def validate_539(rows):
    if not rows:
        raise ValueError("539 驗證失敗：沒有任何資料")

    for row in rows:
        if "draw_date" not in row:
            raise ValueError("539 驗證失敗：缺少 draw_date")

        try:
            datetime.strptime(row["draw_date"], "%Y-%m-%d")
        except Exception:
            raise ValueError(f"539 驗證失敗：日期格式錯誤 {row['draw_date']}")

        nums = [row["n1"], row["n2"], row["n3"], row["n4"], row["n5"]]

        if len(nums) != 5:
            raise ValueError("539 驗證失敗：號碼數量不是 5")

        for n in nums:
            if not (1 <= int(n) <= 39):
                raise ValueError(f"539 驗證失敗：號碼超出範圍 {n}")