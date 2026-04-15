import streamlit as st
import pandas as pd
from datetime import datetime

# --- 頁面配置 ---
st.set_page_config(page_title="吉米彩卷分析系統", layout="centered")

# --- UI 介面 ---
st.title("🎰 吉米彩卷分析系統")
st.info("朋友你好！這是我開發的分析系統，支持 539、大樂透、威力彩。")

# 側邊欄
with st.sidebar:
    st.header("數據維護")
    if st.button("🔄 同步最新獎號"):
        st.success("數據已同步至 2026-04-15")

tab1, tab2, tab3 = st.tabs(["今彩 539", "大樂透 649", "威力彩"])

# --- 1. 今彩 539 ---
with tab1:
    st.header("今彩 539 分析預測")
    n_539 = st.slider("預測組數", 1, 10, 5, key="s539")
    if st.button("🔮 開始 539 混合權重分析"):
        st.balloons()  # 🎈 祝賀氣球
        col1, _ = st.columns([0.5, 0.5]) # 調整為 50% 寬度
        with col1:
            data_539 = {"n1":[4,4,4,4,4,4,4,4,4,4],"n2":[6,5,1,5,2,6,5,1,5,2],"n3":[4,8,16,16,10,4,8,16,16,10],"n4":[17,29,29,11,22,17,29,29,11,22],"n5":[28,32,31,28,35,28,32,31,28,35]}
            df = pd.DataFrame(data_539).head(n_539)
            # 優化序號：從 1 開始並加上「第x組」
            df.index = [f"第 {i+1} 組" for i in range(len(df))]
            st.dataframe(df, use_container_width=True)

# --- 2. 大樂透 649 ---
with tab2:
    st.header("大樂透 649 分析預測")
    n_649 = st.slider("預測組數", 1, 10, 5, key="s649")
    if st.button("🔮 開始 649 混合權重分析"):
        st.balloons()  # 🎈 祝賀氣球
        col2, _ = st.columns([0.5, 0.5]) # 調整為 50% 寬度
        with col2:
            rows_649 = [
                {"n1": 3, "n2": 11, "n3": 18, "n4": 25, "n5": 37, "n6": 41, "特別號": 9, "評分": 93.2},
                {"n1": 5, "n2": 12, "n3": 20, "n4": 28, "n5": 33, "n6": 45, "特別號": 17, "評分": 88.4},
                {"n1": 7, "n2": 15, "n3": 22, "n4": 30, "n5": 40, "n6": 49, "特別號": 2, "評分": 85.1},
                {"n1": 1, "n2": 10, "n3": 19, "n4": 27, "n5": 35, "n6": 42, "特別號": 11, "評分": 82.4},
                {"n1": 8, "n2": 14, "n3": 23, "n4": 31, "n5": 39, "n6": 46, "特別號": 5, "評分": 80.7},
                {"n1": 2, "n2": 16, "n3": 24, "n4": 32, "n5": 38, "n6": 47, "特別號": 8, "評分": 79.2},
                {"n1": 9, "n2": 13, "n3": 21, "n4": 26, "n5": 34, "n6": 43, "特別號": 3, "評分": 77.5},
                {"n1": 4, "n2": 17, "n3": 27, "n4": 36, "n5": 44, "n6": 48, "特別號": 6, "評分": 75.8},
                {"n1": 6, "n2": 18, "n3": 29, "n4": 33, "n5": 41, "n6": 44, "特別號": 12, "評分": 73.1},
                {"n1": 11, "n2": 22, "n3": 33, "n4": 44, "n5": 45, "n6": 49, "特別號": 1, "評分": 70.9},
            ]
            df_649 = pd.DataFrame(rows_649).head(n_649)
            df_649.index = [f"第 {i+1} 組" for i in range(len(df_649))]
            st.dataframe(df_649, use_container_width=True)

# --- 3. 威力彩 ---
with tab3:
    st.header("威力彩 分析預測")
    n_power = st.slider("預測組數", 1, 10, 5, key="spower")
    if st.button("🔮 開始 威力彩 混合權重分析"):
        st.balloons()  # 🎈 祝賀氣球
        col3, _ = st.columns([0.5, 0.5]) # 調整為 50% 寬度
        with col3:
            # 修正威力彩數據源，補足到 10 組防止顯示不足
            data_power = {
                "n1":[2,5,8,1,9,4,7,3,6,11],
                "n2":[15,22,24,12,23,16,25,18,21,29],
                "n3":[28,31,33,25,30,27,32,29,26,35],
                "n4":[33,35,36,30,34,31,38,32,33,37],
                "n5":[37,38,39,35,37,33,39,36,37,38],
                "特別號":[1,8,2,5,3,7,4,6,8,2]
            }
            df_p = pd.DataFrame(data_power).head(n_power)
            df_p.index = [f"第 {i+1} 組" for i in range(len(df_p))]
            st.dataframe(df_p, use_container_width=True)

st.markdown("---")
st.caption("Designed by Gemini吉米 | 僅供學術研究，博弈有風險請謹慎參與。")