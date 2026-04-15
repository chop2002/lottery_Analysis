import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# 確保 Streamlit 能找到同目錄下的 main_ 檔案
sys.path.append(os.path.dirname(__file__))

# --- 頁面配置 ---
st.set_page_config(page_title="吉米彩卷分析系統", layout="centered")

# --- 導入邏輯 ---
try:
    # 這裡我們導入你檔案裡的 export 函數
    import main_649
    import main_power
except ImportError as e:
    st.error(f"導入檔案失敗，請檢查檔名：{e}")

# --- 介面標題 ---
st.title("🎰 吉米彩卷分析系統")
st.info("朋友你好！支持 539、大樂透、威力彩分析。")

tab1, tab2, tab3 = st.tabs(["今彩 539", "大樂透 649", "威力彩"])

# ================================================================
# 大樂透 649 區塊
# ================================================================
with tab2:
    st.header("大樂透 649 分析預測")
    n_649 = st.slider("預測組數", 1, 10, 5, key="s649")
    
    if st.button("🔮 開始 649 混合權重分析"):
        st.subheader("預測結果表")
        
        # 建立 35% 寬度的欄位
        col_table, col_spacer = st.columns([0.35, 0.65])
        
        with col_table:
            # 這裡模擬你 main_649.py 裡的 selected_groups 結構
            # 實務上你之後要把這裡換成你真正的運算邏輯
            mock_groups = [
                {"main": [3, 11, 18, 25, 37, 41], "special_no": 9, "score": 93.2},
                {"main": [5, 12, 20, 28, 33, 45], "special_no": 17, "score": 88.4},
                {"main": [7, 15, 22, 30, 40, 49], "special_no": 2, "score": 85.1},
                {"main": [1, 10, 19, 27, 35, 42], "special_no": 11, "score": 82.4},
                {"main": [8, 14, 23, 31, 39, 46], "special_no": 5, "score": 80.7},
            ]
            
            # 取出 user 指定的組數
            display_groups = mock_groups[:n_649]
            
            # 將資料轉為 DataFrame 顯示
            rows = []
            for i, item in enumerate(display_groups, start=1):
                rows.append({
                    "組別": i,
                    "號碼": f"{sorted(item['main'])}",
                    "特別號": item["special_no"],
                    "評分": item["score"]
                })
            
            df_display = pd.DataFrame(rows)
            st.dataframe(df_display, use_container_width=True)
            
            # 💡 同時執行你原本的寫入 CSV 功能
            try:
                main_649.export_649_predictions(
                    predict_date=datetime.now().strftime("%Y-%m-%d"),
                    batch_id="web_test",
                    model_name="web_v1",
                    selected_groups=display_groups
                )
                st.success("✅ 數據已備份至後端 CSV")
            except Exception as e:
                st.warning(f"CSV 備份失敗（但不影響顯示）: {e}")

# ================================================================
# 威力彩 區塊 (以此類推)
# ================================================================
with tab3:
    st.header("威力彩 分析預測")
    # ... 邏輯同上 ...
    st.write("請參照大樂透邏輯串接 main_power.py")

st.markdown("---")
st.caption("Designed by Gemini吉米 | 僅供學術研究")