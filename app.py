import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# 1. 網頁基本設定
st.set_page_config(page_title="工程執行管控系統", layout="wide")
st.title("🚧 裝修工程執行與驗收管控系統")

# 2. 初始資料庫設定
if 'gantt_df' not in st.session_state:
    st.session_state['gantt_df'] = pd.DataFrame(columns=[
        "案場", "工程內容", "工種", "開始", "結束", "狀態", "完成度 (%)", "發包預算", "實際請款", "防呆與工法"
    ])

# 新增：照片紀錄資料庫
if 'photo_logs' not in st.session_state:
    st.session_state['photo_logs'] = []

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

# 4. 工程數據管理表格 (加入待驗收狀態)
st.header("📊 工地現場查核與數據登打")
st.info("💡 提示：當工班回傳照片後，可將狀態改為「🔵 待驗收」，確認無誤後再改為「✅ 驗收通過」。")

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
            # 新增「🔵 待驗收 (照片已傳)」的狀態
            "狀態": st.column_config.SelectboxColumn("狀態燈號", options=["🟢 施工中", "🟡 待料/待確認", "🔵 待驗收 (照片已傳)", "🔴 停工/卡關", "✅ 驗收通過"]),
            "發包預算": st.column_config.NumberColumn("發包預算 ($)", format="$ %d"),
            "實際請款": st.column_config.NumberColumn("實際請款 ($)", format="$ %d")
        }
    )
    st.session_state['gantt_df'] = edited_df

    # ================= 新增：照片上傳與驗收區塊 =================
    st.divider()
    st.header("📸 驗收與施工照片管理")
    
    col_upload, col_gallery = st.columns([1, 2])
    
    with col_upload:
        st.subheader("上傳回報照片")
        # 讓使用者選擇這張照片是屬於哪一個工程任務的
        task_list = edited_df['工程內容'].tolist()
        selected_task = st.selectbox("選擇要回報的工程項目", task_list)
        
        # 建立上傳檔案的元件 (支援多張照片)
        uploaded_files = st.file_uploader("選擇工班回傳的照片或現場紀錄", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        
        photo_note = st.text_input("照片備註 (例如: 廁所暗管已封板、防水測試已過)")
        
        if st.button("💾 儲存照片紀錄") and uploaded_files:
            for file in uploaded_files:
                # 實務上會存進 AWS/Google Drive，這裡我們先暫存進系統記憶體展示
                st.session_state['photo_logs'].append({
                    "task": selected_task,
                    "image": file,
                    "note": photo_note,
                    "date": date.today().strftime("%Y-%m-%d")
                })
            st.success("✅ 照片已成功與工程綁定！")
            st.rerun()

    with col_gallery:
        st.subheader("工地影像存證庫")
        if len(st.session_state['photo_logs']) > 0:
            # 用三排的方式展示照片牆
            cols = st.columns(3)
            for idx, log in enumerate(st.session_state['photo_logs']):
                with cols[idx % 3]:
                    st.image(log['image'], use_container_width=True)
                    st.caption(f"**{log['task']}**")
                    st.caption(f"📅 {log['date']}")
                    st.caption(f"📝 {log['note']}")
        else:
            st.info("目前還沒有上傳任何照片。")

    # ================= 繪製甘特圖 =================
    st.divider()
    custom_colors = {"前置作業": "#7F7F7F", "水電工程": "#1F77B4", "泥作工程": "#8C564B", "漆做工程": "#FF7F0E", "木工工程": "#2CA02C", "地板工程": "#9467BD", "設備安裝": "#E377C2", "清潔收尾": "#17BECF"}
    
    fig_gantt = px.timeline(
        edited_df, x_start="開始", x_end="結束", y="工程內容", color="工種", 
        color_discrete_map=custom_colors, hover_data=["案場", "狀態", "完成度 (%)", "防呆與工法"], title="📅 施工排程甘特圖"
    )
    fig_gantt.update_yaxes(autorange="reversed")
    fig_gantt.update_layout(xaxis_tickformat='%m/%d')
    st.plotly_chart(fig_gantt, use_container_width=True)

else:
    st.info("👈 請從左側匯入模板或新增任務。")
