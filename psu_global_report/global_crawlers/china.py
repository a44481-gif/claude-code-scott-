"""
中國電商平台爬蟲
京東 (JD.com)、京東國際、天貓 (Tmall)、淘寶 (Taobao)

注意：京東/天貓有嚴格反爬機制。
HTTP 版本可能需要添加 Cookie 或使用 Playwright 才能穩定抓取。
"""

import re
import logging
from .base_crawler import GlobalBaseCrawler
from .brand_utils import detect_brand, clean_html

logger = logging.getLogger(__name__)


class JDGlobal(GlobalBaseCrawler):
    """
    京東 (JD.com) — 中國最大電商平台
    注意：需確保訪問 mainland JD（search.jd.com），不是 tw.jd.com
    """
    REGION = "亞洲"
    platform_name = "京東"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        # 確保送到 mainland JD
        encoded = keyword.encode("utf-8").decode("utf-8")
        import urllib.parse
        q = urllib.parse.quote(encoded)
        return (
            f"https://search.jd.com/Search?keyword={q}"
            f"&enc=utf-8&page={page}"
            f"&wq={q}"  # 搜索框即時建議詞（同步）
        )

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "zh-CN,zh;q=0.9"
        h["Referer"] = "https://www.jd.com/"
        h["Origin"] = "https://www.jd.com"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<li class="gl-item"[^>]*>(.*?)</li>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<div class="p-name p-name-type2">.*?<em>(.*?)</em>(.*?)</a>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1) + name_m.group(2)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<i class="price">.*?([\d,.]+)</i>',
                    item_html, re.DOTALL
                )
                price = price_m.group(1).replace(",", "") if price_m else None

                sales_m = re.search(
                    r'<div class="p-commit">.*?(\d+[萬百千]?[0-9]?)',
                    item_html, re.DOTALL
                )
                sales = clean_html(sales_m.group(0)) if sales_m else None

                url_m = re.search(r'href="(//item\.jd\.com/\d+\.html[^"]*)"', item_html)
                url = "https:" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="CNY", sales_count=sales,
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[京東] 解析失敗: {e}")
        return products


class TmallGlobal(GlobalBaseCrawler):
    """
    天貓 (Tmall) — 中國最大 B2C 電商
    提示：直接 HTTP 可能跳轉到淘寶，建議使用 Playwright 版本
    """
    REGION = "亞洲"
    platform_name = "天貓"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        import urllib.parse
        q = urllib.parse.quote(keyword)
        return (
            f"https://list.tmall.com/search_product.htm"
            f"?q={q}&page={page}"
            f"&sort=s&style=g"  # sort by sales, grid style
        )

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "zh-CN,zh;q=0.9"
        h["Referer"] = "https://www.tmall.com/"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        # 天貓商品卡片
        item_pattern = re.compile(
            r'<div[^>]*class="product[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<a[^>]*class="productTitle[^"]*"[^>]*>.*?<em>(.*?)</em>(.*?)</a>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    name_m = re.search(
                        r'<p[^>]*class="productTitle[^"]*"[^>]*>(.*?)</p>',
                        item_html, re.DOTALL
                    )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1) + (name_m.group(2) if name_m.lastindex >= 2 else "")).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="[^"]*price[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                price_str = clean_html(price_m.group(1)) if price_m else None
                price = re.sub(r"[^\d.]", "", price_str) if price_str else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="CNY"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[天貓] 解析失敗: {e}")
        return products


class Taobao(GlobalBaseCrawler):
    """
    淘寶 (Taobao) — 中國最大 C2C 電商
    提示：淘寶搜尋需要登入狀態，建議使用 Playwright 版本
    """
    REGION = "亞洲"
    platform_name = "淘寶"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        import urllib.parse
        q = urllib.parse.quote(keyword)
        return f"https://s.taobao.com/search?q={q}&page={page}&sort=sale-desc"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "zh-CN,zh;q=0.9"
        h["Referer"] = "https://www.taobao.com/"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*item[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<a[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</a>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<strong[^>]*>(.*?)</strong>',
                    item_html, re.DOTALL
                )
                price_str = clean_html(price_m.group(1)) if price_m else None
                price = re.sub(r"[^\d.]", "", price_str) if price_str else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="CNY"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[淘寶] 解析失敗: {e}")
        return products
