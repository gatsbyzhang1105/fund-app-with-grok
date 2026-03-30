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

def ann_vol(r):
    r = pd.Series(r).dropna()
    return None if len(r) < 10 else r.std(ddof=1) * math.sqrt(252)

def score_from_raw(raw: float) -> float:
    return max(0, min(100, (raw + 6) / 12 * 100))

def clamp(x, a, b):
    return max(a, min(b, x))


# ====================== 战术模型 & 评分 ======================
def tactical_model(cur_nav: float, hist: pd.DataFrame, style_key: str) -> Dict:
    """简化版战术模型（可后续扩展）"""
    return {
        'raw': 0.0,
        'base_score': 50.0,
        'base_advice': '观望',
        'style_key': style_key,
        'stats': []
    }


def build_operation_signal(tactical: Dict, **kwargs) -> Dict:
    """构建操作信号"""
    return {
        'score': 50.0,
        'advice': '观望',
        'raw': 0.0,
        'base_score': tactical.get('base_score', 50.0),
        'base_advice': tactical.get('base_advice', '观望')
    }


# ====================== 主分析函数 ======================
def analyze_single_fund_v26(
    code: str,
    style_choices: Dict,
    bench_choices: Dict = None,
    engine_choices: Dict = None,
    holdings_map: Dict = None,
    position_detail_map: Dict = None,
    total_portfolio_amount: float = 0.0,
    default_weight_map: Dict = None,
    style_exposure_map: Dict = None,
    advanced: bool = True,
    pro_mode: bool = True,
    rf: float = 0.03,
    trade_cost: float = 0.001,
    bench_source_pref: str = 'auto',
    max_single_weight: float = 35.0,
    max_style_exposure: float = 60.0,
    backtest_days: int = 252
) -> Dict[str, Any]:
    """单只基金完整分析入口（优化重构版）"""
    try:
        holdings_map = holdings_map or {}
        position_detail_map = position_detail_map or {}
        default_weight_map = default_weight_map or {}

        # 1. 获取数据
        hist = get_fund_history(code)
        info = get_estimate(code)

        style_key = style_choices.get(code, 'balanced')

        # 2. 持仓快照
        snapshot = build_position_snapshot(
            code=code,
            display_nav=info,
            holdings_map=holdings_map,
            position_detail_map=position_detail_map,
            total_portfolio_amount=total_portfolio_amount
        )

        # 3. 战术模型 & 操作信号（简化版）
        tactical = tactical_model(float(info.get('estimate_nav', 0)), hist, style_key)
        operation = build_operation_signal(tactical)

        # 4. 最终决策
        decision = {
            'score': operation['score'],
            'advice': operation['advice'],
            'position_action': '维持仓位',
            'direction': '中性',
            'raw': operation['raw']
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
        print(f"分析 {code} 时出错: {e}")
        return {'code': code, 'success': False, 'error': str(e)}


print("✅ decision_engine.py 优化版加载完成")