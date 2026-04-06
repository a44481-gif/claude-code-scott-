"""
東南亞電商平台爬蟲
- Shopee (泰國/越南/印尼/馬來西亞/菲律賓/新加坡)
- Lazada (泰國/越南/印尼/馬來西亞/菲律賓/新加坡)
- Tokopedia (印尼)
- 其他: 京東/天貓/淘寶 (見 china.py)
"""

import re
import logging
from .base_crawler import GlobalBaseCrawler
from .brand_utils import detect_brand, clean_html

logger = logging.getLogger(__name__)


class ShopeeBase(GlobalBaseCrawler):
    """
    Shopee (東南亞龍頭電商)
    Shopee 有多國站點，此為基礎類別
    实际使用時建議透過官方 API 或 Playwright
    """
    REGION = "東南亞"

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        # Shopee 商品卡片 (HTML 渲染)
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*shopee-item-card[^"]*"[^>]*>(.*?)</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<div[^>]*class="[^"]*item-name[^"]*"[^>]*>(.*?)</div>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="[^"]*price[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                price_str = clean_html(price_m.group(1)) if price_m else None
                price = re.sub(r'[^\d.]', '', price_str) if price_str else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency=self.currency
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Shopee] 解析失敗: {e}")

        if len(products) < 3:
            logger.warning(
                f"[{self.platform_name}] ⚠️ HTML 解析結果過少，"
                "Shopee 需要 JavaScript 渲染，建議使用 Playwright"
            )
        return products


class ShopeeTH(ShopeeBase):
    """Shopee Thailand (泰國)"""
    platform_name = "Shopee TH"
    currency = "THB"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://shopee.co.th/search?keyword={q}&page={page - 1}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "th-TH,th;q=0.9"
        return h


class ShopeeVN(ShopeeBase):
    """Shopee Vietnam (越南)"""
    platform_name = "Shopee VN"
    currency = "VND"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://shopee.vn/search?keyword={q}&page={page - 1}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "vi-VN,vi;q=0.9"
        return h


class ShopeeID(ShopeeBase):
    """Shopee Indonesia (印尼)"""
    platform_name = "Shopee ID"
    currency = "IDR"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://shopee.co.id/search?keyword={q}&page={page - 1}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "id-ID,id;q=0.9"
        return h


class ShopeeMY(ShopeeBase):
    """Shopee Malaysia (馬來西亞)"""
    platform_name = "Shopee MY"
    currency = "MYR"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://shopee.com.my/search?keyword={q}&page={page - 1}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "ms-MY,ms;q=0.9"
        return h


class ShopeePH(ShopeeBase):
    """Shopee Philippines (菲律賓)"""
    platform_name = "Shopee PH"
    currency = "PHP"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://shopee.ph/search?keyword={q}&page={page - 1}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "en-PH,en;q=0.9"
        return h


class LazadaBase(GlobalBaseCrawler):
    """Lazada (東南亞電商，與 Shopee 類似)"""
    REGION = "東南亞"

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*productCard[^"]*"[^>]*>(.*?)</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<div[^>]*class="[^"]*productName[^"]*"[^>]*>(.*?)</div>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="[^"]*price[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                price_str = clean_html(price_m.group(1)) if price_m else None
                price = re.sub(r'[^\d.]', '', price_str) if price_str else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency=self.currency
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Lazada] 解析失敗: {e}")

        if len(products) < 3:
            logger.warning(
                f"[{self.platform_name}] ⚠️ HTML 解析結果過少，"
                "建議使用 Playwright"
            )
        return products


class LazadaTH(LazadaBase):
    platform_name = "Lazada TH"
    currency = "THB"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.lazada.co.th/catalog/?q={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "th-TH,th;q=0.9"
        return h


class LazadaVN(LazadaBase):
    platform_name = "Lazada VN"
    currency = "VND"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.lazada.vn/catalog/?q={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "vi-VN,vi;q=0.9"
        return h


class LazadaID(LazadaBase):
    platform_name = "Lazada ID"
    currency = "IDR"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.lazada.co.id/catalog/?q={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "id-ID,id;q=0.9"
        return h


class LazadaMY(LazadaBase):
    platform_name = "Lazada MY"
    currency = "MYR"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.lazada.com.my/catalog/?q={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "ms-MY,ms;q=0.9"
        return h


class Tokopedia(GlobalBaseCrawler):
    """Tokopedia (印尼最大電商平台)"""
    REGION = "東南亞"
    platform_name = "Tokopedia"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.tokopedia.com/search?page={page}&q={q}&st=product"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "id-ID,id;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*productCard[^"]*"[^>]*>(.*?)</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<span[^>]*class="[^"]*productName[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="[^"]*price[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                price_str = clean_html(price_m.group(1)) if price_m else None
                price = re.sub(r'[^\d.]', '', price_str) if price_str else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="IDR"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Tokopedia] 解析失敗: {e}")
        return products
