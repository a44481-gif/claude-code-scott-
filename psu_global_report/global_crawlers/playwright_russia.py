"""
俄羅斯電商平台 Playwright 爬蟲
覆蓋：Ozon, Wildberries, Yandex Market
俄羅斯平台有強反爬機制，HTTP 無法穩定抓取
"""

import logging
from .playwright_base import PlaywrightCrawler, PlaywrightConfig

logger = logging.getLogger(__name__)


class OzonPlaywright(PlaywrightCrawler):
    """Ozon.ru — 俄羅斯最大電商平台"""
    platform_name = "Ozon"
    REGION = "俄羅斯"
    currency = "RUB"

    SELECTORS = {
        # Ozon 搜尋結果商品卡片
        "item": "[data-widget='searchResultsV2'] .ts-item, .widget-search-result-container .a00o0",
        "name": "[class*='tsBody'] a, .a00o0 a[href*='/product/']",
        "price": "[class*='c301-a1'], [class*='price'], .a00o0 [class*='price'] span:first-child",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "+")
        return f"https://www.ozon.ru/search/?text={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="ru-RU",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))


class WildberriesPlaywright(PlaywrightCrawler):
    """Wildberries.ru — 俄羅斯電商（需登入）"""
    platform_name = "Wildberries"
    REGION = "俄羅斯"
    currency = "RUB"

    SELECTORS = {
        "item": ".j-card-item, .productCard",
        "name": ".goods-name, .productCard a[href*='/product/']",
        "price": ".price-block .price, .productCard [class*='price']",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "%20")
        return f"https://www.wildberries.ru/catalog/0/search.aspx?search={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="ru-RU",
            scroll_pages=2,
            delay_between_scrolls=2.0,
        ))

    def _collect_page(self, keyword: str, page_num: int):
        """Wildberries 需要特殊處理：頁面有延遲加載"""
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        url = self.build_url(keyword, page_num)
        context = self._get_context()
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=self.pw_cfg.timeout_ms)
            # 等待動態內容
            page.wait_for_timeout(3000)
            for _ in range(self.pw_cfg.scroll_pages):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            html = page.content()
            return self.parse_products(html, self._brand_map, page)
        except Exception as e:
            logger.error(f"[Wildberries] Playwright 錯誤: {e}")
            return []
        finally:
            page.close()


class YandexMarketPlaywright(PlaywrightCrawler):
    """Yandex Market — 俄羅斯比價平台"""
    platform_name = "Yandex Market"
    REGION = "俄羅斯"
    currency = "RUB"

    SELECTORS = {
        "item": ".n-snippet-card2, .serp-controller__content .search-snippet",
        "name": "a.link[href*='/product/'], a.AlgTitle",
        "price": "[class*='price'], .price-block__price-value",
        "url": "a[href*='/product/']",
    }

    def build_url(self, keyword: str, page: int) -> str:
        q = keyword.replace(" ", "+")
        return f"https://market.yandex.ru/search?text={q}&page={page}"

    def __init__(self, config: dict):
        super().__init__(config, PlaywrightConfig(
            headless=True,
            locale="ru-RU",
            scroll_pages=1,
            delay_between_scrolls=1.5,
        ))
