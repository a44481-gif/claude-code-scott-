"""
北美電商平台爬蟲
- Amazon.com (US)
- Newegg
- Best Buy US
"""

import re
import logging
from .base_crawler import GlobalBaseCrawler, ProductInfo
from .brand_utils import detect_brand, extract_wattage, extract_certification, clean_html

logger = logging.getLogger(__name__)


class AmazonUS(GlobalBaseCrawler):
    """Amazon.com (北美)"""
    REGION = "北美"
    platform_name = "Amazon US"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.amazon.com/s?k={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "en-US,en;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list[ProductInfo]:
        products = []
        # Amazon 搜尋結果區塊
        item_pattern = re.compile(
            r'<div[^>]*data-component-type="s-search-result"[^>]*>(.*?)</div>\s*</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                # 商品名
                name_m = re.search(
                    r'<span[^>]*class="a-size-medium[^"]*a-color-base[^"]*a-text-normal"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    name_m = re.search(
                        r'<a[^>]*class="a-link-normal[^"]*a-text-normal"[^>]*title="([^"]+)"',
                        item_html, re.DOTALL
                    )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()

                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                # 價格
                price_m = re.search(r'<span[^>]*class="a-price-whole"[^>]*>(\d+)</span>', item_html)
                price = price_m.group(1) if price_m else None

                # 評分
                rating_m = re.search(r'<span[^>]*class="a-icon-alt"[^>]*>([^<]+)</span>', item_html)
                rating = rating_m.group(1).strip()[:3] if rating_m else None

                # 評論數
                reviews_m = re.search(
                    r'<span[^>]*class="a-size-base s-underline-text"[^>]*>\((\d+,?\d*)\)</span>',
                    item_html
                )
                reviews = reviews_m.group(1) if reviews_m else None

                # 連結
                url_m = re.search(
                    r'<a[^>]*class="a-link-normal s-no-outline[^"]*"[^>]*href="([^"]+)"',
                    item_html
                )
                url = "https://www.amazon.com" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="USD", rating=rating, reviews_count=reviews,
                    sales_count=reviews,
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Amazon US] 解析失敗: {e}")
        return products


class NeweggCrawler(GlobalBaseCrawler):
    """Newegg.com (北美)"""
    REGION = "北美"
    platform_name = "Newegg"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.newegg.com/p/pl?d={q}&Page={page}"

    def parse_products(self, html: str, brand_map) -> list[ProductInfo]:
        products = []
        # Newegg 商品卡片
        item_pattern = re.compile(
            r'<div class="item-cell">(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                # 名稱
                name_m = re.search(
                    r'<a[^>]*class="item-title"[^>]*>(.*?)</a>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()

                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                # 價格
                price_m = re.search(
                    r'<li[^>]*class="price-current"[^>]*>.*?(\$[\d,.]+)',
                    item_html, re.DOTALL
                )
                price = price_m.group(1).replace("$", "").replace(",", "") if price_m else None

                # 評分
                rating_m = re.search(
                    r'<span[^>]*class="rating"[^>]*title="([^"]+)"',
                    item_html
                )
                rating = rating_m.group(1)[:3] if rating_m else None

                # URL
                url_m = re.search(r'href="([^"]+item[^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="USD", rating=rating,
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Newegg] 解析失敗: {e}")
        return products


class BestBuyUS(GlobalBaseCrawler):
    """BestBuy.com (北美)"""
    REGION = "北美"
    platform_name = "Best Buy US"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.bestbuy.com/site/search?sp={page}&page=1&q={q}&sl=true"

    def parse_products(self, html: str, brand_map) -> list[ProductInfo]:
        products = []
        item_pattern = re.compile(
            r'<li[^>]*class="sku-item"[^>]*>(.*?)</li>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<a[^>]*class="sku-title"[^>]*>(.*?)</a>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()

                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="priceView-customer-price"[^>]*>.*?(\$[\d,.]+)',
                    item_html, re.DOTALL
                )
                price = price_m.group(1).replace("$", "").replace(",", "") if price_m else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = "https://www.bestbuy.com" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="USD",
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Best Buy US] 解析失敗: {e}")
        return products


class AmazonCanada(GlobalBaseCrawler):
    """Amazon.ca (加拿大)"""
    REGION = "北美"
    platform_name = "Amazon Canada"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.amazon.ca/s?k={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "en-CA,en;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list[ProductInfo]:
        # 與 Amazon US 相同解析邏輯
        return AmazonUS.parse_products(self, html, brand_map)


class BestBuyCanada(GlobalBaseCrawler):
    """BestBuy.ca (加拿大)"""
    REGION = "北美"
    platform_name = "Best Buy Canada"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.bestbuy.ca/en-ca/search?q={q}&page={page}"

    def parse_products(self, html: str, brand_map) -> list[ProductInfo]:
        products = []
        item_pattern = re.compile(
            r'<div[^>]*class="productItem_"[^>]*>(.*?)</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<span[^>]*class="productTitle"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()

                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="price_[^"]*"[^>]*>.*?(\$[\d,.]+)',
                    item_html, re.DOTALL
                )
                price = price_m.group(1).replace("$", "").replace(",", "") if price_m else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="CAD",
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Best Buy Canada] 解析失敗: {e}")
        return products
