import streamlit as st
import pandas as pd
import os
import subprocess
import sys  # 👈 這是解決 ModuleNotFoundError 的關鍵
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="吉米彩卷分析預測", page_icon="🎰", layout="wide")

st.title("🎰 吉米彩卷分析系統 (Cloud版)")

# --- 核心執行函式 ---
def run_lotto_process(game_name, scripts, final_csv):
    with st.spinner(f"{game_name} 數據計算中..."):
        # 1. 檢查原始檔案是否存在
        raw_check = f"data/{game_name}/raw/{game_name}_raw.csv"
        if not os.path.exists(raw_check):
            st.error(f"❌ 找不到原始檔：{raw_check}")
            return

        try:
            # 2. 依序執行腳本
            for script in scripts:
                # 💡 重點：使用 sys.executable 確保使用含有 pandas 的環境
                if isinstance(script, list): # 處理帶參數的指令
                    cmd = [sys.executable] + script
                else:
                    cmd = [sys.executable, script]
                
                subprocess.run(cmd, check=True)
            
            # 3. 顯示結果
            if os.path.exists(final_csv):
                df = pd.read_csv(final_csv)
                st.success(f"✅ {game_name} 分析完成！")
                st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)
                st.balloons()
            else:
                st.warning(f"分析已執行，但找不到結果檔：{final_csv}")
        except Exception as e:
            st.error(f"執行過程出錯：{e}")

# --- 分頁介面 ---
tabs = st.tabs(["今彩 539", "大樂透 649", "威力彩"])

with tabs[0]:
    if st.button("🔮 執行 539 分析"):
        run_lotto_process("539", [
            "utils/clean_539.py", 
            "utils/build_539_table1_latest5.py",
            "utils/build_539_table2_lookup.py",
            "utils/build_539_weight_table.py",
            "utils/build_539_table3_predict_hybrid_weighted.py" # 參數先拿掉測試
        ], "data/539/query/539_table3_predict_hybrid_weighted.csv")

with tabs[1]:
    if st.button("🔮 執行大樂透分析"):
        run_lotto_process("649", [
            "utils/clean_649.py",
            "utils/build_649_table1_latest5.py",
            "utils/build_649_table2_lookup.py",
            "utils/build_649_weight_table.py",
            "utils/build_649_table3_predict_hybrid_weighted.py"
        ], "data/649/query/649_table3_predict_hybrid_weighted.csv")

with tabs[2]:
    if st.button("🔮 執行威力彩分析"):
        run_lotto_process("power", [
            "utils/clean_power.py",
            "utils/build_power_table1_latest5.py",
            "utils/build_power_table2_lookup.py",
            "utils/build_power_weight_table.py",
            "utils/build_power_table3_predict_hybrid_weighted.py"
        ], "data/power/query/power_table3_predict_hybrid_weighted.csv")

st.divider()
st.caption("Designed by Gemini吉米 | 僅供學術研究")
