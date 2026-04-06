"""
全球電商平台爬蟲 — 統一入口
一次性實例化所有平台爬蟲
"""

from .base_crawler import GlobalBaseCrawler, ProductInfo

# ── 北美 ──
from .north_america import (
    AmazonUS, NeweggCrawler, BestBuyUS,
    AmazonCanada, BestBuyCanada,
)

# ── 歐洲 ──
from .europe import AmazonDE, AmazonUK, MediaMarkt, Saturn

# ── 俄羅斯 ──
from .russia import Ozon, Wildberries, YandexMarket

# ── 中國 ──
from .china import JDGlobal, TmallGlobal, Taobao

# ── 台灣 ──
from .taiwan import PChome, Momo

# ── 東亞/南亞 ──
from .asia_east import AmazonJP, Rakuten, Gmarket, Coupang, Flipkart, AmazonIN

# ── 東南亞 ──
from .asia_southeast import (
    ShopeeTH, ShopeeVN, ShopeeID, ShopeeMY, ShopeePH,
    LazadaTH, LazadaVN, LazadaID, LazadaMY,
    Tokopedia,
)

# ── 南美 ──
from .latam import MercadoLibreAR, MercadoLibreBR, MercadoLibreMX

# ── 中東 ──
from .middle_east import Noon, AmazonSAE


# ── 所有爬蟲註冊表 ──
# 格式：(爬蟲類, 關鍵字列表, 優先級, 備註)
# 優先級: 1=直接HTTP可抓, 2=可能需Playwright, 3=需API/登入

CRAWLER_REGISTRY: list[tuple] = [
    # 北美 (1)
    (AmazonUS,       ["power supply unit", "PSU", "ATX power supply", "computer power supply"], 1, ""),
    (NeweggCrawler,  ["power supply", "PSU", "ATX", "computer power supply"], 1, ""),
    (BestBuyUS,      ["power supply", "PSU", "computer power supply"], 1, ""),
    (AmazonCanada,   ["power supply unit", "PSU", "ATX power supply"], 1, ""),
    (BestBuyCanada,  ["power supply", "PSU", "computer power supply"], 1, ""),

    # 歐洲 (1)
    (AmazonDE,       ["Netzteil", "PC Netzteil", "ATX Netzteil", "750W", "850W"], 1, "德語關鍵字"),
    (AmazonUK,       ["power supply unit", "PSU", "ATX power supply"], 1, ""),
    (MediaMarkt,     ["Netzteil", "PC Netzteil"], 2, "需JS渲染"),
    (Saturn,         ["Netzteil", "PC Netzteil"], 2, "需JS渲染"),

    # 俄羅斯 (2-3)
    (Ozon,           ["блок питания", "PSU", "атх блок питания"], 2, "需Playwright或API"),
    (Wildberries,    ["блок питания", "PSU", "атх"], 3, "需登入/Playwright"),
    (YandexMarket,   ["блок питания", "PSU", "компьютерный блок питания"], 2, "需JS渲染"),

    # 中國 (1)
    (JDGlobal,       ["電源供應器", "PC電源", "ATX電源", "電腦電源"], 1, ""),
    (TmallGlobal,    ["電源供應器", "電腦電源", "ATX"], 1, ""),
    (Taobao,         ["電源供應器", "電腦電源"], 1, ""),

    # 台灣 (1)
    (PChome,         ["電源供應器", "PC電源", "電腦電源", "PSU"], 1, ""),
    (Momo,           ["電源供應器", "PSU", "電腦電源"], 1, ""),

    # 日本 (1)
    (AmazonJP,       ["電源ユニット", "パワーサプライ", "ATX電源", "PC電源"], 1, "日語關鍵字"),
    (Rakuten,        ["電源ユニット", "ATX", "PC電源"], 2, "需登入/Playwright"),

    # 韓國 (2)
    (Gmarket,        ["파워서플라이", "PC전원", "ATX파워"], 2, "需韓文Cookie"),
    (Coupang,        ["파워서플라이", "컴퓨터 파워", "PSU"], 2, "需Playwright"),

    # 印度 (1)
    (Flipkart,       ["power supply", "PSU", "computer power supply", "SMPS"], 1, ""),
    (AmazonIN,       ["power supply unit", "PSU", "SMPS", "ATX power supply"], 1, ""),

    # 東南亞 (2)
    (ShopeeTH,       ["power supply", "PSU", "อุปกรณ์จ่ายไฟ"], 2, "需JS渲染"),
    (ShopeeVN,       ["nguồn máy tính", "PSU", "bộ nguồn"], 2, "需JS渲染"),
    (ShopeeID,       ["power supply", "PSU", "catu daya"], 2, "需JS渲染"),
    (ShopeeMY,       ["power supply", "PSU", "computer power supply"], 2, "需JS渲染"),
    (ShopeePH,       ["power supply", "PSU", "computer power supply"], 2, "需JS渲染"),
    (LazadaTH,       ["power supply", "PSU"], 2, "需JS渲染"),
    (LazadaVN,       ["nguồn máy tính", "PSU"], 2, "需JS渲染"),
    (LazadaID,       ["power supply", "PSU"], 2, "需JS渲染"),
    (LazadaMY,       ["power supply", "PSU"], 2, "需JS渲染"),
    (Tokopedia,      ["power supply", "PSU", "catu daya"], 2, "需JS渲染"),

    # 南美 (2)
    (MercadoLibreAR, ["fuente de alimentacion", "PSU", "atx", "fuente pc"], 2, "需JS渲染"),
    (MercadoLibreBR, ["fonte de alimentacao", "PSU", "fonte atx", "fonte pc"], 2, "需JS渲染"),
    (MercadoLibreMX, ["fuente de alimentacion", "PSU", "atx", "fuente pc"], 2, "需JS渲染"),

    # 中東 (2)
    (Noon,           ["power supply", "PSU", "computer power supply"], 2, "需JS渲染"),
    (AmazonSAE,      ["power supply", "PSU", "computer power supply"], 1, ""),
]


