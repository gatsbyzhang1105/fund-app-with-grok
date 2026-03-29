# app.py （临时自包含版 - 不再依赖 utils.py）
import streamlit as st
import pandas as pd
import re
from datetime import datetime

# ====================== 直接内置 normalize_position_table ======================
def normalize_position_table(df_like):
    if df_like is None:
        return []
    try:
        df = pd.DataFrame(df_like).copy()
    except Exception:
        return []
    if df.empty:
        return []

    rename_map = {}
    for col in df.columns:
        s = str(col).strip()
        if s in {'代码', '基金代码'}:
            rename_map[col] = '基金代码'
        elif s in {'持仓成本', '持仓成本净值'}:
            rename_map[col] = '持仓成本净值'
        elif s in {'投资成本', '当前持有本金', '本金'}:
            rename_map[col] = '投资成本'
        elif s in {'目前盈亏情况', '盈亏', '盈亏情况'}:
            rename_map[col] = '目前盈亏情况'

    df = df.rename(columns=rename_map)

    for col in ['基金代码', '持仓成本净值', '投资成本', '目前盈亏情况']:
        if col not in df.columns:
            df[col] = '' if col in {'基金代码', '目前盈亏情况'} else None

    rows = []
    seen = set()
    for _, row in df[['基金代码', '持仓成本净值', '投资成本', '目前盈亏情况']].iterrows():
        code = str(row.get('基金代码', '') or '').strip()
        if not code:
            continue
        try:
            cost_nav = float(row.get('持仓成本净值'))
            principal = float(row.get('投资成本'))
        except Exception:
            continue
        if cost_nav <= 0 or principal < 0:
            continue
        pnl = str(row.get('目前盈亏情况', '') or '').strip()
        item = {
            '基金代码': code,
            '持仓成本净值': round(cost_nav, 6),
            '投资成本': round(principal, 2),
            '目前盈亏情况': pnl,
        }
        if code in seen:
            rows = [r for r in rows if r['基金代码'] != code]
        seen.add(code)
        rows.append(item)
    return rows

# ====================== 页面 ======================
st.set_page_config(page_title='基金投资分析 Cloud · 临时测试版', layout='wide')
st.title("基金投资分析 Cloud · 临时测试版")

preview_codes = st.text_input("输入基金代码（多个用空格分隔）", placeholder="003305 019032")

if st.button("🚀 开始分析", type="primary", use_container_width=True):
    if not preview_codes.strip():
        st.warning("请输入基金代码")
        st.stop()
    codes = [c.strip() for c in re.split(r'[,，\s]+', preview_codes.strip()) if c.strip()]
    st.success(f"收到 {len(codes)} 只基金：{codes}")
    st.info("（决策引擎部分暂未完全接入，后续我会继续给你完整版）")

st.caption("这是临时自包含版，已解决 import 错误。你可以正常运行了。")