# portfolio_io.py
from typing import Dict, Any, List, Tuple
from datetime import datetime
import json

from config import *
from utils import safe_float, sanitize_code, normalize_position_table


def _sanitize_preset_item(item: Dict[str, Any]) -> Dict[str, Any] | None:
    if not isinstance(item, dict):
        return None

    style = item.get('style', 'balanced')
    bench = item.get('bench', 'auto_style')
    engine = item.get('engine', 'auto_engine')
    weight = safe_float(item.get('weight'))

    style = style if style in STYLE_CFG else 'balanced'
    bench = bench if bench in {'auto_style', *BENCHMARKS.keys()} else 'auto_style'
    engine = engine if engine in A_SHARE_ENGINE_CFG else 'auto_engine'

    holding = None
    raw = item.get('holding')
    if isinstance(raw, dict):
        code = sanitize_code(raw.get('基金代码') or raw.get('code'))
        cost_nav = safe_float(raw.get('持仓成本净值') or raw.get('cost_nav'))
        principal = safe_float(raw.get('投资成本') or raw.get('principal'))
        if code and cost_nav is not None and principal is not None and cost_nav > 0 and principal >= 0:
            holding = {
                '基金代码': code,
                '持仓成本净值': round(cost_nav, 6),
                '投资成本': round(principal, 2),
                '目前盈亏情况': str(raw.get('目前盈亏情况') or raw.get('pnl', '')).strip(),
            }

    return {
        'style': style,
        'bench': bench,
        'engine': engine,
        'weight': weight,
        'updated_at': str(item.get('updated_at', '')),
        'holding': holding
    }


def load_fund_presets() -> Dict[str, Dict]:
    try:
        if not PRESET_FILE.exists():
            return {}
        data = json.loads(PRESET_FILE.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            return {}
        return {sanitize_code(k): v for k, v in data.items() if (v := _sanitize_preset_item(v))}
    except Exception:
        return {}


def save_fund_presets(presets: Dict) -> Tuple[bool, str]:
    try:
        cleaned = {sanitize_code(k): v for k, v in (presets or {}).items() if (v := _sanitize_preset_item(v))}
        PRESET_FILE.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding='utf-8')
        return True, ''
    except Exception as e:
        return False, str(e)