from __future__ import annotations

from pathlib import Path
from datetime import datetime
import pandas as pd

from src.prediction_writer import append_predictions_csv
from src.draw_schedule import get_target_draw_date, TAIPEI_TZ


BASE_DIR = Path(__file__).resolve().parent
PREDICTION_FILE = BASE_DIR / "data" / "power" / "predictions.csv"


def export_power_predictions(
    predict_date: str,
    batch_id: str,
    model_name: str,
    selected_groups: list[dict],
) -> None:
    """
    selected_groups 格式範例：
    [
        {"zone1": [3, 8, 14, 21, 29, 35], "special_no": 7, "score": 95.3},
        {"zone1": [5, 11, 17, 24, 31, 38], "special_no": 2, "score": 89.8},
    ]
    """
    predict_dt = datetime.strptime(predict_date, "%Y-%m-%d").replace(tzinfo=TAIPEI_TZ)
    target_draw_date = get_target_draw_date("power", predict_dt=predict_dt)

    rows = []
    for i, item in enumerate(selected_groups, start=1):
        zone1 = sorted(item["zone1"])
        special_no = item["special_no"]
        score = item.get("score", None)

        if len(zone1) != 6:
            raise ValueError(f"威力彩第 {i} 組第一區不是 6 碼：{zone1}")

        rows.append({
            "predict_date": predict_date,
            "target_draw_date": target_draw_date,
            "lottery": "power",
            "batch_id": batch_id,
            "model": model_name,
            "group_id": str(i),
            "rank": i,
            "score": score,
            "p1": zone1[0],
            "p2": zone1[1],
            "p3": zone1[2],
            "p4": zone1[3],
            "p5": zone1[4],
            "p6": zone1[5],
            "special_no": special_no,
        })

    df = pd.DataFrame(rows)

    required_columns = [
        "predict_date", "target_draw_date", "lottery", "batch_id",
        "model", "group_id", "rank", "score",
        "p1", "p2", "p3", "p4", "p5", "p6", "special_no"
    ]

    append_predictions_csv(PREDICTION_FILE, df, required_columns)
    print(f"✅ 已輸出 威力彩 predictions.csv：{PREDICTION_FILE}")


def main() -> None:
    print("===== 威力彩 一鍵執行開始 =====")

    now_dt = datetime.now(TAIPEI_TZ)
    predict_date = now_dt.strftime("%Y-%m-%d")
    batch_id = now_dt.strftime("%Y%m%d") + "_power_v1"
    model_name = "power_hybrid_v1"

    # 先用測試資料；之後再換成你真正分析後的結果
    selected_groups = [
        {"zone1": [3, 8, 14, 21, 29, 35], "special_no": 7, "score": 95.3},
        {"zone1": [5, 11, 17, 24, 31, 38], "special_no": 2, "score": 89.8},
    ]

    export_power_predictions(
        predict_date=predict_date,
        batch_id=batch_id,
        model_name=model_name,
        selected_groups=selected_groups,
    )

    print("🎯 威力彩主流程完成")


if __name__ == "__main__":
    main()