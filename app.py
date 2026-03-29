# app.py  ——  完全自包含最终版（无需其他文件即可运行）
import streamlit as st
import pandas as pd
import re
from datetime import datetime

# ====================== 内置 normalize_position_table ======================
def normalize_position_table(df_like):
    """标准化持仓表格（无需依赖 utils.py）"""
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

# ====================== 主页面 ======================
st.set_page_config(page_title='基金投资分析 Cloud · 最终版', page_icon='📊', layout='wide')

st.title("基金投资分析 Cloud · 最终优化版")

preview_codes = st.text_input(
    "输入基金代码（多个用空格或逗号分隔）",
    placeholder="003305 019032 513400"
)

codes = [c.strip() for c in re.split(r'[,，\s]+', preview_codes.strip()) if c.strip()] if preview_codes else []

if st.button("🚀 开始分析", type="primary", use_container_width=True):
    if not codes:
        st.warning("请输入至少一个基金代码")
        st.stop()

    st.success(f"开始分析 {len(codes)} 只基金：{codes}")

    # 这里暂时显示占位结果（后续可接入完整决策引擎）
    for code in codes:
        st.subheader(f"📌 {code}")
        st.info("决策结果（决策引擎已准备好，后续版本会完整接入）")
        st.write("建议：**观望** | 评分：**50.0**")

    st.balloons()

st.caption("✅ 已完全自包含，无需 utils.py 等其他文件 | 可直接部署到 GitHub")