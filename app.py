import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# 1. 網頁基本設定
st.set_page_config(page_title="工程執行管控系統", layout="wide")
st.title("🚧 裝修工程執行與驗收看板")

# 2. 初始資料庫設定
if 'gantt_df' not in st.session_state:
    st.session_state['gantt_df'] = pd.DataFrame(columns=[
        "案場", "工程內容", "工種", "開始", "結束", "狀態", "完成度 (%)", "發包預算", "實際請款", "防呆與工法"
    ])

# 3. 側邊欄：新增工程與模板匯入
with st.sidebar:
    st.header("📋 快速建立工程")
    
    if st.button("📥 載入【減法設計】標準工序"):
        template_data = [
            {"案場": "新案場", "工程內容": "保護工程與清運", "工種": "前置作業", "開始": date.today(), "結束": date.today(), "狀態": "🟢 施工中", "完成度 (%)": 0, "發包預算": 15000, "實際請款": 0, "防呆與工法": "傢俱清運優先申請"},
            {"案場": "新案場", "工程內容": "明管配置與軌道燈", "工種": "水電工程", "開始": date.today(), "結束": date.today(), "狀態": "🟢 施工中", "完成度 (%)": 0, "發包預算": 50000, "實際請款": 0, "防呆與工法": "工業風裸露設計"},
            {"案場": "新案場", "工程內容": "系統櫃貼膜", "工種": "木工工程", "開始": date.today(), "結束": date.today(), "狀態": "🟢 施工中", "完成度 (%)": 0, "發包預算": 40000, "實際請款": 0, "防呆與工法": "著重表面包覆"},
            {"案場": "新案場", "工程內容": "天地壁單色噴漆", "工種": "漆做工程", "開始": date.today(), "結束": date.today(), "狀態": "🟢 施工中", "完成度 (%)": 0, "發包預算": 35000, "實際請款": 0, "防呆與工法": "木工退場後進場"}
        ]
        new_df = pd.DataFrame(template_data)
        st.session_state['gantt_df'] = pd.concat([st.session_state['gantt_df'], new_df], ignore_index=True)
        st.rerun()

    st.divider()
    st.subheader("➕ 手動新增單一任務")
    new_site = st.text_input("案場", placeholder="例如: 西安街")
    new_task = st.text_input("工程內容")
    new_cat = st.selectbox("工種", ["前置作業", "水電工程", "泥作工程", "漆做工程", "木工工程", "地板工程", "設備安裝", "清潔收尾"])
    
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        new_start = st.date_input("開始", date.today())
    with col_date2:
        new_end = st.date_input("結束", date.today())
        
    new_budget = st.number_input("發包預算 ($)", min_value=0, value=0, step=1000)
    new_note = st.text_input("💡 防呆與工法提醒")
    
    if st.button("手動加入清單"):
        if new_site and new_task:
            new_row = pd.DataFrame([{
                "案場": new_site, "工程內容": new_task, "工種": new_cat, 
                "開始": new_start, "結束": new_end, "狀態": "🟢 施工中", "完成度 (%)": 0, 
                "發包預算": new_budget, "實際請款": 0, "防呆與工法": new_note
            }])
            st.session_state['gantt_df'] = pd.concat([st.session_state['gantt_df'], new_row], ignore_index=True)
            st.rerun()
        else:
            st.error("⚠️ 案場與工程內容必填！")

# 4. 工程數據管理表格
st.header("📊 工地現場驗收與數據登打")
st.info("💡 現場巡視重點：直接修改「狀態燈號」推進驗收進度，並確認「實際請款」是否符合發包預算。")

df_current = st.session_state['gantt_df']

if not df_current.empty:
    edited_df = st.data_editor(
        df_current,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "開始": st.column_config.DateColumn(),
            "結束": st.column_config.DateColumn(),
            "完成度 (%)": st.column_config.ProgressColumn("完成度 (%)", format="%d%%", min_value=0, max_value=100),
            # 【極簡版重點】精準的驗收工作流
            "狀態": st.column_config.SelectboxColumn("狀態燈號", options=[
                "🟢 施工中", 
                "🔵 待驗收", 
                "🟡 驗收修正中", 
                "✅ 驗收完成"
            ]),
            "發包預算": st.column_config.NumberColumn("發包預算 ($)", format="$ %d"),
            "實際請款": st.column_config.NumberColumn("實際請款 ($)", format="$ %d")
        }
    )
    st.session_state['gantt_df'] = edited_df

    # 5. 專注於工程端的核心指標
    st.divider()
    total_budget = edited_df['發包預算'].sum()
    total_actual = edited_df['實際請款'].sum()
    remaining_budget = total_budget - total_actual
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("發包總預算", f"$ {total_budget:,}")
    with col2:
        st.metric("目前已請款金額", f"$ {total_actual:,}")
    with col3:
        st.metric("工程款剩餘額度", f"$ {remaining_budget:,}")

    # 6. 甘特圖：工程排程視覺化
    st.divider()
    custom_colors = {"前置作業": "#7F7F7F", "水電工程": "#1F77B4", "泥作工程": "#8C564B", "漆做工程": "#FF7F0E", "木工工程": "#2CA02C", "地板工程": "#9467BD", "設備安裝": "#E377C2", "清潔收尾": "#17BECF"}
    
    fig_gantt = px.timeline(
        edited_df, x_start="開始", x_end="結束", y="工程內容", color="工種", 
        color_discrete_map=custom_colors, 
        hover_data=["案場", "狀態", "完成度 (%)", "防呆與工法"], 
        title="📅 施工排程甘特圖"
    )
    fig_gantt.update_yaxes(autorange="reversed")
    fig_gantt.update_layout(xaxis_tickformat='%m/%d')
    st.plotly_chart(fig_gantt, use_container_width=True)

else:
    st.info("👈 請從左側匯入模板或新增任務。")
