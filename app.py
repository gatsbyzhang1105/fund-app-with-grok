# app.py
from typing import Dict, List
import streamlit as st
import pandas as pd

from config import *
from utils import normalize_position_table
from portfolio_io import (
    load_fund_presets, save_fund_presets,
    load_holdings_archive_text, save_holdings_archive_text,
    rows_to_holdings_text, normalize_position_table
)
from decision_engine import analyze_single_fund_v26
from data_sources import get_fund_history, get_estimate
from calibration_io import load_calibration_feedback, get_feedback_stats


st.set_page_config(page_title='基金投资分析 Cloud · V28 优化版', page_icon='📊', layout='wide')

# ====================== Session State 初始化 ======================
if '_position_editor_version' not in st.session_state:
    st.session_state['_position_editor_version'] = 0
if '_analysis_update_map' not in st.session_state:
    st.session_state['_analysis_update_map'] = {}

# ====================== 页面主界面 ======================
st.title("基金投资分析 Cloud · 优化版")

# 基金代码输入
preview_codes = st.text_input(
    "输入基金代码（多个用空格/逗号分隔）",
    placeholder="003305 019032 513400",
    value=st.session_state.get('_last_codes', '')
).strip()

if preview_codes:
    codes = [c.strip() for c in re.split(r'[,，\s]+', preview_codes) if c.strip()]
    st.session_state['_last_codes'] = preview_codes
else:
    codes = []

# 持仓档案编辑器
st.subheader("基础持仓档案")
position_rows = st.data_editor(
    pd.DataFrame(normalize_position_table([])),  # 默认空表
    key=f"position_base_editor_v{st.session_state['_position_editor_version']}",
    num_rows="dynamic",
    use_container_width=True
)

# 开始分析按钮
if st.button("🚀 开始分析", type="primary", use_container_width=True):
    if not codes:
        st.warning("请先输入基金代码")
        st.stop()

    # 调用优化后的决策引擎
    results = []
    for code in codes:
        with st.spinner(f"正在分析 {code}..."):
            result = analyze_single_fund_v26(
                code=code,
                style_choices={code: 'balanced'},   # 可后续扩展
                bench_choices={},
                engine_choices={},
                holdings_map={},
                position_detail_map={},
                total_portfolio_amount=0.0,
                default_weight_map={},
                style_exposure_map={},
                advanced=True,
                pro_mode=True,
                rf=0.03,
                trade_cost=0.001,
                bench_source_pref='auto',
                max_single_weight=35.0,
                max_style_exposure=60.0,
                backtest_days=252
            )
            if result:
                results.append(result)

    # 显示结果（此处可继续扩展）
    if results:
        st.success(f"已完成 {len(results)} 只基金分析")
        for r in results:
            st.write(f"**{r['code']}** 建议：{r.get('decision', {}).get('advice', '观望')}")

# ====================== 底部信息 ======================
st.caption("优化版 v28 - 使用 utils.py + 模块化结构 | 代码已大幅精简、可维护性提升")

print("app.py 优化版本加载完成")