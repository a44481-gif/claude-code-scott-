"""
亞洲/南美/中東電商 Playwright 爬蟲
覆蓋：Coupang, Mercado Libre, Noon, Lazada, Tokopedia, Rakuten
"""

import logging
from .playwright_base import PlaywrightCrawler, PlaywrightConfig

logger = logging.getLogger(__name__)


# ── 韓國 ─────────────────────────────────────────────────────────

class CoupangPlaywright(PlaywrightCrawler):
    """Coupang — 韓國最大電商（有強反爬）"""
    platform_name = "Coupang"
    REGION = "亞洲"
    currency = "KRW"

    SELECTORS = {
        "item": "li.search-product, .searchProductList li",
        "name": ".search-product__name, .product-item-name a",
        "price": ".price-section .price, .product-item-price strong",
        "url": "a[href*='/products/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.coupang.com/np/search?q={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="ko-KR",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class GmarketPlaywright(PlaywrightCrawler):
    """Gmarket — 韓國最大電商"""
    platform_name = "Gmarket"
    REGION = "亞洲"
    currency = "KRW"

    SELECTORS = {
        "item": ".box__component-itemcard, .itemList_area .item",
        "name": ".txt__item, .box__component-itemcard .txt__item",
        "price": ".price__current, strong.price",
        "url": "a[href*='/goods/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.gmarket.co.kr/n/search?keyword={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="ko-KR",
            scroll_pages=1,
            delay_between_scrolls=1.5,
        ))


# ── 日本 ─────────────────────────────────────────────────────────

class RakutenPlaywright(PlaywrightCrawler):
    """Rakuten — 日本最大電商平台"""
    platform_name = "Rakuten"
    REGION = "亞洲"
    currency = "JPY"

    SELECTORS = {
        "item": ".searchresultitem, .dui3N2Xq, [class*='searchresultitem']",
        "name": ".item-name a, a[item-name], .dui3N2Xq a[href*='/products/']",
        "price": ".price, .item-price, strong.price",
        "url": "a[href*='/products/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "+")
        return f"https://search.rakuten.co.jp/search/mall/{q}/?size=30&p={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="ja-JP",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


# ── 南美 ─────────────────────────────────────────────────────────

class MercadoLibreARPlaywright(PlaywrightCrawler):
    """Mercado Libre Argentina"""
    platform_name = "Mercado Libre AR"
    REGION = "南美"
    currency = "ARS"

    SELECTORS = {
        "item": ".ui-card-padding, .poly-component__wrapper",
        "name": ".poly-component__title a, .ui-card .title",
        "price": ".poly-component__price div, .price-tag .price-tag-ui",
        "url": "a[href*='/p/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.mercadolibre.com.ar/search?q={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="es-AR",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class MercadoLibreBRPlaywright(PlaywrightCrawler):
    """Mercado Livre Brasil"""
    platform_name = "Mercado Livre BR"
    REGION = "南美"
    currency = "BRL"

    SELECTORS = {
        "item": ".ui-card-padding, .poly-component__wrapper",
        "name": ".poly-component__title a, .ui-card .title",
        "price": ".poly-component__price div, .price-tag .price-tag-ui",
        "url": "a[href*='/p/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.mercadolivre.com.br/search?q={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="pt-BR",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class MercadoLibreMXPlaywright(PlaywrightCrawler):
    """Mercado Libre México"""
    platform_name = "Mercado Libre MX"
    REGION = "南美"
    currency = "MXN"

    SELECTORS = {
        "item": ".ui-card-padding, .poly-component__wrapper",
        "name": ".poly-component__title a",
        "price": ".poly-component__price div",
        "url": "a[href*='/p/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.mercadolibre.com.mx/search?q={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="es-MX",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


# ── 中東 ─────────────────────────────────────────────────────────

class NoonPlaywright(PlaywrightCrawler):
    """Noon.com — 中東最大電商"""
    platform_name = "Noon"
    REGION = "中東"
    currency = "SAR"

    SELECTORS = {
        "item": ".productWidget, [class*='product'], .noon也想",
        "name": "h3.productName, [class*='productName'], .product-title a",
        "price": "[class*='price'], .price-tag, span.amount",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.noon.com/saudi-en/search/?q={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="en-AE",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


# ── Lazada ────────────────────────────────────────────────────────

class LazadaTHPlaywright(PlaywrightCrawler):
    """Lazada Thailand"""
    platform_name = "Lazada TH"
    REGION = "東南亞"
    currency = "THB"

    SELECTORS = {
        "item": ".catalog_product_item, [class*='productCard'], .pmanItem",
        "name": ".productCardTitle a, .pmanItem a[name*='title']",
        "price": ".productPrice, .pmanItem .price",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.lazada.co.th/catalog/?q={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="th-TH",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class LazadaVNPlaywright(PlaywrightCrawler):
    """Lazada Vietnam"""
    platform_name = "Lazada VN"
    REGION = "東南亞"
    currency = "VND"

    SELECTORS = {
        "item": ".catalog_product_item, [class*='productCard'], .pmanItem",
        "name": ".productCardTitle a, .pmanItem a",
        "price": ".productPrice, .pmanItem .price",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.lazada.vn/catalog/?q={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="vi-VN",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class LazadaIDPlaywright(PlaywrightCrawler):
    """Lazada Indonesia"""
    platform_name = "Lazada ID"
    REGION = "東南亞"
    currency = "IDR"

    SELECTORS = {
        "item": ".catalog_product_item, [class*='productCard'], .pmanItem",
        "name": ".productCardTitle a",
        "price": ".productPrice",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.lazada.co.id/catalog/?q={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="id-ID",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class LazadaMYPlaywright(PlaywrightCrawler):
    """Lazada Malaysia"""
    platform_name = "Lazada MY"
    REGION = "東南亞"
    currency = "MYR"

    SELECTORS = {
        "item": ".catalog_product_item, [class*='productCard'], .pmanItem",
        "name": ".productCardTitle a",
        "price": ".productPrice",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.lazada.com.my/catalog/?q={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="en-MY",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


# ── Tokopedia ─────────────────────────────────────────────────────

class TokopediaPlaywright(PlaywrightCrawler):
    """Tokopedia — 印尼最大電商"""
    platform_name = "Tokopedia"
    REGION = "東南亞"
    currency = "IDR"

    SELECTORS = {
        "item": "[data-testid='product-card'], .catalogProductListItem",
        "name": "[data-testid='product-name'], .catalogProductListItem a",
        "price": "[data-testid='product-price'], .catalogProductListItem .price",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.tokopedia.com/search?page={page}&q={q}&st=product"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="id-ID",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))
