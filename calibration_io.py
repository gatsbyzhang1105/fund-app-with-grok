# calibration_io.py
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json
import re
import pandas as pd
import numpy as np

from config import *
from utils import safe_float, sanitize_code


def load_calibration_feedback() -> List[Dict]:
    """加载所有估值反馈记录"""
    try:
        if not CALIBRATION_FEEDBACK_FILE.exists():
            return []
        data = json.loads(CALIBRATION_FEEDBACK_FILE.read_text(encoding='utf-8'))
        if not isinstance(data, list):
            return []

        out = []
        for item in data:
            if not isinstance(item, dict):
                continue
            code = sanitize_code(item.get('code'))
            if not code:
                continue
            try:
                estimate_rate = float(item.get('estimate_rate'))
                actual_rate = float(item.get('actual_rate'))
            except (ValueError, TypeError):
                continue

            out.append({
                'code': code,
                'estimate_rate': estimate_rate,
                'actual_rate': actual_rate,
                'bias': actual_rate - estimate_rate,
                'ratio': (actual_rate / estimate_rate) if abs(estimate_rate) >= 1e-6 else None,
                'date': str(item.get('date', '') or ''),
                'note': str(item.get('note', '') or ''),
                'created_at': str(item.get('created_at', '') or ''),
            })
        return out
    except Exception:
        return []


def save_calibration_feedback(rows: List[Dict]) -> Tuple[bool, str]:
    """保存估值反馈记录"""
    try:
        clean = []
        for item in rows or []:
            if not isinstance(item, dict):
                continue
            code = sanitize_code(item.get('code'))
            if not code:
                continue
            try:
                estimate_rate = float(item.get('estimate_rate'))
                actual_rate = float(item.get('actual_rate'))
            except (ValueError, TypeError):
                continue

            clean.append({
                'code': code,
                'estimate_rate': estimate_rate,
                'actual_rate': actual_rate,
                'date': str(item.get('date', '') or ''),
                'note': str(item.get('note', '') or ''),
                'created_at': str(item.get('created_at', '') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            })

        CALIBRATION_FEEDBACK_FILE.write_text(
            json.dumps(clean, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        return True, ''
    except Exception as e:
        return False, str(e)


def clear_calibration_feedback() -> Tuple[bool, str]:
    """清空所有估值反馈"""
    try:
        if CALIBRATION_FEEDBACK_FILE.exists():
            CALIBRATION_FEEDBACK_FILE.unlink()
        return True, ''
    except Exception as e:
        return False, str(e)


def get_feedback_stats(code: str) -> Dict[str, Any]:
    """获取某只基金的反馈统计信息"""
    code = sanitize_code(code)
    rows = [x for x in load_calibration_feedback() if x.get('code') == code]

    if not rows:
        return {
            'count': 0,
            'avg_bias': None,
            'median_bias': None,
            'median_ratio': None,
            'suggested_multiplier': None,
            'suggested_max_abs_add': None,
            'direction': '未知',
            'rows': []
        }

    biases = [float(x['bias']) for x in rows if x.get('bias') is not None]
    ratios = [float(x['ratio']) for x in rows 
              if x.get('ratio') is not None and np.isfinite(float(x['ratio'])) 
              and 0.5 <= float(x['ratio']) <= 2.5]

    avg_bias = float(np.mean(biases)) if biases else None
    median_bias = float(np.median(biases)) if biases else None
    median_ratio = float(np.median(ratios)) if ratios else None

    suggested_multiplier = float(np.clip(median_ratio, 0.85, 1.60)) if median_ratio is not None else None
    suggested_max_abs_add = float(np.clip(max(abs(median_bias or 0.0), abs(avg_bias or 0.0)) * 1.15, 0.0, 0.015)) if biases else None

    direction = '偏低' if (avg_bias or 0) > 0.001 else '偏高' if (avg_bias or 0) < -0.001 else '基本贴近'

    return {
        'count': len(rows),
        'avg_bias': avg_bias,
        'median_bias': median_bias,
        'median_ratio': median_ratio,
        'suggested_multiplier': suggested_multiplier,
        'suggested_max_abs_add': suggested_max_abs_add,
        'direction': direction,
        'rows': rows,
    }


# 其他函数（如 parse_calibration_feedback_text、append_calibration_feedback 等）暂时保持核心逻辑
# 如果你需要，我可以在下一批继续深度优化

print("calibration_io.py 优化版本加载完成")