def get_all_crawlers(config: dict) -> list[GlobalBaseCrawler]:
    """根據配置創建所有爬蟲實例"""
    crawlers = []
    for (crawler_cls, *_) in CRAWLER_REGISTRY:
        try:
            crawlers.append(crawler_cls(config))
        except Exception as e:
            import logging
            logging.warning(f"無法創建爬蟲 {crawler_cls.__name__}: {e}")
    return crawlers


def get_primary_crawlers(config: dict) -> list[GlobalBaseCrawler]:
    """只返回優先級=1（可直接HTTP抓取）的爬蟲"""
    crawlers = []
    for (crawler_cls, kw, priority, _) in CRAWLER_REGISTRY:
        if priority == 1:
            try:
                crawlers.append(crawler_cls(config))
            except Exception:
                pass
    return crawlers


__all__ = [
    "GlobalBaseCrawler",
    "ProductInfo",
    "CRAWLER_REGISTRY",
    "get_all_crawlers",
    "get_primary_crawlers",
    # 各平台爬蟲
    "AmazonUS", "NeweggCrawler", "BestBuyUS", "AmazonCanada", "BestBuyCanada",
    "AmazonDE", "AmazonUK", "MediaMarkt", "Saturn",
    "Ozon", "Wildberries", "YandexMarket",
    "JDGlobal", "TmallGlobal", "Taobao",
    "PChome", "Momo",
    "AmazonJP", "Rakuten",
    "Gmarket", "Coupang",
    "Flipkart", "AmazonIN",
    "ShopeeTH", "ShopeeVN", "ShopeeID", "ShopeeMY", "ShopeePH",
    "LazadaTH", "LazadaVN", "LazadaID", "LazadaMY",
    "Tokopedia",
    "MercadoLibreAR", "MercadoLibreBR", "MercadoLibreMX",
    "Noon", "AmazonSAE",
]
