# config.py
import json
import math
import os
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ====================== 风格与基准配置 ======================
STYLE_BENCH = {
    'balanced': '000300.SH',
    'growth': '399006.SZ',
    'cyclical': '000985.SH',
    'defensive': '000300.SH',
    'qdii_us': 'NDX100.GLB',
    'qdii_global': 'WORLD.GLB',
    'qdii_hk': 'HSI.GLB',
    'qdii_japan': 'N225.GLB',
    'qdii_gold': 'GOLD.GLB',
}

STYLE_CFG = {
    'balanced': {
        'label': '平衡型',
        'w': (0.50, 0.30, 0.20),
        'buy': (10, 20, 35),
        'sell': (90, 80, 65),
        'dev': (4.0, 2.0, 1.0),
        'th': (2.2, 0.8, -0.8, -2.2)
    },
    'growth': {
        'label': '成长科技型',
        'w': (0.35, 0.35, 0.30),
        'buy': (8, 18, 30),
        'sell': (92, 82, 70),
        'dev': (6.0, 3.5, 1.5),
        'th': (2.4, 1.0, -1.0, -2.4)
    },
    'cyclical': {
        'label': '资源周期型',
        'w': (0.25, 0.35, 0.40),
        'buy': (12, 22, 35),
        'sell': (88, 78, 65),
        'dev': (7.0, 4.0, 2.0),
        'th': (2.2, 0.8, -0.8, -2.2)
    },
    'defensive': {
        'label': '低波稳健型',
        'w': (0.55, 0.30, 0.15),
        'buy': (15, 25, 40),
        'sell': (85, 75, 60),
        'dev': (3.0, 1.8, 0.8),
        'th': (2.0, 0.7, -0.7, -2.0)
    },
    # QDII 风格配置
    'qdii_us': {'label': 'QDII-美股宽基', 'w': (0.35, 0.35, 0.30), 'buy': (8, 18, 30), 'sell': (92, 82, 70), 'dev': (6.0, 3.5, 1.5), 'th': (2.0, 0.8, -0.8, -2.0)},
    'qdii_global': {'label': 'QDII-全球股票', 'w': (0.45, 0.30, 0.25), 'buy': (10, 20, 34), 'sell': (90, 80, 66), 'dev': (5.0, 3.0, 1.4), 'th': (1.9, 0.7, -0.7, -1.9)},
    'qdii_hk': {'label': 'QDII-港股/中概', 'w': (0.30, 0.35, 0.35), 'buy': (10, 20, 34), 'sell': (90, 80, 66), 'dev': (6.2, 3.6, 1.8), 'th': (2.1, 0.8, -0.8, -2.1)},
    'qdii_japan': {'label': 'QDII-日本市场', 'w': (0.40, 0.35, 0.25), 'buy': (10, 20, 34), 'sell': (90, 80, 66), 'dev': (5.0, 2.8, 1.3), 'th': (1.9, 0.7, -0.7, -1.9)},
    'qdii_gold': {'label': 'QDII-黄金/商品', 'w': (0.25, 0.30, 0.45), 'buy': (12, 24, 38), 'sell': (88, 76, 62), 'dev': (5.5, 3.2, 1.5), 'th': (1.8, 0.7, -0.7, -1.8)},
}

# ====================== 策略引擎配置 ======================
A_SHARE_ENGINE_CFG = {
    'auto_engine': {'label': '自动跟随风格', 'quality': 1.0, 'stability': 1.0, 'risk': 1.0, 'active': 1.0, 'heat': 1.0, 'regime': 1.0},
    'broad_index': {'label': '宽基指数', 'quality': 0.90, 'stability': 0.95, 'risk': 1.00, 'active': 0.45, 'heat': 0.60, 'regime': 0.95},
    'industry_theme': {'label': '行业主题', 'quality': 0.78, 'stability': 0.78, 'risk': 0.92, 'active': 0.55, 'heat': 1.30, 'regime': 1.05},
    'active_equity': {'label': '主动权益', 'quality': 1.00, 'stability': 1.00, 'risk': 0.95, 'active': 1.18, 'heat': 0.80, 'regime': 0.88},
    'dividend_lowvol': {'label': '红利低波', 'quality': 0.98, 'stability': 1.12, 'risk': 1.18, 'active': 0.55, 'heat': 0.55, 'regime': 0.72},
    'qdii_generic': {'label': 'QDII通用', 'quality': 0.95, 'stability': 0.95, 'risk': 1.00, 'active': 0.80, 'heat': 0.85, 'regime': 0.90},
}

