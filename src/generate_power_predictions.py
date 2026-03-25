from __future__ import annotations
from pathlib import Path
import pandas as pd
from prediction_writer import append_predictions_csv


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "power" / "predictions.csv"


def main() -> None:
    predict_date = "2026-03-20"
    target_draw_date = "2026-03-23"
    batch_id = "20260320_power_v1"

    rows = [
        {
            "predict_date": predict_date,
            "target_draw_date": target_draw_date,
            "lottery": "power",
            "batch_id": batch_id,
            "model": "power_hybrid_v1",
            "group_id": "1",
            "rank": 1,
            "score": 95.3,
            "p1": 3, "p2": 8, "p3": 14, "p4": 21, "p5": 29, "p6": 35,
            "special_no": 7,
        },
        {
            "predict_date": predict_date,
            "target_draw_date": target_draw_date,
            "lottery": "power",
            "batch_id": batch_id,
            "model": "power_hybrid_v1",
            "group_id": "2",
            "rank": 2,
            "score": 89.8,
            "p1": 5, "p2": 11, "p3": 17, "p4": 24, "p5": 31, "p6": 38,
            "special_no": 2,
        },
    ]

    df = pd.DataFrame(rows)

    required_columns = [
        "predict_date", "target_draw_date", "lottery", "batch_id",
        "model", "group_id", "rank", "score",
        "p1", "p2", "p3", "p4", "p5", "p6", "special_no"
    ]

    append_predictions_csv(OUTPUT_FILE, df, required_columns)
    print(f"✅ 威力彩預測已輸出：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()