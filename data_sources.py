# data_sources.py
from typing import Dict, Tuple, Optional
import re
import pandas as pd
import time
import requests

from config import *
from utils import safe_float
from calibration_io import build_calibration_profile


def http_get(url: str, **kwargs):
    """带重试的 HTTP 请求"""
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://fund.eastmoney.com/',
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    }
    timeout = kwargs.pop('timeout', REQUEST_TIMEOUT)
    
    for i in range(4):
        try:
            r = SESSION.get(url, headers=headers, timeout=timeout, **kwargs)
            r.raise_for_status()
            return r
        except Exception:
            time.sleep(0.8 * (i + 1))
    
    r = requests.get(url, headers=headers, timeout=timeout, **kwargs)
    r.raise_for_status()
    return r


# ====================== 估值相关 ======================
def apply_estimate_calibration(code: str, estimate_payload: Dict) -> Dict:
    """应用估值校准"""
    data = dict(estimate_payload or {})
    if not data or not data.get('estimate_ok'):
        return data

    calibration = build_calibration_profile(code)
    if not calibration:
        data['estimate_calibrated'] = False
        return data

    try:
        unit_nav = float(data.get('unit_nav') or 0)
        estimate_rate = float(data.get('estimate_rate') or 0)
        multiplier = float(calibration.get('rate_multiplier') or 1.0)
        max_abs_add = float(calibration.get('max_abs_add') or 0.0)

        adjusted_rate = estimate_rate * multiplier
        if max_abs_add > 0:
            adjusted_rate = estimate_rate + max(-max_abs_add, min(max_abs_add, adjusted_rate - estimate_rate))

        adjusted_nav = unit_nav * (1.0 + adjusted_rate) if unit_nav > 0 else float(data.get('estimate_nav') or 0)

        data.update({
            'raw_estimate_rate': estimate_rate,
            'estimate_rate': adjusted_rate,
            'estimate_nav': adjusted_nav,
            'estimate_calibrated': True,
            'estimate_calibration_note': str(calibration.get('note', '')),
        })
        return data
    except Exception:
        data['estimate_calibrated'] = False
        return data


def get_estimate(code: str) -> Dict:
    """获取盘中估值"""
    for base_url in ['http://fundgz.1234567.com.cn/js/', 'https://fundgz.1234567.com.cn/js/']:
        try:
            r = http_get(f"{base_url}{code}.js")
            m = re.search(r'jsonpgz\((.*)\)', r.text.strip())
            if m:
                d = eval(m.group(1))
                payload = {
                    'code': d.get('fundcode', code),
                    'name': d.get('name', code),
                    'unit_nav': float(d.get('dwjz') or 0),
                    'estimate_nav': float(d.get('gsz') or 0),
                    'estimate_rate': float(d.get('gszzl') or 0) / 100,
                    'estimate_time': d.get('gztime', ''),
                    'estimate_ok': True
                }
                return apply_estimate_calibration(code, payload)
        except Exception:
            continue
    raise ValueError(f"无法获取 {code} 的估值数据")


def get_fund_history(code: str) -> pd.DataFrame:
    """获取基金历史净值"""
    try:
        r = http_get(
            'https://fundmobapi.eastmoney.com/FundMNewApi/FundMNHisNetList',
            params={
                'FCODE': code,
                'pageIndex': 1,
                'pageSize': 1000,
                'plat': 'Android',
                'appType': 'ttjj'
            }
        )
        rows = (r.json() or {}).get('Datas') or []
        df = pd.DataFrame([
            {'date': x.get('FSRQ'), 'nav': float(x.get('DWJZ'))}
            for x in rows if x.get('FSRQ') and x.get('DWJZ')
        ])
        if df.empty:
            raise ValueError('历史净值为空')
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date').drop_duplicates('date').tail(LOOKBACK).reset_index(drop=True)
    except Exception as e:
        raise ValueError(f"获取 {code} 历史净值失败: {e}")


print("✅ data_sources.py 优化版加载完成")