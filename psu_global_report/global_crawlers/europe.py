"""
歐洲電商平台爬蟲
- Amazon.de (德國)
- Amazon.co.uk (英國)
- MediaMarkt (歐洲)
- Saturn (德國)
"""

import re
import logging
from .base_crawler import GlobalBaseCrawler
from .brand_utils import detect_brand, clean_html

logger = logging.getLogger(__name__)


class AmazonDE(GlobalBaseCrawler):
    """Amazon.de (德國)"""
    REGION = "歐洲"
    platform_name = "Amazon DE"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.amazon.de/s?k={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "de-DE,de;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<div[^>]*data-component-type="s-search-result"[^>]*>(.*?)</div>\s*</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<span[^>]*class="a-size-medium[^"]*a-color-base[^"]*a-text-normal"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="a-price-whole"[^>]*>(\d+)</span>',
                    item_html
                )
                price = price_m.group(1) if price_m else None

                url_m = re.search(
                    r'<a[^>]*class="a-link-normal s-no-outline[^"]*"[^>]*href="([^"]+)"',
                    item_html
                )
                url = "https://www.amazon.de" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="EUR"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Amazon DE] 解析失敗: {e}")
        return products


class AmazonUK(GlobalBaseCrawler):
    """Amazon.co.uk (英國)"""
    REGION = "歐洲"
    platform_name = "Amazon UK"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.amazon.co.uk/s?k={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "en-GB,en;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<div[^>]*data-component-type="s-search-result"[^>]*>(.*?)</div>\s*</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<span[^>]*class="a-size-medium[^"]*a-color-base[^"]*a-text-normal"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(r'<span[^>]*class="a-price-whole"[^>]*>(\d+)</span>', item_html)
                price = price_m.group(1) if price_m else None

                url_m = re.search(
                    r'<a[^>]*class="a-link-normal s-no-outline[^"]*"[^>]*href="([^"]+)"',
                    item_html
                )
                url = "https://www.amazon.co.uk" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="GBP"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Amazon UK] 解析失敗: {e}")
        return products


class MediaMarkt(GlobalBaseCrawler):
    """MediaMarkt (歐洲大型電子零售商)"""
    REGION = "歐洲"
    platform_name = "MediaMarkt"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.mediamarkt.de/de/search?query={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "de-DE,de;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        # MediaMarkt 商品卡片
        item_pattern = re.compile(
            r'<article[^>]*class="[^"]*product[^"]*"[^>]*>(.*?)</article>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<span[^>]*class="[^"]*product-title[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="[^"]*price[^"]*"[^>]*>.*?(\d+[,.]\d+)',
                    item_html, re.DOTALL
                )
                price = price_m.group(1).replace(",", ".") if price_m else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = "https://www.mediamarkt.de" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="EUR"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[MediaMarkt] 解析失敗: {e}")
        return products


class Saturn(GlobalBaseCrawler):
    """Saturn (德國/奧地利電子零售商)"""
    REGION = "歐洲"
    platform_name = "Saturn"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.saturn.de/de/search.html?search={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "de-DE,de;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*productCell[^"]*"[^>]*>(.*?)</div>\s*</div>',
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
                url = "https://www.saturn.de" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="EUR"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Saturn] 解析失敗: {e}")
        return products
