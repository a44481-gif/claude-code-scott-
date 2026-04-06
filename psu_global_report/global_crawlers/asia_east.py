"""
日本 / 韓國 / 印度電商平台爬蟲
日本: Amazon.co.jp, 樂天市場 (Rakuten)
韓國: Gmarket, Coupang
印度: Flipkart, Amazon.in
"""

import re
import logging
from .base_crawler import GlobalBaseCrawler
from .brand_utils import detect_brand, clean_html

logger = logging.getLogger(__name__)


# ─────────── 日本 ───────────

class AmazonJP(GlobalBaseCrawler):
    """Amazon.co.jp (日本)"""
    REGION = "亞洲"
    platform_name = "Amazon JP"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.amazon.co.jp/s?k={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "ja-JP,ja;q=0.9"
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
                url = "https://www.amazon.co.jp" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="JPY"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Amazon JP] 解析失敗: {e}")
        return products


class Rakuten(GlobalBaseCrawler):
    """
    樂天市場 (Rakuten) — 日本最大電商平台
    ⚠️ 需要 Rakuten 登入或特定 Headers，標準 HTTP 可能受限
    """
    REGION = "亞洲"
    platform_name = "Rakuten"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return (
            f"https://search.rakuten.co.jp/search/mall/{q}/?size=30&p={page}"
        )

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "ja-JP,ja;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        # 樂天商品卡片
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*searchresultitem[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<a[^>]*class="[^"]*itemname[^"]*"[^>]*>(.*?)</a>',
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
                price = re.sub(r'[^\d]', '', price_str) if price_str else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="JPY"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Rakuten] 解析失敗: {e}")
        return products


# ─────────── 韓國 ───────────

class Gmarket(GlobalBaseCrawler):
    """
    Gmarket (韓國最大電商)
    ⚠️ Gmarket 需要韓文 Cookie 設置，標準 HTTP 可能受限
    """
    REGION = "亞洲"
    platform_name = "Gmarket"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.gmarket.co.kr/n/search?keyword={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "ko-KR,ko;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*box__component-itemcard[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<span[^>]*class="[^"]*txt__item[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<strong[^>]*class="[^"]*price[^"]*"[^>]*>(.*?)</strong>',
                    item_html, re.DOTALL
                )
                price_str = clean_html(price_m.group(1)) if price_m else None
                price = re.sub(r'[^\d]', '', price_str) if price_str else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = "https://www.gmarket.co.kr" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="KRW"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Gmarket] 解析失敗: {e}")
        return products


class Coupang(GlobalBaseCrawler):
    """
    Coupang (韓國電商巨頭)
    ⚠️ Coupang 有反爬機制，建議使用 Playwright
    """
    REGION = "亞洲"
    platform_name = "Coupang"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.coupang.com/np/search?q={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "ko-KR,ko;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<li[^>]*class="[^"]*search-product[^"]*"[^>]*>(.*?)</li>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<span[^>]*class="[^"]*name[^"]*"[^>]*>(.*?)</span>',
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
                price = re.sub(r'[^\d]', '', price_str) if price_str else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="KRW"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Coupang] 解析失敗: {e}")

        if len(products) < 3:
            logger.warning(
                "[Coupang] ⚠️ HTML 解析結果過少，Coupang 有較強反爬機制，"
                "建議使用 Playwright"
            )
        return products


# ─────────── 印度 ───────────

class Flipkart(GlobalBaseCrawler):
    """Flipkart (印度最大電商平台)"""
    REGION = "亞洲"
    platform_name = "Flipkart"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return (
            f"https://www.flipkart.com/search?q={q}&page={page}"
        )

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "en-IN,en;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*_1AtVB5[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<a[^>]*class="[^"]*KzDlHZ[^"]*"[^>]*>(.*?)</a>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    name_m = re.search(
                        r'<div[^>]*class="[^"]*product-name[^"]*"[^>]*>(.*?)</div>',
                        item_html, re.DOTALL
                    )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<div[^>]*class="[^"]*Nx9bq[^"]*"[^>]*>(.*?)</div>',
                    item_html, re.DOTALL
                )
                price_str = clean_html(price_m.group(1)) if price_m else None
                price = re.sub(r'[^\d]', '', price_str) if price_str else None

                rating_m = re.search(
                    r'<span[^>]*class="[^"]*Wphh3N[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                rating = clean_html(rating_m.group(1))[:3] if rating_m else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = "https://www.flipkart.com" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="INR", rating=rating,
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Flipkart] 解析失敗: {e}")
        return products


class AmazonIN(GlobalBaseCrawler):
    """Amazon.in (印度)"""
    REGION = "亞洲"
    platform_name = "Amazon IN"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.amazon.in/s?k={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "en-IN,en;q=0.9"
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
                url = "https://www.amazon.in" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="INR"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Amazon IN] 解析失敗: {e}")
        return products
