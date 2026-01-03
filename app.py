import streamlit as st
import akshare as ak
import pandas as pd
import datetime
import time

# Streamlit 頁面配置（寬屏、手機友好）
st.set_page_config(page_title="中國A股熱門人氣股監控App", layout="wide")
st.title("🔥 中國A股熱門人氣個股監控系統")
st.markdown("""
**功能說明**：
- 實時監控熱門人氣股票（高換手率 + 資金活躍）
- 檢測顯性主力資金流入/流出
- 檢測潛在「拆單/暗池」隱藏買入（主力大單拆小單吸籌）
- 提供簡單入場/出場時機提示（僅供參考，基於資金流邏輯）
- 數據來源：東方財富/akshare（交易日9:30-15:00實時，非交易日數據靜止）

**警告**：本工具僅供學習參考，非投資建議！股市有風險，所有信號均有滯後與噪音，請結合基本面、技術面自行判斷。
""")

# 側邊欄參數調整
st.sidebar.header("監控參數調整（可自訂）")
REFRESH_INTERVAL = st.sidebar.slider("自動刷新間隔（秒）", 60, 600, 300, help="建議300秒以上，避免請求過頻")
HIDDEN_BUY_THRESHOLD = st.sidebar.number_input("暗池買入閾值（小單淨流入，萬元）", value=5000, help="越高越嚴格")
VISIBLE_SELL_THRESHOLD = st.sidebar.number_input("顯性主力流出閾值（萬元）", value=-2000, help="負值表示主力顯性賣出")
HOT_TURNOVER = st.sidebar.number_input("熱門人氣換手率下限（%）", value=5.0, help="換手率越高越熱門")
TOP_N = st.sidebar.slider("顯示前N名", 10, 50, 20)

# 數據獲取函數
@st.cache_data(ttl=REFRESH_INTERVAL)  # 緩存數據，避免重複請求
def get_all_data():
    with st.spinner("正在下載全市場實時數據（約5000+股票），請稍等10-30秒..."):
        df = ak.stock_zh_a_spot_em()
        # 欄位清理
        fund_cols = ['主力淨流入-淨額', '超大單淨流入-淨額', '大單淨流入-淨額', 
                     '中單淨流入-淨額', '小單淨流入-淨額']
        for col in fund_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['顯性主力淨流入'] = df.get('超大單淨流入-淨額', 0) + df.get('大單淨流入-淨額', 0)
        df['漲跌幅'] = pd.to_numeric(df['漲跌幅'], errors='coerce').fillna(0)
        df['換手率'] = pd.to_numeric(df['換手率'], errors='coerce').fillna(0)
        df['總市值'] = pd.to_numeric(df['總市值'], errors='coerce').fillna(0)
        
        # 過濾：排除ST、退市、小市值、低活躍
        df = df[~df['名稱'].str.contains('ST|退|*', na=False)]
        df = df[df['總市值'] > 3e9]  # 30億以上
        
        return df

# 信號判斷函數
def generate_signal(row):
    visible = row['顯性主力淨流入']
    hidden = row['小單淨流入-淨額']
    turnover = row['換手率']
    change = row['漲跌幅']
    
    signals = []
    if visible > 1e7:  # 顯性主力強流入 >1億
        signals.append("🟢 顯性主力強買，熱門吸籌")
    if visible < -5e6 and change < 0:  # 主力流出 + 股價跌
        signals.append("🔴 主力出貨，注意出場風險")
    
    if (visible < VISIBLE_SELL_THRESHOLD * 1e4 and 
        hidden > HIDDEN_BUY_THRESHOLD * 1e4 and 
        change >= -1 and turnover > 3):  # 暗池條件
        signals.append("🟡 潛在暗池拆單強買，吸籌階段（考慮低位入場）")
    
    if turnover > HOT_TURNOVER and change > 5:
        signals.append("⚡ 超高人氣，短期熱門")
    
    if not signals:
        return "⚪ 無明顯信號"
    return " | ".join(signals)

# 主邏輯
df = get_all_data()

# 熱門人氣篩選：換手率高 + 有資金活躍
hot_df = df[df['換手率'] > HOT_TURNOVER].copy()

# 顯性主力熱門榜
visible_hot = hot_df[hot_df['顯性主力淨流入'] > 0].sort_values(by='顯性主力淨流入', ascending=False).head(TOP_N)

# 暗池拆單熱門榜
hidden_hot = hot_df[
    (hot_df['顯性主力淨流入'] < VISIBLE_SELL_THRESHOLD * 1e4) &
    (hot_df['小單淨流入-淨額'] > HIDDEN_BUY_THRESHOLD * 1e4) &
    (hot_df['漲跌幅'] >= -2)
].sort_values(by='小單淨流入-淨額', ascending=False).head(TOP_N)

# 添加信號
if not visible_hot.empty:
    visible_hot['信號提示'] = visible_hot.apply(generate_signal, axis=1)
if not hidden_hot.empty:
    hidden_hot['信號提示'] = hidden_hot.apply(generate_signal, axis=1)

