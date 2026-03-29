# portfolio_io.py
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json

from config import *
from utils import safe_float, sanitize_code, normalize_position_table


def _sanitize_preset_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """清理单条预设项（核心函数，已优化）"""
    if not isinstance(item, dict):
        return None

    style = item.get('style', 'balanced')
    bench = item.get('bench', 'auto_style')
    engine = item.get('engine', 'auto_engine')
    weight = safe_float(item.get('weight'))

    # 合法性校验
    style = style if style in STYLE_CFG else 'balanced'
    bench = bench if bench in {'auto_style', *BENCHMARKS.keys()} else 'auto_style'
    engine = engine if engine in A_SHARE_ENGINE_CFG else 'auto_engine'

    # 处理 holding（持仓信息）
    holding = None
    raw_holding = item.get('holding')
    if isinstance(raw_holding, dict):
        code = sanitize_code(raw_holding.get('基金代码') or raw_holding.get('code'))
        cost_nav = safe_float(raw_holding.get('持仓成本净值') or raw_holding.get('cost_nav'))
        principal = safe_float(raw_holding.get('投资成本') or raw_holding.get('principal'))

        if code and cost_nav is not None and principal is not None and cost_nav > 0 and principal >= 0:
            holding = {
                '基金代码': code,
                '持仓成本净值': round(cost_nav, 6),
                '投资成本': round(principal, 2),
                '目前盈亏情况': str(raw_holding.get('目前盈亏情况') or raw_holding.get('pnl', '')).strip(),
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
    """加载基金预设配置"""
    try:
        if not PRESET_FILE.exists():
            return {}
        data = json.loads(PRESET_FILE.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            return {}
        return {
            sanitize_code(code): parsed
            for code, item in data.items()
            if (parsed := _sanitize_preset_item(item))
        }
    except Exception:
        return {}


def save_fund_presets(presets: Dict) -> Tuple[bool, str]:
    """保存基金预设配置"""
    try:
        cleaned = {
            sanitize_code(code): parsed
            for code, item in (presets or {}).items()
            if (parsed := _sanitize_preset_item(item))
        }
        PRESET_FILE.write_text(
            json.dumps(cleaned, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        return True, ''
    except Exception as e:
        return False, str(e)


# ==================== 以下为持仓档案相关函数（已大量简化） ====================

def load_holdings_archive_text() -> str:
    """加载持仓档案文本"""
    try:
        if not HOLDINGS_ARCHIVE_FILE.exists():
            return ''
        data = json.loads(HOLDINGS_ARCHIVE_FILE.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            return str(data.get('base_text', '') or '')
        return str(data or '')
    except Exception:
        return ''


def save_holdings_archive_text(base_text: str) -> Tuple[bool, str]:
    """保存持仓档案文本"""
    try:
        payload = {
            'base_text': str(base_text or ''),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        HOLDINGS_ARCHIVE_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        return True, ''
    except Exception as e:
        return False, str(e)


def clear_holdings_archive_text() -> Tuple[bool, str]:
    """清空持仓档案"""
    try:
        if HOLDINGS_ARCHIVE_FILE.exists():
            HOLDINGS_ARCHIVE_FILE.unlink()
        return True, ''
    except Exception as e:
        return False, str(e)


def rows_to_holdings_text(rows: List[Dict]) -> str:
    """将标准化后的持仓行转为文本格式"""
    lines = []
    for item in normalize_position_table(rows):
        code = item['基金代码']
        cost_nav = item['持仓成本净值']
        principal = item['投资成本']
        pnl = item.get('目前盈亏情况', '').strip()
        base = f"{code}:{cost_nav}:{principal}"
        if pnl:
            base += f":{pnl}"
        lines.append(base)
    return "\n".join(lines)


# 其他函数（如 build_position_xxx）如果暂时不改，可以先保持原样
# 我会在下一批继续帮你优化 decision_engine 和 app.py 中的调用部分

print("portfolio_io.py 优化版本加载完成")