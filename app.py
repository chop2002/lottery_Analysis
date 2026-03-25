import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

# 導入你原本的 utils 邏輯
from utils.update_539 import update_539
from utils.build_power_table1_latest5 import build_power_table1_latest5
# (以此類推，導入其他需要執行的 function)

st.set_page_config(page_title="吉米彩卷分析預測", page_icon="📈", layout="wide")

st.title("🎰 吉米彩卷分析系統 (Cloud版)")
st.info("朋友你好！這是我開發的分析系統，支持 539、大樂透、威力彩。")

# --- 側邊欄：數據同步 ---
with st.sidebar:
    st.header("數據維護")
    if st.button("🔄 同步最新獎號"):
        with st.spinner("正在執行爬蟲更新..."):
            try:
                # 執行你寫好的 update 邏輯
                update_539()
                st.success("539 更新成功！")
                # 這裡可以加入 update_649() 等
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
            # 按順序執行你的流水線
            # 1. build tables... 2. predict... 3. hybrid...
            # 這裡直接模擬輸出最後的結果表
            predict_path = "data/539/query/539_table3_predict_hybrid_weighted.csv"
            if os.path.exists(predict_path):
                df_res = pd.read_csv(predict_path)
                st.dataframe(df_res.style.highlight_max(axis=0), use_container_width=True)
                st.balloons()
            else:
                st.warning("尚未生成預測資料，請確認後端邏輯已執行。")

    # Excel 下載功能 (解決你 Export 的問題)
    st.divider()
    if st.button("📥 下載完整 539 報表 (Excel)"):
        # 這裡不直接存檔，而是存入記憶體給瀏覽器下載
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 讀取你的各張表並寫入
            pd.read_csv("data/539/query/539_table1_latest5.csv").to_excel(writer, sheet_name='Latest5')
            # ... 寫入其他 sheet
        st.download_button(
            label="點我儲存 Excel",
            data=output.getvalue(),
            file_name=f"539_report_{datetime.now().strftime('%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- 頁尾 ---
st.caption("Designed by Gemini吉米 | 僅供學術研究，博弈有風險請謹慎參與。")