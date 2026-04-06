"""
俄羅斯電商平台爬蟲
⚠️ 注意：Ozon、Wildberries、Yandex.Market 需要登入/API 或反爬機制較強
，建議使用 Playwright/Selenium 或官方 API 抓取
此處提供 URL 模板和基礎解析邏輯，實際運行可能需要進一步調整
"""

import re
import logging
from .base_crawler import GlobalBaseCrawler
from .brand_utils import detect_brand, clean_html

logger = logging.getLogger(__name__)


class Ozon(GlobalBaseCrawler):
    """
    Ozon.ru (俄羅斯最大電商平台)
    ⚠️ 需要 API 或 JavaScript 渲染，建議使用 Playwright
    """
    REGION = "俄羅斯"
    platform_name = "Ozon"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        # Ozon API 風格搜尋（也可走 HTML 搜尋）
        return (
            f"https://www.ozon.ru/search/?text={q}&page={page}"
        )

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "ru-RU,ru;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        """
        Ozon 使用 JavaScript 渲染，HTML 搜尋結果有限
        ⚠️ 建議啟用 Playwright 模式
        """
        products = []
        # Ozon 商品卡片 HTML 結構
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*widget[^"]*ood5[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<span[^>]*class="[^"]*tsBody[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="[^"]*c301-a1[^"]*"[^>]*>.*?(\d+[\s\d]*)',
                    item_html, re.DOTALL
                )
                price = re.sub(r'\s', '', price_m.group(1)) if price_m else None

                url_m = re.search(r'href="(/product/[^"]+)"', item_html)
                url = "https://www.ozon.ru" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="RUB"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Ozon] 解析失敗: {e}")

        if len(products) < 3:
            logger.warning(
                "[Ozon] ⚠️ 檢測到 HTML 解析結果過少，建議使用 Playwright "
                "（Ozon 使用 JavaScript 渲染，HTTP 請求可能無法獲取完整數據）"
            )
        return products


class Wildberries(GlobalBaseCrawler):
    """
    Wildberries.ru (俄羅斯電商平台)
    ⚠️ 需要登入 Cookie 或 API，建議使用 Playwright
    """
    REGION = "俄羅斯"
    platform_name = "Wildberries"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.wildberries.ru/catalog/0/search.aspx?search={q}&page={page}"

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "ru-RU,ru;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        # Wildberries 商品卡片
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*j-card-item[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<span[^>]*class="[^"]*goods-name[^"]*"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<span[^>]*class="[^"]*price[^"]*"[^>]*>.*?(\d+)',
                    item_html, re.DOTALL
                )
                price = price_m.group(1) if price_m else None

                url_m = re.search(r'href="(/product/[^"]+)"', item_html)
                url = "https://www.wildberries.ru" + url_m.group(1) if url_m else ""

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="RUB"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Wildberries] 解析失敗: {e}")

        if len(products) < 3:
            logger.warning(
                "[Wildberries] ⚠️ HTML 解析結果過少，建議使用 Playwright "
                "（Wildberries 需要登入才能查看完整數據）"
            )
        return products


class YandexMarket(GlobalBaseCrawler):
    """Yandex.Market (俄羅斯比價購物平台)"""
    REGION = "俄羅斯"
    platform_name = "Yandex Market"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        q = keyword.replace(" ", "+")
        return (
            f"https://market.yandex.ru/search?text={q}&page={page}"
        )

    def get_headers(self):
        h = super().get_headers()
        h["Accept-Language"] = "ru-RU,ru;q=0.9"
        return h

    def parse_products(self, html: str, brand_map) -> list:
        products = []
        item_pattern = re.compile(
            r'<div[^>]*class="[^"]*n-snippet-card2[^"]*"[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        for item_html in item_pattern.findall(html):
            try:
                name_m = re.search(
                    r'<a[^>]*class="[^"]*link[^"]*title[^"]*"[^>]*>(.*?)</a>',
                    item_html, re.DOTALL
                )
                if not name_m:
                    continue
                name = clean_html(name_m.group(1)).strip()
                brand = detect_brand(name, brand_map)
                if not brand:
                    continue

                price_m = re.search(
                    r'<a[^>]*class="[^"]*price[^"]*"[^>]*>.*?(\d+[\s\d]*)',
                    item_html, re.DOTALL
                )
                price = re.sub(r'\s', '', price_m.group(1)) if price_m else None

                url_m = re.search(r'href="([^"]+)"', item_html)
                url = url_m.group(1) if url_m else ""
                if url and not url.startswith("http"):
                    url = "https://market.yandex.ru" + url

                p = self._build_product(
                    name=name, brand=brand, price=price, url=url,
                    currency="RUB"
                )
                if p:
                    products.append(p)
            except Exception as e:
                logger.debug(f"[Yandex Market] 解析失敗: {e}")
        return products
