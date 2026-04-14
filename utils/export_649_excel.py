import pandas as pd
import os
from datetime import datetime

TABLE1 = "data/649/query/649_table1_latest5.csv"
TABLE2 = "data/649/query/649_table2_lookup.csv"
WEIGHT_TABLE = "data/649/query/649_weight_table.csv"
TABLE3 = "data/649/query/649_table3_predict.csv"
HYBRID_TABLE = "data/649/query/649_table4_hybrid.csv"
HYBRID_WEIGHTED_PREDICT = "data/649/query/649_table3_predict_hybrid_weighted.csv"

OUTPUT_DIR = "data/649/output"


def export_649_excel():
    df1 = pd.read_csv(TABLE1, encoding="utf-8-sig")
    df2 = pd.read_csv(TABLE2, encoding="utf-8-sig")
    dfw = pd.read_csv(WEIGHT_TABLE, encoding="utf-8-sig")
    df3 = pd.read_csv(TABLE3, encoding="utf-8-sig")
    dfh = pd.read_csv(HYBRID_TABLE, encoding="utf-8-sig")
    dfhw = pd.read_csv(HYBRID_WEIGHTED_PREDICT, encoding="utf-8-sig")

    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"649_report_{now_str}.xlsx"
    output_path = os.path.join(OUTPUT_DIR, filename)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        sheet_name = "report"

        start1 = 0
        df1.to_excel(writer, sheet_name=sheet_name, startrow=start1 + 1, index=False)

        start2 = start1 + len(df1) + 4
        df2.to_excel(writer, sheet_name=sheet_name, startrow=start2 + 1, index=False)

        startw = start2 + len(df2) + 4
        dfw.to_excel(writer, sheet_name=sheet_name, startrow=startw + 1, index=False)

        start3 = startw + len(dfw) + 4
        df3.to_excel(writer, sheet_name=sheet_name, startrow=start3 + 1, index=False)

        starth = start3 + len(df3) + 4
        dfh.to_excel(writer, sheet_name=sheet_name, startrow=starth + 1, index=False)

        starthw = starth + len(dfh) + 4
        dfhw.to_excel(writer, sheet_name=sheet_name, startrow=starthw + 1, index=False)

        ws = writer.book[sheet_name]
        ws.cell(row=start1 + 1, column=1, value="Table1")
        ws.cell(row=start2 + 1, column=1, value="Table2")
        ws.cell(row=startw + 1, column=1, value="WEIGHT_TABLE")
        ws.cell(row=start3 + 1, column=1, value="Table3")
        ws.cell(row=starth + 1, column=1, value="HYBRID_TABLE")
        ws.cell(row=starthw + 1, column=1, value="HYBRID_WEIGHTED_PREDICT")

    print("✅ 大樂透 Excel 輸出完成")
    print(f"檔案：{os.path.abspath(output_path)}")


if __name__ == "__main__":
    export_649_excel()