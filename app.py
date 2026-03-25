import streamlit as st
import pandas as pd
import os
import subprocess
import sys
from datetime import datetime

st.set_page_config(page_title="吉米彩卷分析預測", page_icon="🎰", layout="wide")

st.title("🎰 吉米彩卷分析系統 (Cloud版)")

# --- 核心執行函式 (自動處理參數與環境) ---
def run_lotto_process(game_name, scripts, final_csv, test_time=None):
    with st.spinner(f"{game_name} 數據計算中..."):
        try:
            for script in scripts:
                # 建立指令清單
                cmd = [sys.executable, script]
                # 如果是預測腳本，傳入組數參數
                if "predict" in script and test_time is not None:
                    cmd.append(str(test_time))
                
                # 執行並捕獲錯誤
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    st.error(f"執行 {script} 失敗！")
                    st.code(result.stderr) # 顯示後台報錯，方便除錯
                    return

            if os.path.exists(final_csv):
                df = pd.read_csv(final_csv)
                st.success(f"✅ {game_name} 分析完成！")
                st.write("### 🎯 推薦號碼")
                st.dataframe(df, use_container_width=True)
                st.balloons()
            else:
                st.warning(f"分析已結束，但找不到結果檔：{final_csv}")
        except Exception as e:
            st.error(f"系統崩潰：{e}")

tabs = st.tabs(["今彩 539", "大樂透 649", "威力彩"])

# --- 今彩 539 ---
with tabs[0]:
    t539 = st.slider("預測組數", 1, 20, 5, key="s539")
    if st.button("🔮 執行 539 分析", key="b539"):
        run_lotto_process("539", [
            "utils/clean_539.py", 
            "utils/build_539_table1_latest5.py",
            "utils/build_539_table2_lookup.py",
            "utils/build_539_weight_table.py",
            "utils/build_539_table3_predict_hybrid_weighted.py"
        ], "data/539/query/539_table3_predict_hybrid_weighted.csv", test_time=t539)

# --- 大樂透 649 ---
with tabs[1]:
    t649 = st.slider("預測組數", 1, 20, 5, key="s649")
    if st.button("🔮 執行大樂透分析", key="b649"):
        run_lotto_process("649", [
            "utils/clean_649.py",
            "utils/build_649_table1_latest5.py",
            "utils/build_649_table2_lookup.py",
            "utils/build_649_weight_table.py",
            "utils/build_649_table3_predict_hybrid_weighted.py"
        ], "data/649/query/649_table3_predict_hybrid_weighted.csv", test_time=t649)

# --- 威力彩 ---
with tabs[2]:
    tpow = st.slider("預測組數", 1, 20, 5, key="spow")
    if st.button("🔮 執行威力彩分析", key="bpow"):
        run_lotto_process("power", [
            "utils/clean_power.py",
            "utils/build_power_table1_latest5.py",
            "utils/build_power_table2_lookup.py",
            "utils/build_power_weight_table.py",
            "utils/build_power_table3_predict_hybrid_weighted.py"
        ], "data/power/query/power_table3_predict_hybrid_weighted.csv", test_time=tpow)
