"""
全球電商平台 PSU 爬蟲 — 通用品牌偵測工具
"""

import re
from typing import Optional

# 所有目標品牌的別名映射（品牌名 → 標準名）
BRAND_ALIASES: dict[str, str] = {
    # ASUS 華碩
    "asus": "華碩（ASUS）", "asus rog": "華碩（ASUS）",
    # GIGABYTE 技嘉
    "gigabyte": "技嘉（GIGABYTE）", "giga byte": "技嘉（GIGABYTE）",
    # MSI 微星
    "msi": "微星（MSI）",
    # Corsair 海盜船
    "corsair": "海盜船（Corsair）",
    # Seasonic 海韻
    "seasonic": "海韻（Seasonic）",
    # Antec 安鈦克
    "antec": "安鈦克（Antec）",
    # Cooler Master 酷冷至尊
    "cooler master": "酷冷至尊（Cooler Master）",
    "coolermaster": "酷冷至尊（Cooler Master）",
    # BQT
    "bqt": "BQT",
    # DeepCool 九州風神
    "deepcool": "九州風神（DeepCool）",
    # Lian Li 聯力
    "lian li": "聯力（Lian Li）", "lianli": "聯力（Lian Li）",
}

# 常見 PSU 關鍵字
PSU_KEYWORDS = {
    "en": ["power supply", "psu", "atx power supply", "computer power supply",
           "modular power supply", "smps", "750w", "850w", "650w", "1000w"],
    "zh": ["電源", "電源供應器", "pc電源", "atx電源", "電腦電源"],
    "ja": ["電源ユニット", "パワーサプライ", "ATX電源", "PC電源"],
    "ko": ["파워서플라이", "PC전원", "ATX파워", "컴퓨터 파워"],
    "ru": ["блок питания", "бп", "атх блок питания"],
    "de": ["netzteil", "pc netzteil", "atx netzteil", "7800", "850w"],
    "es": ["fuente de alimentacion", "psu", "atx", "fuente pc"],
    "ar": ["مزود الطاقة", "بور سبلاي", "وحدة امداد الطاقة"],
}

# 工廠函數：根據名稱創建標準品牌的別名字典（給各爬蟲用）
def build_brand_map(brands: list[dict]) -> dict[str, str]:
    """從 config 中的品牌列表構建別名映射"""
    aliases = {}
    for b in brands:
        canonical = b["name"]
        aliases[b["name"].lower()] = canonical
        for alias in b.get("aliases", []):
            aliases[alias.lower()] = canonical
    return aliases


def detect_brand(text: str, brand_map: dict[str, str]) -> Optional[str]:
    """在文本中偵測目標品牌（大小寫不敏感）"""
    text_lower = text.lower()
    for alias, canonical in brand_map.items():
        if alias in text_lower:
            return canonical
    return None


def extract_wattage(text: str) -> Optional[str]:
    """從文字中提取瓦數（如 750W, 850W, 1000W）"""
    patterns = [
        r'(\d{3,4})\s*[Ww]',           # 750W, 850 W
        r'(\d{3,4})\s*龍\s*瓦',          # 850龍瓦
        r'(\d{3,4})\s*W\s*[Tt]itanium', # 1000W Titanium
        r'[Ww]att[:\s]*(\d{3,4})',       # 750 Watt / 850W
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1) + "W"
    return None


def extract_certification(text: str) -> Optional[str]:
    """提取 80 Plus 認證等級"""
    cert_map = {
        "titanium": "80+ Titanium",
        "platinum": "80+ Platinum",
        "gold": "80+ Gold",
        "silver": "80+ Silver",
        "bronze": "80+ Bronze",
    }
    text_lower = text.lower()
    for key, cert in cert_map.items():
        if key in text_lower:
            # 避免匹配 "Gold" 這類非認證詞
            if re.search(rf'\+?\s*{key}\s*(plus|titanium|platinum|silver|bronze)?', text_lower):
                return cert
            if key in ["gold", "silver", "bronze"]:
                # 更嚴格匹配
                if re.search(rf'(80\s*plus\s*{key}|{key}\s*80\s*plus)', text_lower):
                    return cert
    return None


def extract_rating(text: str) -> Optional[str]:
    """提取評分（如 4.5/5, 92%）"""
    m = re.search(r'([0-9.]+)\s*[\/\★⭐]\s*5', text)
    if m:
        return m.group(1)
    m = re.search(r'([0-9]+)\s*%', text)
    if m:
        score = int(m.group(1))
        if score <= 100:
            return str(score / 20)  # 轉為 5 分制
    return None


def clean_html(text: str) -> str:
    """清除 HTML 標籤"""
    return re.sub(r'<[^>]+>', "", text).strip()


def normalize_price(price_str: str) -> Optional[float]:
    """將價格字串標準化為數字"""
    if not price_str:
        return None
    text = re.sub(r'[^\d.,]', '', str(price_str))
    text = text.replace(',', '')
    try:
        return float(text)
    except ValueError:
        return None


def convert_currency(amount: float, from_currency: str) -> float:
    """將價格轉換為 USD（大致估算）"""
    rates = {
        "USD": 1.0, "CNY": 0.14, "JPY": 0.0067, "KRW": 0.00074,
        "EUR": 1.08, "GBP": 1.27, "RUB": 0.011, "INR": 0.012,
        "BRL": 0.20, "CAD": 0.74, "AUD": 0.65, "TWD": 0.031,
        "THB": 0.029, "SGD": 0.75, "MYR": 0.22, "PHP": 0.018,
        "IDR": 0.000063, "VND": 0.00004, "AED": 0.27,
        "SAR": 0.27, "EGP": 0.021, "TRY": 0.030,
    }
    rate = rates.get(from_currency.upper(), 1.0)
    return amount * rate
