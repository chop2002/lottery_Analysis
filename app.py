import streamlit as st
import pandas as pd

# ----------------------------------------------------------------
# 1. 導入你的邏輯檔案 (請確保檔名正確)
# ----------------------------------------------------------------
try:
    from main_649 import get_649_results  # 假設你的函數叫這個，請視情況修改
    from main_power import get_power_results
    # 如果 539 也是獨立檔案，請也導入：
    # from main_539 import get_539_results
except ImportError:
    st.warning("部分邏輯檔案導入失敗，請檢查 main_649.py 與 main_power.py 是否在同目錄。")

# --- 頁面配置 ---
st.set_page_config(page_title="吉米彩卷分析系統", layout="centered")

# --- 標題與簡介 ---
st.title("🎰 吉米彩卷分析系統")
st.info("朋友你好！這是我開發的分析系統，支持 539、大樂透、威力彩。")

# --- 側邊欄：數據維護 ---
with st.sidebar:
    st.header("數據維護")
    if st.button("🔄 同步最新獎號"):
        st.toast("正在同步最新數據...", icon="⏳")
        # 這裡放置你的爬蟲或同步邏輯
        st.success("數據同步完成！")

# --- 分頁標籤設定 ---
tab1, tab2, tab3 = st.tabs(["今彩 539", "大樂透 649", "威力彩"])

# ================================================================
# 今彩 539
# ================================================================
with tab1:
    st.header("今彩 539 分析預測")
    n_539 = st.slider("預測組數", 1, 10, 5, key="s539")
    
    if st.button("🔮 開始 539 混合權重分析"):
        st.subheader("預測結果表")
        col1, spacer1 = st.columns([0.35, 0.65]) # 減少 65% 寬度
        with col1:
            # 這裡放你的 539 數據產出邏輯
            # df_539 = get_539_results(n_539) 
            st.write("表格已縮減至 35% 寬度")
            # st.dataframe(df_539, use_container_width=True)

# ================================================================
# 大樂透 649
# ================================================================
with tab2:
    st.header("大樂透 649 分析預測")
    n_649 = st.slider("預測組數", 1, 10, 5, key="s649")
    
    if st.button("🔮 開始 649 混合權重分析"):
        st.subheader("預測結果表")
        col2, spacer2 = st.columns([0.35, 0.65]) # 減少 65% 寬度
        with col2:
            try:
                # 呼叫你 main_649.py 裡的邏輯
                df_649 = get_649_results(n_649) 
                st.dataframe(df_649, use_container_width=True)
            except NameError:
                st.error("找不到 get_649_results 函數，請確認 import 名稱。")

# ================================================================
# 威力彩
# ================================================================
with tab3:
    st.header("威力彩 分析預測")
    n_power = st.slider("預測組數", 1, 10, 5, key="spower")
    
    if st.button("🔮 開始 威力彩 混合權重分析"):
        st.subheader("預測結果表")
        col3, spacer3 = st.columns([0.35, 0.65]) # 減少 65% 寬度
        with col3:
            try:
                # 呼叫你 main_power.py 裡的邏輯
                df_power = get_power_results(n_power)
                st.dataframe(df_power, use_container_width=True)
            except NameError:
                st.error("找不到 get_power_results 函數，請確認 import 名稱。")

# --- 頁尾 ---
st.markdown("---")
st.caption("Designed by Gemini吉米 | 僅供學術研究，博弈有風險請謹慎參與。")