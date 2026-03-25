from __future__ import annotations

from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo


TAIPEI_TZ = ZoneInfo("Asia/Taipei")
CUT_OFF_TIME = time(20, 0)   # 保守用 20:00 截止投注
DRAW_TIME = time(20, 30)     # 開獎約 20:30


# Python weekday: Monday=0 ... Sunday=6
DRAW_WEEKDAYS = {
    "539": {0, 1, 2, 3, 4, 5},   # 週一~週六
    "power": {0, 3},             # 週一、週四
    "649": {1, 4},               # 週二、週五
}


def _normalize_lottery(lottery: str) -> str:
    key = str(lottery).strip().lower()
    aliases = {
        "539": "539",
        "power": "power",
        "威力彩": "power",
        "649": "649",
        "大樂透": "649",
    }
    if key not in aliases:
        raise ValueError(f"不支援的 lottery 類型：{lottery}")
    return aliases[key]


def is_draw_day(lottery: str, d: date) -> bool:
    key = _normalize_lottery(lottery)
    return d.weekday() in DRAW_WEEKDAYS[key]


def next_draw_date_from_date(lottery: str, base_date: date) -> date:
    """
    回傳 strictly next 的開獎日。
    例如：
    - 539 在週四 -> 回傳週五
    - power 在週一 -> 回傳週四
    - 649 在週二 -> 回傳週五
    """
    key = _normalize_lottery(lottery)
    d = base_date + timedelta(days=1)
    while d.weekday() not in DRAW_WEEKDAYS[key]:
        d += timedelta(days=1)
    return d


def get_target_draw_date(
    lottery: str,
    predict_dt: datetime | None = None,
    allow_same_day_before_cutoff: bool = False,
) -> str:
    """
    給主程式用的統一函式。

    預設行為：
    - 產生預測時，一律抓「下一個」開獎日
    - 也就是 strictly next，不會回傳今天

    若 allow_same_day_before_cutoff=True：
    - 今天如果本來就是開獎日，而且現在還沒到 20:00，
      就允許 target_draw_date = 今天
    """
    key = _normalize_lottery(lottery)

    if predict_dt is None:
        predict_dt = datetime.now(TAIPEI_TZ)
    elif predict_dt.tzinfo is None:
        predict_dt = predict_dt.replace(tzinfo=TAIPEI_TZ)
    else:
        predict_dt = predict_dt.astimezone(TAIPEI_TZ)

    today = predict_dt.date()
    now_t = predict_dt.time()

    if allow_same_day_before_cutoff and today.weekday() in DRAW_WEEKDAYS[key] and now_t < CUT_OFF_TIME:
        return today.strftime("%Y-%m-%d")

    return next_draw_date_from_date(key, today).strftime("%Y-%m-%d")


def get_draw_datetime(draw_date_str: str) -> datetime:
    d = datetime.strptime(draw_date_str, "%Y-%m-%d").date()
    return datetime.combine(d, DRAW_TIME, tzinfo=TAIPEI_TZ)