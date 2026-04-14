from configs.game_539 import CONFIG
from engines.hybrid_table_engine import build_hybrid_table


if __name__ == "__main__":
    build_hybrid_table(
        table2_path=CONFIG["table2_path"],
        weight_table_path=CONFIG["weight_table_path"],
        output_path=CONFIG["hybrid_table_path"],
        fields=CONFIG["fields"],
    )