"""
南美電商平台爬蟲
Mercado Libre (阿根廷/巴西/墨西哥/智利/哥倫比亞等)
"""

import re
import logging
from .base_crawler import GlobalBaseCrawler
from .brand_utils import detect_brand, clean_html

logger = logging.getLogger(__name__)


class MercadoLibreBase(GlobalBaseCrawler):
    """Mercado Libre (南美最大電商平台，覆蓋多國)"""
    REGION = "南美"

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        # Mercado Libre 商品卡片
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*ui-card-padding[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<span[^>]*class="[^"]*mainTitle[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="[^"]*price-tag[^"]*"[^>]*>(.*?)</span>',
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
                logger.debug(f"[{self.platform_name}] 解析失敗: {e}")

        if len(products) < 3:
            logger.warning(
                f"[{self.platform_name}] ⚠️ HTML 解析結果過少，"
                "Mercado Libre 有 JavaScript 渲染，建議使用 Playwright"
            )
        return products


class MercadoLibreAR(MercadoLibreBase):
    """Mercado Libre Argentina"""
    platform_name = "Mercado Libre AR"
    currency = "ARS"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.mercadolibre.com.ar/search?q={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "es-AR,es;q=0.9"
        return h


class MercadoLibreBR(MercadoLibreBase):
    """Mercado Livre Brasil (巴西)"""
    platform_name = "Mercado Livre BR"
    currency = "BRL"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.mercadolivre.com.br/search?q={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "pt-BR,pt;q=0.9"
        return h


class MercadoLibreMX(MercadoLibreBase):
    """Mercado Libre México (墨西哥)"""
    platform_name = "Mercado Libre MX"
    currency = "MXN"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.mercadolibre.com.mx/search?q={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "es-MX,es;q=0.9"
        return h
