from __future__ import annotations
from pathlib import Path
import pandas as pd
from prediction_writer import append_predictions_csv


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "539" / "predictions.csv"


def main() -> None:
    predict_date = "2026-03-20"
    target_draw_date = "2026-03-21"
    batch_id = "20260320_539_night_v1"

    rows = [
        {
            "predict_date": predict_date,
            "target_draw_date": target_draw_date,
            "lottery": "539",
            "batch_id": batch_id,
            "model": "hybrid_v1",
            "group_id": "1",
            "rank": 1,
            "score": 92.5,
            "n1": 2, "n2": 11, "n3": 18, "n4": 24, "n5": 35,
        },
        {
            "predict_date": predict_date,
            "target_draw_date": target_draw_date,
            "lottery": "539",
            "batch_id": batch_id,
            "model": "hybrid_v1",
            "group_id": "2",
            "rank": 2,
            "score": 88.7,
            "n1": 5, "n2": 12, "n3": 19, "n4": 21, "n5": 33,
        },
        {
            "predict_date": predict_date,
            "target_draw_date": target_draw_date,
            "lottery": "539",
            "batch_id": batch_id,
            "model": "tail_balance_v2",
            "group_id": "1",
            "rank": 1,
            "score": 90.1,
            "n1": 3, "n2": 8, "n3": 14, "n4": 22, "n5": 31,
        },
    ]

    df = pd.DataFrame(rows)

    required_columns = [
        "predict_date", "target_draw_date", "lottery", "batch_id",
        "model", "group_id", "rank", "score",
        "n1", "n2", "n3", "n4", "n5"
    ]

    append_predictions_csv(OUTPUT_FILE, df, required_columns)
    print(f"✅ 539 預測已輸出：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()