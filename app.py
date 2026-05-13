import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# 1. 網頁基本設定
st.set_page_config(page_title="工程進度與請款核銷系統", layout="wide")
st.title("🚧 裝修工程進度與請款核銷看板")

# 2. 初始資料庫設定 (新增請款與發票相關欄位)
if 'total_budget' not in st.session_state:
    st.session_state['total_budget'] = 500000  # 預設總預算

if 'gantt_df' not in st.session_state:
    st.session_state['gantt_df'] = pd.DataFrame(columns=[
        "案場", "工程內容", "工種", "開始", "結束", "防呆與工法", 
        "工程狀態", "發票/憑證號碼", "核定應付金額", "付款狀態"
    ])

# 3. 側邊欄：總預算設定與新增任務
with st.sidebar:
    st.header("💰 財務總管")
    # 【實戰功能 1】由主理人直接填寫專案總預算
    new_total = st.number_input("設定專案總預算 ($)", min_value=0, value=st.session_state['total_budget'], step=10000)
    st.session_state['total_budget'] = new_total
    
    st.divider()
    
    st.header("📋 快速建立工程")
    if st.button("📥 載入【減法設計】標準工序"):
        template_data = [
            {"案場": "新案場", "工程內容": "保護工程與清運", "工種": "前置作業", "開始": date.today(), "結束": date.today(), "防呆與工法": "傢俱清運優先申請", "工程狀態": "🟢 施工中", "發票/憑證號碼": "", "核定應付金額": 0, "付款狀態": "❌ 尚未請款"},
            {"案場": "新案場", "工程內容": "明管配置與軌道燈", "工種": "水電工程", "開始": date.today(), "結束": date.today(), "防呆與工法": "工業風裸露設計", "工程狀態": "🟢 施工中", "發票/憑證號碼": "", "核定應付金額": 0, "付款狀態": "❌ 尚未請款"},
            {"案場": "新案場", "工程內容": "系統櫃貼膜", "工種": "木工工程", "開始": date.today(), "結束": date.today(), "防呆與工法": "著重表面包覆", "工程狀態": "🟢 施工中", "發票/憑證號碼": "", "核定應付金額": 0, "付款狀態": "❌ 尚未請款"},
            {"案場": "新案場", "工程內容": "天地壁單色噴漆", "工種": "漆做工程", "開始": date.today(), "結束": date.today(), "防呆與工法": "木工退場後進場", "工程狀態": "🟢 施工中", "發票/憑證號碼": "", "核定應付金額": 0, "付款狀態": "❌ 尚未請款"}
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
    new_note = st.text_input("💡 防呆與工法提醒")
    
    if st.button("手動加入清單"):
        if new_site and new_task:
            new_row = pd.DataFrame([{
                "案場": new_site, "工程內容": new_task, "工種": new_cat, 
                "開始": new_start, "結束": new_end, "防呆與工法": new_note,
                "工程狀態": "🟢 施工中", "發票/憑證號碼": "", "核定應付金額": 0, "付款狀態": "❌ 尚未請款"
            }])
            st.session_state['gantt_df'] = pd.concat([st.session_state['gantt_df'], new_row], ignore_index=True)
            st.rerun()
        else:
            st.error("⚠️ 案場與工程內容必填！")

# ================= 專注進度與時間的甘特圖 =================
st.header("📅 施工時間軸與工序 (純淨版)")
st.info("💡 圖表專注於「時間進程」與「工法提醒」，確保工班進場順序不打結。")

df_current = st.session_state['gantt_df']

if not df_current.empty:
    custom_colors = {"前置作業": "#7F7F7F", "水電工程": "#1F77B4", "泥作工程": "#8C564B", "漆做工程": "#FF7F0E", "木工工程": "#2CA02C", "地板工程": "#9467BD", "設備安裝": "#E377C2", "清潔收尾": "#17BECF"}
    
    # 甘特圖現在只顯示跟現場施工有關的資訊，不顯示金額
    fig_gantt = px.timeline(
        df_current, x_start="開始", x_end="結束", y="工程內容", color="工種", 
        color_discrete_map=custom_colors, 
        hover_data=["案場", "工程狀態", "防呆與工法"] 
    )
    fig_gantt.update_yaxes(autorange="reversed")
    fig_gantt.update_layout(xaxis_tickformat='%m/%d', height=350)
    st.plotly_chart(fig_gantt, use_container_width=True)

# ================= 財務與核銷數據 =================
st.divider()
st.header("💰 驗收與請款核銷作業")

if not df_current.empty:
    # 財務指標計算：只計算你「已經核定」的請款金額，以及「已經付出去」的錢
    total_budget = st.session_state['total_budget']
    
    # 實際要付的總額 (只要填了數字就算)
    total_payable = df_current['核定應付金額'].sum() 
    
    # 真正已經匯出去的錢 (狀態必須是已付款)
    total_paid = df_current.loc[df_current['付款狀態'] == "💸 已匯款/付清", '核定應付金額'].sum()
    
    # 剩餘可動用預算
    remaining_budget = total_budget - total_payable

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("專案總預算", f"$ {total_budget:,}")
    with col2:
        st.metric("核定應付總額", f"$ {total_payable:,}", help="已收到發票並由工程端驗收確認要付的總金額")
    with col3:
        st.metric("實際已撥款金額", f"$ {total_paid:,}", help="會計/財務已經匯給工班的錢")
    with col4:
        st.metric("預算剩餘額度", f"$ {remaining_budget:,}", delta=f"可用餘額", delta_color="normal")

    st.write("---")
    st.info("💡 驗收流程：1. 現場驗收完畢 ➡️ 2. 收到工班發票 ➡️ 3. 填入發票號碼與【核定應付金額】 ➡️ 4. 撥款後切換為【已匯款】。")
    
    # 表格：專注於驗收、請款與發票登錄
    edited_df = st.data_editor(
        df_current,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "開始": st.column_config.DateColumn(),
            "結束": st.column_config.DateColumn(),
            "工程狀態": st.column_config.SelectboxColumn("工程狀態 (現場)", options=["🟢 施工中", "🔵 待驗收", "🟡 驗收修正中", "✅ 驗收完成"]),
            "發票/憑證號碼": st.column_config.TextColumn("發票/憑證號碼", help="請輸入師傅提供的發票或收據單號"),
            "核定應付金額": st.column_config.NumberColumn("核定應付金額 ($)", format="$ %d", help="驗證實際要支付給工班的金額"),
            "付款狀態": st.column_config.SelectboxColumn("付款狀態 (財務)", options=["❌ 尚未請款", "⏳ 收到發票-待請款", "💸 已匯款/付清"])
        }
    )
    st.session_state['gantt_df'] = edited_df

else:
    st.info("👈 請從左側匯入模板或新增任務。")
