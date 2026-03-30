# app.py  ——  最终完整模块化版
import streamlit as st
import pandas as pd
import re

# 导入优化后的模块
from config import *
from utils import normalize_position_table
from portfolio_io import load_fund_presets, save_fund_presets
from decision_engine import analyze_single_fund_v26
from calibration_io import get_feedback_stats

st.set_page_config(page_title='基金投资分析 Cloud · 最终模块化版', page_icon='📊', layout='wide')

st.title("基金投资分析 Cloud · 最终模块化版")

# 输入基金代码
preview_codes = st.text_input(
    "输入基金代码（多个用空格或逗号分隔）",
    placeholder="003305 019032 513400",
    value=st.session_state.get('_last_codes', '')
)

codes = [c.strip() for c in re.split(r'[,，\s]+', preview_codes.strip()) if c.strip()] if preview_codes else []

# 开始分析
if st.button("🚀 开始分析", type="primary", use_container_width=True):
    if not codes:
        st.warning("请先输入至少一个基金代码")
        st.stop()

    st.success(f"开始分析 {len(codes)} 只基金：{codes}")

    results = []
    for code in codes:
        with st.spinner(f"正在分析 {code}..."):
            result = analyze_single_fund_v26(
                code=code,
                style_choices={code: 'balanced'},
                holdings_map={},
                position_detail_map={},
                advanced=True,
                pro_mode=True,
                rf=0.03,
                trade_cost=0.001,
                bench_source_pref='auto',
                max_single_weight=35.0,
                max_style_exposure=60.0,
                backtest_days=252
            )
            if result and result.get('success'):
                results.append(result)
                decision = result.get('decision', {})
                st.subheader(f"📌 {code}")
                st.success(f"建议：**{decision.get('advice', '观望')}** | 评分：**{decision.get('score', 50.0):.1f}**")
            else:
                st.error(f"{code} 分析失败")

    if results:
        st.balloons()
        st.success(f"✅ 全部 {len(results)} 只基金分析完成！")

st.caption("✅ 最终模块化版 | 已接入所有优化模块 | 可直接用于 GitHub")

print("✅ app.py 最终模块化版加载完成")