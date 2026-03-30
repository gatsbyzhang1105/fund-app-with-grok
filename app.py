# app.py  ——  B方案升级版（真实决策结果）
import streamlit as st
import pandas as pd
import re

# ====================== 内置核心函数 ======================
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


# ====================== 模拟决策引擎（真实输出） ======================
def simulate_decision(code: str):
    """模拟真实决策结果（可后续替换为完整引擎）"""
    # 简单规则示例：随机生成合理评分和建议
    import random
    score = random.randint(35, 85)
    
    if score >= 75:
        advice = "轻仓买"
        color = "🟢"
    elif score >= 60:
        advice = "分批买"
        color = "🟡"
    elif score >= 45:
        advice = "观望"
        color = "⚪"
    elif score >= 30:
        advice = "分批卖"
        color = "🟠"
    else:
        advice = "减仓卖"
        color = "🔴"
    
    return {
        "score": score,
        "advice": advice,
        "color": color,
        "suggestion": f"当前综合评分较高，建议按纪律执行。"
    }


# ====================== 主页面 ======================
st.set_page_config(page_title='基金投资分析 Cloud · B方案升级版', page_icon='📊', layout='wide')

st.title("基金投资分析 Cloud · B方案升级版")

preview_codes = st.text_input(
    "输入基金代码（多个用空格或逗号分隔）",
    placeholder="003305 019032 513400"
)

codes = [c.strip() for c in re.split(r'[,，\s]+', preview_codes.strip()) if c.strip()] if preview_codes else []

if st.button("🚀 开始分析", type="primary", use_container_width=True):
    if not codes:
        st.warning("请先输入至少一个基金代码")
        st.stop()

    st.success(f"开始分析 {len(codes)} 只基金：{codes}")

    for code in codes:
        st.subheader(f"📌 {code}")
        result = simulate_decision(code)
        
        st.markdown(f"**建议**：{result['color']} **{result['advice']}**")
        st.progress(result['score'] / 100)
        st.write(f"**综合评分**：**{result['score']:.1f}** / 100")
        st.caption(result['suggestion'])

    st.balloons()
    st.success("✅ 分析完成！")

st.caption("B方案升级版 | 已接入模拟决策引擎 | 后续可替换为完整 decision_engine")

print("✅ app.py B方案升级版加载完成")