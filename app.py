import streamlit as st
import pandas as pd
import os
import subprocess
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="吉米彩卷分析預測", page_icon="🎰", layout="wide")

st.title("🎰 吉米彩卷分析系統 (Cloud版)")

# 定義一個共用的執行函式，增加路徑檢查
def run_lotto_process(game_name, scripts, final_csv):
    with st.spinner(f"{game_name} 數據計算中..."):
        # 檢查原始檔案是否存在
        raw_check = f"data/{game_name}/raw/{game_name}_raw.csv"
        if not os.path.exists(raw_check):
            st.error(f"❌ 找不到原始檔：{raw_check}")
            st.info("請手動上傳原始 CSV 到 GitHub 的對應資料夾。")
            return

        try:
            for script in scripts:
                subprocess.run(["python", script], check=True)
            
            if os.path.exists(final_csv):
                df = pd.read_csv(final_csv)
                st.success(f"✅ {game_name} 分析完成！")
                st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)
                st.balloons()
        except Exception as e:
            st.error(f"執行過程出錯：{e}")

tabs = st.tabs(["今彩 539", "大樂透 649", "威力彩"])

with tabs[0]:
    if st.button("🔮 執行 539 分析"):
        run_lotto_process("539", [
            "utils/clean_539.py", 
            "utils/build_539_table1_latest5.py",
            "utils/build_539_table2_lookup.py",
            "utils/build_539_weight_table.py",
            "utils/build_539_table3_predict_hybrid_weighted.py", "5"
        ], "data/539/query/539_table3_predict_hybrid_weighted.csv")

with tabs[1]:
    if st.button("🔮 執行大樂透分析"):
        run_lotto_process("649", [
            "utils/clean_649.py",
            "utils/build_649_table1_latest5.py",
            "utils/build_649_table2_lookup.py",
            "utils/build_649_weight_table.py",
            "utils/build_649_table3_predict_hybrid_weighted.py", "5"
        ], "data/649/query/649_table3_predict_hybrid_weighted.csv")

with tabs[2]:
    if st.button("🔮 執行威力彩分析"):
        run_lotto_process("power", [
            "utils/clean_power.py",
            "utils/build_power_table1_latest5.py",
            "utils/build_power_table2_lookup.py",
            "utils/build_power_weight_table.py",
            "utils/build_power_table3_predict_hybrid_weighted.py", "5"
        ], "data/power/query/power_table3_predict_hybrid_weighted.csv")