# 格式化金額（億元）
def format_money(df):
    money_cols = ['顯性主力淨流入', '小單淨流入-淨額', '主力淨流入-淨額', '總市值']
    for col in money_cols:
        if col in df.columns:
            df[f'{col}(億元)'] = (df[col] / 1e8).round(2)
    return df

# 顯示結果
if stock_code:

search_df=df[df['代碼'].str.contains（stock_code）|df['''str.contains（stock_code）]
如果不是search_df.empty：
st.子标题（f"個股資金詳情：{search_df. iloc[0][''mayoto']}（{search_df. iloc[0]']}）"
row = search_df.iloc[0]
    else:
斯特包含（stock_code）如果'']}'''str.contains（stock_code）]如果不是 search_df.empty：'代碼'
st.st.子标题（f"mayoto willoyoto mayoto：{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）"st.子标题（f"mayoto willoyoto mayoto：{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）"）
st.row = search_df.iloc[0]row = search_df.iloc[0]）
st.st.write（f"最新價：{row['you mayoto you']}：{row[''''']}％|{row['）

斯特包含（股票_代码）'.']}％|{row[str.contains（stock_code）]如果不是 search_df.empty:'mayou'
st. st.子标题（f"mayoto willoyoto mayoto:{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）st. mayoto mayoto（f"mayoto）willoyoto mayoto:{search_df。iloc[0]['mayoto']}{search_df
st. st.子标题（f"mayoto willoyoto mayoto:{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）st. mayoto mayoto（f"mayoto）willoyoto mayoto:{search_df。iloc[0]['mayoto']}{search_dfst.row = search_df.iloc[0]row = search_df.iloc[0]）
空的圣子标题 f# 顯示結果"mayoto willoyoto mayoto:{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）st. mayoto mayoto（f"包含（stock_code）mayoto）willoyoto mayoto:{search_df。iloc[0]['mayoto']}{search_df
    子标题 f圣
斯特"mayoto willoyoto mayoto:{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）st. mayoto mayoto（f"
mayoto）willoyoto mayoto:{search_df。iloc[0]['mayoto']}{search_dfsearch_df=df[st。st.子标题（f"mayoto willoyoto mayoto:{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）st. mayoto mayoto（f"mayoto）willoyotomayoto:{search_df. iloc[0]['mayoto']}{search_dfst. row=search_df. iloc[0]row=search_df. iloc[0]）[st。st.子标题（f"mayoto willoyoto mayoto:{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）st. mayoto mayoto（f"mayoto）willoyotomayoto:{search_df. iloc[0]['mayoto']}{search_dfst. row=search_df. iloc[0]row=search_df. iloc[0]）st.st.write（f"最新價：{row['you mayoto you']}：{row['''''st. row=search_df. iloc[0]row=search_df. iloc[0]空的圣子标题 f# 顯示結果"mayoto willoyoto mayoto:{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）st. mayoto mayoto（f"包含（stock_code）mayoto）willoyoto mayoto:{search_df。iloc[0]['mayoto']}{search_df子标题 f圣. 子标题 f圣(斯特"mayoto willoyoto mayoto:{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）st. mayoto mayoto（f"{斯特"mayoto willoyoto mayoto:{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）st. mayoto mayoto（f"['
行willoyoto）willoyoto mayoto:{search_df. iloc[0]['mayoto']}{search_dfsearch_df=df[st.子标题（f"mayoto willoyoto mayoto:{search_df. iloc[0]]}}（{search_df. iloc[0]]}）st. mayoto（f"mayoto）willoyotomayoto:{search_df。[0]['mayoto']}{search_dfst。row of search_df。row=search_df。[0]）[st.子标题（f"mayoto willoyoto mayoto:{search_df. iloc[0]['mayoto']}（{search_df. iloc[0]]]}）st. mayoto mayoto（f"mayoto）willoyotomayoto:{search_df.[0]['mayoto']}{search_dfst。row of search_df。row=search_df。st. st. write（f"最新價：{row['you mayoto you']}：{row[''''{劳工组织['''
劳工组织
圣'

st.如果 visible_hot.empty：]}.使用使用
you mayoto you“顯性主力淨流入”（“idden_you”）、“idden_hot”、“idden_hot”、“idden_hot”、“idden_hot”、“idden_hot”、“idden_hot”、“idden_hot”
{[写f][''''顯性主力淨流入'（“idden_you”）、“idden_hot”、“idden_hot”、“idden_hot”、“idden_hot”、“idden_hot”、“idden_hot”{'''"最新價：{row[you mayoto you]}：{row['''{you mayoto you]"最新價：{row[you mayoto you]}：{row['''{you mayoto you]\}：st. row of search_df. row=search_df.[0]）％|圣圣
）youmoviowemoto-行
信号（）***************************************************************************************************************************************************************************************************
hot[估計暗池流入 you mayou mayou mayou mayou you mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou mayou ma
cols=[如果 mayor c format_money（hidden_hot）][you 1*
dataframe(format_money(hidden_hot)[display_cols]，use_container_width=True)display_cols=[如果 mayor c format_money(hidden_hot)
退出
# 個股查詢功能
st.sidebar.header（[個股資金查詢]）
stock_code=st.侧栏 you.（[mayoto broyou（600519）you joryou willoyou]）
    else:
        st.sidebar
