import sys
from configs.game_649 import CONFIG
from engines.weighted_predict_engine import build_weighted_predict


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("請傳入 test_time")
    test_time = int(sys.argv[1])

    build_weighted_predict(
        hybrid_table_path=CONFIG["hybrid_table_path"],
        output_path=CONFIG["predict_output_path"],
        test_time=test_time,
        main_fields=CONFIG["main_fields"],
        sp_field=CONFIG["sp_field"],
        weight_common=0.6,
        weight_weight_only=0.3,
        weight_freq_only=0.1,
    )