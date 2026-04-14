import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

# 導入你原本的 utils 邏輯 (請確保 GitHub 上也有這些資料夾)
from utils.update_539 import update_539
from utils.build_power_table1_latest5 import build_power_table1_latest5

st.set_page_config(page_title="吉米彩卷分析預測", page_icon="📈", layout="wide")

# --- CSS 強制隱藏 Streamlit 登入按鈕 (讓畫面更清爽) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🎰 吉米彩卷分析系統")
st.info("朋友你好！這是我開發的分析系統，支持 539、大樂透、威力彩。")

# --- 側邊欄：數據同步 ---
with st.sidebar:
    st.header("數據維護")
    if st.button("🔄 同步最新獎號"):
        with st.spinner("正在執行爬蟲更新..."):
            try:
                update_539()
                st.success("539 更新成功！")
            except Exception as e:
                st.error(f"更新失敗: {e}")

# --- 主畫面：預測操作 ---
tabs = st.tabs(["今彩 539", "大樂透 649", "威力彩"])

# 以 539 為例
with tabs[0]:
    st.subheader("今彩 539 分析預測")
    test_time = st.slider("預測組數", 1, 20, 5, key="539_slider")
    
    if st.button("🔮 開始 539 混合權重分析"):
        with st.spinner("計算中..."):
            predict_path = "data/539/query/539_table3_predict_hybrid_weighted.csv"
            if os.path.exists(predict_path):
                df_res = pd.read_csv(predict_path)
                st.write("### 預測結果表")
                st.dataframe(df_res.head(test_time).style.highlight_max(axis=0), use_container_width=True)
                st.balloons()
            else:
                st.warning("⚠️ 找不到預測資料檔，請先執行同步或確認路徑。")

    st.divider()
    if st.button("📥 下載完整 539 報表 (Excel)"):
        try:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # 安全讀取，若檔案不存在則跳過
                if os.path.exists("data/539/query/539_table1_latest5.csv"):
                    pd.read_csv("data/539/query/539_table1_latest5.csv").to_excel(writer, sheet_name='Latest5')
                else:
                    pd.DataFrame({"提示": ["尚未產生資料"]}).to_excel(writer, sheet_name='Latest5')
            
            st.download_button(
                label="點我儲存 Excel",
                data=output.getvalue(),
                file_name=f"539_report_{datetime.now().strftime('%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"產生下載檔失敗: {e}")

st.caption("Designed by Gemini吉米 | 僅供學術研究，博弈有風險請謹慎參與。")