A_SHARE_ENGINE_DEFAULT_BY_STYLE = {
    'balanced': 'broad_index',
    'growth': 'industry_theme',
    'cyclical': 'industry_theme',
    'defensive': 'dividend_lowvol',
    'qdii_us': 'qdii_generic',
    'qdii_global': 'qdii_generic',
    'qdii_hk': 'qdii_generic',
    'qdii_japan': 'qdii_generic',
    'qdii_gold': 'qdii_generic',
}

# ====================== QDII 元数据 ======================
QDII_STYLE_META = {
    'qdii_us': {
        'market': '美股',
        'settle': '通常按上一海外交易日信号看待，确认节奏常见 T+2',
        'fx_symbol': 'USDCNY=X',
        'fx_label': '美元/人民币',
        'signal_note': '盘中估值参考意义弱于 A 股基金，建议更偏观察/分批。'
    },
    'qdii_global': {
        'market': '全球股票',
        'settle': '多市场混合，确认节奏常见 T+2',
        'fx_symbol': 'USDCNY=X',
        'fx_label': '美元/人民币',
        'signal_note': '全球市场与汇率共同影响净值，短线动作应更克制。'
    },
    # 其他 QDII 风格可继续补充...
}

# ====================== 基准配置 ======================
BENCHMARKS = {
    '000300.SH': ('沪深300', '1.000300'),
    '000905.SH': ('中证500', '1.000905'),
    '000985.SH': ('中证全指', '1.000985'),
    '000852.SH': ('中证1000', '1.000852'),
    '399006.SZ': ('创业板指', '0.399006'),
    'NDX100.GLB': ('纳斯达克100', 'Y:^NDX'),
    'SP500.GLB': ('标普500', 'Y:^GSPC'),
    'HSI.GLB': ('恒生指数', 'Y:^HSI'),
    'N225.GLB': ('日经225', 'Y:^N225'),
    'WORLD.GLB': ('MSCI World', 'Y:URTH'),
    'GOLD.GLB': ('黄金', 'Y:GLD'),
}

# ====================== 建议相关配置 ======================
ADVICE_ORDER = ['减仓卖', '分批卖', '观望', '分批买', '轻仓买']

# ====================== 文件路径配置 ======================
PRESET_FILE = Path(__file__).parent / 'fund_style_benchmark_presets.json'
HOLDINGS_ARCHIVE_FILE = Path(__file__).parent / 'fund_holdings_archive.json'
RATE_UPDATE_FILE = Path(__file__).parent / 'fund_daily_rate_updates.json'
CALIBRATION_FEEDBACK_FILE = Path(__file__).parent / 'fund_estimate_calibration_feedback.json'

# ====================== 网络请求配置 ======================
SESSION = requests.Session()
SESSION.mount('http://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.8)))
SESSION.mount('https://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.8)))
REQUEST_TIMEOUT = (8, 20)

# ====================== 辅助函数 ======================
clamp = lambda x, a, b: max(a, min(b, x))
pctx = lambda x, d=2: '--' if x is None or pd.isna(x) else f'{x*100:.{d}f}%'
numx = lambda x, d=2: '--' if x is None or pd.isna(x) else f'{x:.{d}f}'
signed_pct = lambda x, d=2: '--' if x is None or pd.isna(x) else f'{x*100:+.{d}f}%'
signed_num = lambda x, d=4: '--' if x is None or pd.isna(x) else f'{x:+.{d}f}'

def sanitize_code(code: Any) -> str:
    return str(code or '').strip()

print("config.py 优化版本加载完成")