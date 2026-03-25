import streamlit as st
import pandas as pd
import os
import subprocess
from io import BytesIO
from datetime import datetime

# 設定網頁標題與圖示
st.set_page_config(page_title="吉米彩卷分析預測", page_icon="🎰", layout="wide")

# 自定義 CSS 讓介面更漂亮
st.markdown("""
    <style>
    .main {
        background-color: #1a1a1a;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎰 吉米彩卷分析系統 (Cloud版)")
st.info("朋友你好！這是我開發的分析系統，支持 539、大樂透、威力彩。")

# --- 側邊欄：數據同步 ---
with st.sidebar:
    st.header("⚙️ 數據維護")
    if st.button("🔄 同步最新獎號 (爬蟲)"):
        with st.spinner("正在執行數據同步..."):
            try:
                # 這裡調用你原本的 update 腳本
                subprocess.run(["python", "utils/update_539.py"], check=True)
                st.success("數據更新成功！")
            except Exception as e:
                st.error(f"更新失敗: {e}")

# --- 主畫面：分頁標籤 ---
tabs = st.tabs(["今彩 539", "大樂透 649", "威力彩"])

# ==========================================
# 1. 今彩 539 邏輯
# ==========================================
with tabs[0]:
    st.subheader("今彩 539 分析預測")
    test_time_539 = st.slider("預測組數", 1, 20, 5, key="539_slider")
    
    if st.button("🔮 執行 539 全流程分析", key="btn_539"):
        with st.spinner("539 數據計算中..."):
            try:
                # 依序執行你的流水線
                subprocess.run(["python", "utils/clean_539.py"], check=True)
                subprocess.run(["python", "utils/build_539_table1_latest5.py"], check=True)
                subprocess.run(["python", "utils/build_539_table2_lookup.py"], check=True)
                subprocess.run(["python", "utils/build_539_weight_table.py"], check=True)
                subprocess.run(["python", "utils/build_539_table3_predict_hybrid_weighted.py", str(test_time_539)], check=True)
                
                res_path = "data/539/query/539_table3_predict_hybrid_weighted.csv"
                if os.path.exists(res_path):
                    df_res = pd.read_csv(res_path)
                    st.success("✅ 539 分析完成！")
                    st.write("### 🎯 推薦號碼")
                    st.dataframe(df_res.style.highlight_max(axis=0), use_container_width=True)
                    st.balloons()
            except Exception as e:
                st.error(f"執行出錯：{e}")

# ==========================================
# 2. 大樂透 649 邏輯
# ==========================================
with tabs[1]:
    st.subheader("大樂透 649 分析預測")
    test_time_649 = st.slider("預測組數", 1, 20, 5, key="649_slider")
    
    if st.button("🔮 執行大樂透全流程分析", key="btn_649"):
        with st.spinner("大樂透數據計算中..."):
            try:
                subprocess.run(["python", "utils/clean_649.py"], check=True)
                subprocess.run(["python", "utils/build_649_table1_latest5.py"], check=True)
                subprocess.run(["python", "utils/build_649_table2_lookup.py"], check=True)
                subprocess.run(["python", "utils/build_649_weight_table.py"], check=True)
                subprocess.run(["python", "utils/build_649_table3_predict_hybrid_weighted.py", str(test_time_649)], check=True)
                
                res_path = "data/649/query/649_table3_predict_hybrid_weighted.csv"
                if os.path.exists(res_path):
                    df_res = pd.read_csv(res_path)
                    st.success("✅ 大樂透分析完成！")
                    st.write("### 🎯 推薦號碼")
                    st.dataframe(df_res.style.highlight_max(axis=0), use_container_width=True)
                    st.balloons()
            except Exception as e:
                st.error(f"執行出錯：{e}")

# ==========================================
# 3. 威力彩 Power 邏輯
# ==========================================
with tabs[2]:
    st.subheader("威力彩分析預測")
    test_time_power = st.slider("預測組數", 1, 20, 5, key="power_slider")
    
    if st.button("🔮 執行威力彩全流程分析", key="btn_power"):
        with st.spinner("威力彩數據計算中..."):
            try:
                subprocess.run(["python", "utils/clean_power.py"], check=True)
                subprocess.run(["python", "utils/build_power_table1_latest5.py"], check=True)
                subprocess.run(["python", "utils/build_power_table2_lookup.py"], check=True)
                subprocess.run(["python", "utils/build_power_weight_table.py"], check=True)
                subprocess.run(["python", "utils/build_power_table3_predict_hybrid_weighted.py", str(test_time_power)], check=True)
                
                res_path = "data/power/query/power_table3_predict_hybrid_weighted.csv"
                if os.path.exists(res_path):
                    df_res = pd.read_csv(res_path)
                    st.success("✅ 威力彩分析完成！")
                    st.write("### 🎯 推薦號碼")
                    st.dataframe(df_res.style.highlight_max(axis=0), use_container_width=True)
                    st.balloons()
                except subprocess.CalledProcessError as e:
                    st.error(f"執行出錯！這通常是因為缺少原始資料檔。")
                    st.info("請檢查 GitHub 是否有 data/649/raw/649_raw.csv")
# --- 頁尾 ---
st.divider()
st.caption("Designed by Gemini吉米 | 僅供學術研究，博弈有風險請謹慎參與。")
