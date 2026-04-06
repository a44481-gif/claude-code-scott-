"""
中東電商平台爬蟲
Souq.com (原中東最大電商，已被 Amazon 收購整合)
Noon.com (中東新興電商巨頭)
"""

import re
import logging
from .base_crawler import GlobalBaseCrawler
from .brand_utils import detect_brand, clean_html

logger = logging.getLogger(__name__)


class Noon(GlobalBaseCrawler):
    """Noon.com (中東/北非電商巨頭，覆蓋沙烏地阿拉伯/阿聯酋/埃及等)"""
    REGION = "中東"
    platform_name = "Noon"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.noon.com/saudi-en/search/?q={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "en-AE,en;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        # Noon 商品卡片
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*productWidget[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<h3[^>]*class="[^"]*productName[^"]*"[^>]*>(.*?)</h3>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    name_m = re.search(
                        r'<span[^>]*class="[^"]*productTitle[^"]*"[^>]*>(.*?)</span>',
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
                if url and not url.startswith("http"):
                    url = "https://www.noon.com" + url

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="SAR"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Noon] 解析失敗: {e}")

        if len(products) < 3:
            logger.warning(
                "[Noon] ⚠️ HTML 解析結果過少，Noon 有 JavaScript 渲染，"
                "建議使用 Playwright"
            )
        return products


class AmazonSAE(GlobalBaseCrawler):
    """Amazon.ae / Amazon Saudi (Amazon 中東站)"""
    REGION = "中東"
    platform_name = "Amazon UAE"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.amazon.ae/s?k={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "en-AE,en;q=0.9"
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
                url = "https://www.amazon.ae" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="AED"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Amazon UAE] 解析失敗: {e}")
        return products


# Souq.com 現已重定向至 Amazon.ae，故整合至 Amazon UAE 爬蟲
# 保留此處供歷史參考
class SouqDeprecated(GlobalBaseCrawler):
    """Souq.com — 已於 2019 年整合至 Amazon.ae，請使用 AmazonSAE"""
    REGION = "中東"
    platform_name = "Souq (已停用→Amazon.ae)"
    currency = "AED"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        logger.warning("[Souq] Souq.com 已於 2019 年停止服務，請使用 Amazon.ae 爬蟲")
        return "https://www.amazon.ae"

    def parse_products(self, html: str, brand_map) -> list:
        logger.warning("[Souq] 此爬蟲已停用")
        return []
