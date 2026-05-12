import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# 1. 網頁基本設定
st.set_page_config(page_title="工地進度管理系統", layout="wide")
st.title("🏗️ 裝修工程進度管理系統 (專業版)")

# 2. 初始資料
if 'gantt_df' not in st.session_state:
    initial_data = [
        {"任務": "優先處理衛浴/馬桶按鈕", "工種": "水電工程", "開始": "2026-04-16", "結束": "2026-04-17", "防呆提醒": "確保工班可用廁所"},
        {"任務": "雲端電表安裝", "工種": "水電工程", "開始": "2026-04-17", "結束": "2026-04-18", "防呆提醒": "伺服器需留網路"},
        {"任務": "全室更換崁燈", "工種": "水電工程", "開始": "2026-04-18", "結束": "2026-04-19", "防呆提醒": "4000K 自然光"},
        {"任務": "全室刷漆與床墊送達", "工種": "漆做工程", "開始": "2026-04-25", "結束": "2026-04-26", "防呆提醒": "床墊注意防塵"}
    ]
    df = pd.DataFrame(initial_data)
    
    # 🌟【修正核心 1】：強制將文字轉換為「真實的日期時間格式」
    df['開始'] = pd.to_datetime(df['開始']).dt.date
    df['結束'] = pd.to_datetime(df['結束']).dt.date
    
    st.session_state['gantt_df'] = df

# 3. 側邊欄：新增任務功能
with st.sidebar:
    st.header("➕ 新增任務")
    new_task = st.text_input("任務名稱")
    new_cat = st.selectbox("工種", ["水電工程", "泥作工程", "漆做工程", "木工工程", "地板工程", "軟裝工程", "清潔收尾"])
    new_start = st.date_input("開始日期", date.today())
    new_end = st.date_input("結束日期", date.today())
    new_note = st.text_input("💡 防呆提醒")
    
    if st.button("加入清單"):
        # 🌟【修正核心 2】：移除 str()，直接將 new_start 和 new_end 以日期格式存入
        new_row = pd.DataFrame([{"任務": new_task, "工種": new_cat, "開始": new_start, "結束": new_end, "防呆提醒": new_note}])
        st.session_state['gantt_df'] = pd.concat([st.session_state['gantt_df'], new_row], ignore_index=True)
        st.rerun()

# 4. 中央區域：互動式編輯表格
st.header("📊 工程數據管理")
st.info("💡 提示：你可以直接點擊表格修改日期、任務名稱。點擊左側選取列後按 Delete 鍵即可刪除任務。")

edited_df = st.data_editor(
    st.session_state['gantt_df'],
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "開始": st.column_config.DateColumn(),
        "結束": st.column_config.DateColumn(),
    }
)

st.session_state['gantt_df'] = edited_df

# 5. 繪製甘特圖與輸出
if not edited_df.empty:
    fig = px.timeline(
        edited_df, 
        x_start="開始", 
        x_end="結束", 
        y="任務", 
        color="工種",
        hover_data=["防呆提醒"],
        title="工地施工時程總覽"
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(xaxis_tickformat='%m/%d')
    
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.header("📁 輸出報表")
    col_out1, col_out2 = st.columns(2)
    
    with col_out1:
        html_bytes = fig.to_html().encode('utf-8')
        st.download_button(
            label="📥 下載互動式甘特圖 (HTML)",
            data=html_bytes,
            file_name="工地進度表.html",
            mime="text/html"
        )

    with col_out2:
        st.write("如需 PDF 報告，建議直接使用瀏覽器的「列印 (Cmd+P)」並選擇「另存為 PDF」，畫面最為完整。")
else:
    st.warning("目前清單為空，請先新增任務。")
