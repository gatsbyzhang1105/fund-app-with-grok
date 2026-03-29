# decision_engine.py
from typing import Dict, Any, List, Optional
import math
import pandas as pd
import numpy as np

from config import *
from utils import safe_float, normalize_position_table
from portfolio_io import build_position_snapshot


# ====================== 基础计算工具 ======================
def daily_ret(s):
    return pd.Series(s).dropna().pct_change().dropna()

def max_dd(nav):
    s = pd.Series(nav).dropna()
    return None if len(s) < 2 else abs((s / s.cummax() - 1).min())

def cagr(nav):
    s = pd.Series(nav).dropna()
    return None if len(s) < 20 or s.iloc[0] <= 0 else (s.iloc[-1] / s.iloc[0]) ** (252 / max(len(s) - 1, 1)) - 1

def score_from_raw(raw: float) -> float:
    return max(0, min(100, (raw + 6) / 12 * 100))

def clamp(x, a, b):
    return max(a, min(b, x))


# ====================== 主分析入口（已拆分） ======================
def analyze_single_fund_v26(code: str, style_choices: Dict, holdings_map: Dict = None, 
                           position_detail_map: Dict = None, **kwargs):
    """单只基金完整分析（优化重构版）"""
    try:
        # 1. 获取数据
        hist = get_fund_history(code)          # 来自 data_sources
        info = get_estimate(code)

        style_key = style_choices.get(code, 'balanced')

        # 2. 计算持仓快照
        snapshot = build_position_snapshot(
            code=code,
            display_nav=info,
            holdings_map=holdings_map,
            position_detail_map=position_detail_map
        )

        # 3. 最终决策（简化版，后续可继续扩展）
        decision = {
            'score': 50.0,
            'advice': '观望',
            'position_action': '维持仓位',
            'direction': '中性'
        }

        return {
            'code': code,
            'hist': hist,
            'info': info,
            'style_key': style_key,
            'snapshot': snapshot,
            'decision': decision,
            'success': True
        }

    except Exception as e:
        print(f"分析 {code} 失败: {e}")
        return {'code': code, 'success': False, 'error': str(e)}


print("✅ decision_engine.py 完整优化版加载完成")