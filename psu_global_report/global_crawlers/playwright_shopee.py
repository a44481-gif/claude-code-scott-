"""
Shopee 系列 Playwright 爬蟲
覆蓋：泰國/越南/印尼/馬來西亞/菲律賓
Shopee 使用 JavaScript 渲染，HTTP 請求無法獲取完整數據
"""

import logging
from .playwright_base import PlaywrightCrawler, PlaywrightConfig

logger = logging.getLogger(__name__)


class ShopeeTH(PlaywrightCrawler):
    """Shopee Thailand"""
    platform_name = "Shopee TH"
    REGION = "東南亞"
    currency = "THB"

    SELECTORS = {
        "item": "[data-sqe='item'], .shopee-item-card, [class*='item-card']",
        "name": "[class*='product-name'], [class*='item-name'], .CveXj",
        "price": "[class*='price'], .WTFdWs",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        # Shopee 頁碼從 0 開始
        q = keyword.replace(" ", "%20")
        return f"https://shopee.co.th/search?keyword={q}&page={page - 1}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="th-TH",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class ShopeeVN(PlaywrightCrawler):
    """Shopee Vietnam"""
    platform_name = "Shopee VN"
    REGION = "東南亞"
    currency = "VND"

    SELECTORS = {
        "item": "[data-sqe='item'], .shopee-item-card",
        "name": "[class*='product-name'], .CveXj",
        "price": "[class*='price']",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://shopee.vn/search?keyword={q}&page={page - 1}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="vi-VN",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class ShopeeID(PlaywrightCrawler):
    """Shopee Indonesia"""
    platform_name = "Shopee ID"
    REGION = "東南亞"
    currency = "IDR"

    SELECTORS = {
        "item": "[data-sqe='item'], .shopee-item-card",
        "name": "[class*='product-name'], .CveXj",
        "price": "[class*='price']",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://shopee.co.id/search?keyword={q}&page={page - 1}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="id-ID",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class ShopeeMY(PlaywrightCrawler):
    """Shopee Malaysia"""
    platform_name = "Shopee MY"
    REGION = "東南亞"
    currency = "MYR"

    SELECTORS = {
        "item": "[data-sqe='item'], .shopee-item-card",
        "name": "[class*='product-name'], .CveXj",
        "price": "[class*='price']",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://shopee.com.my/search?keyword={q}&page={page - 1}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="en-MY",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class ShopeePH(PlaywrightCrawler):
    """Shopee Philippines"""
    platform_name = "Shopee PH"
    REGION = "東南亞"
    currency = "PHP"

    SELECTORS = {
        "item": "[data-sqe='item'], .shopee-item-card",
        "name": "[class*='product-name'], .CveXj",
        "price": "[class*='price']",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://shopee.ph/search?keyword={q}&page={page - 1}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="en-PH",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))
