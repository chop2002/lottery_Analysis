from __future__ import annotations

from pathlib import Path
from datetime import datetime
import pandas as pd

from src.prediction_writer import append_predictions_csv
from src.draw_schedule import get_target_draw_date, TAIPEI_TZ


BASE_DIR = Path(__file__).resolve().parent
PREDICTION_FILE = BASE_DIR / "data" / "649" / "predictions.csv"


def export_649_predictions(
    predict_date: str,
    batch_id: str,
    model_name: str,
    selected_groups: list[dict],
) -> None:
    predict_dt = datetime.strptime(predict_date, "%Y-%m-%d").replace(tzinfo=TAIPEI_TZ)
    target_draw_date = get_target_draw_date("649", predict_dt=predict_dt)

    rows = []
    for i, item in enumerate(selected_groups, start=1):
        main_nums = sorted(item["main"])
        special_no = item["special_no"]
        score = item.get("score", None)

        if len(main_nums) != 6:
            raise ValueError(f"649 第 {i} 組主號不是 6 碼：{main_nums}")

        rows.append({
            "predict_date": predict_date,
            "target_draw_date": target_draw_date,
            "lottery": "649",
            "batch_id": batch_id,
            "model": model_name,
            "group_id": str(i),
            "rank": i,
            "score": score,
            "n1": main_nums[0],
            "n2": main_nums[1],
            "n3": main_nums[2],
            "n4": main_nums[3],
            "n5": main_nums[4],
            "n6": main_nums[5],
            "special_no": special_no,
        })

    df = pd.DataFrame(rows)

    required_columns = [
        "predict_date", "target_draw_date", "lottery", "batch_id",
        "model", "group_id", "rank", "score",
        "n1", "n2", "n3", "n4", "n5", "n6", "special_no"
    ]

    append_predictions_csv(PREDICTION_FILE, df, required_columns)
    print(f"✅ 已輸出 649 predictions.csv：{PREDICTION_FILE}")


def main() -> None:
    print("===== 649 一鍵執行開始 =====")

    now_dt = datetime.now(TAIPEI_TZ)
    predict_date = now_dt.strftime("%Y-%m-%d")
    batch_id = now_dt.strftime("%Y%m%d") + "_649_v1"
    model_name = "model_649_a"

    selected_groups = [
        {"main": [3, 11, 18, 25, 37, 41], "special_no": 9, "score": 93.2},
        {"main": [5, 12, 20, 28, 33, 45], "special_no": 17, "score": 88.4},
    ]

    export_649_predictions(
        predict_date=predict_date,
        batch_id=batch_id,
        model_name=model_name,
        selected_groups=selected_groups,
    )

    print("🎯 649 主流程完成")


if __name__ == "__main__":
    main()