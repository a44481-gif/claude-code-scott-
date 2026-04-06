"""
台灣電商平台爬蟲
PChome 24h 購物、Momo 購物網
"""

import re
import logging
from .base_crawler import GlobalBaseCrawler
from .brand_utils import detect_brand, clean_html

logger = logging.getLogger(__name__)


class PChome(GlobalBaseCrawler):
    """PChome 24h 購物 (台灣最大電商平台之一)"""
    REGION = "亞洲"
    platform_name = "PChome"
    currency = "TWD"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://shopping.pchome.com.tw/search/?q={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "zh-TW,zh;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        # PChome 商品卡片
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*col3flow[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<h3[^>]*class="[^"]*prodName[^"]*"[^>]*>(.*?)</h3>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    name_m = re.search(
                        r'<a[^>]*class="[^"]*prodName[^"]*"[^>]*>(.*?)</a>',
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
                if url and not url.startswith("http"):
                    url = "https://shopping.pchome.com.tw" + url

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="TWD"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[PChome] 解析失敗: {e}")
        return products


class Momo(GlobalBaseCrawler):
    """Momo 購物網 (台灣大型電商)"""
    REGION = "亞洲"
    platform_name = "Momo"
    currency = "TWD"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.momoshop.com.tw/search/search.jsp?keyword={q}&goodsForm=LIST&curPage={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "zh-TW,zh;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        # Momo 商品卡片
        item_pattern = re.compile(
            r'<li[^>]*class="[^"]*goodsItemLi[^"]*"[^>]*>(.*?)</li>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<h3[^>]*class="[^"]*prdName[^"]*"[^>]*>(.*?)</h3>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    name_m = re.search(
                        r'<a[^>]*class="[^"]*prdName[^"]*"[^>]*>(.*?)</a>',
                        item_html, re.DOTALL
                    )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="[^"]*money[^"]*"[^>]*><b[^>]*>(.*?)</b>',
                    item_html, re.DOTALL
                )
                price_str = clean_html(price_m.group(1)) if price_m else None
                price = re.sub(r'[^\d]', '', price_str) if price_str else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""
                if url and not url.startswith("http"):
                    url = "https://www.momoshop.com.tw" + url

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="TWD"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Momo] 解析失敗: {e}")
        return products
