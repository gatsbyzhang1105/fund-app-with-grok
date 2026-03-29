# utils.py
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import re
from datetime import datetime

def safe_float(val: Any, default: Optional[float] = None) -> 
Optional[float]:
    """安全转换为 float，处理各种异常情况"""
    if val in (None, '', 'None', 'null', 'NaN'):
        return default
    try:
        f = float(val)
        return f if np.isfinite(f) else default
    except (ValueError, TypeError):
        return default

def sanitize_code(code: Any) -> str:
    """清理基金代码"""
    return str(code or '').strip()

def normalize_position_table(df_like: Any) -> List[Dict]:
    """标准化持仓表格（核心复用函数，已大幅优化）"""
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

    rows: List[Dict] = []
    seen = set()
    for _, row in df[['基金代码', '持仓成本净值', '投资成本', 
'目前盈亏情况']].iterrows():
        code = sanitize_code(row.get('基金代码'))
        if not code:
            continue

        cost_nav = safe_float(row.get('持仓成本净值'))
        principal = safe_float(row.get('投资成本'))
        if cost_nav is None or principal is None or cost_nav <= 0 or 
principal < 0:
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

