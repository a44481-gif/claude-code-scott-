"""
Playwright 爬蟲基類
專門用於需要 JavaScript 渲染的電商平台
"""

import time
import logging
import re
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    logger.warning("Playwright 未安裝，JS 渲染爬蟲將無法使用")

from .brand_utils import (
    build_brand_map, detect_brand, extract_wattage,
    extract_certification, normalize_price, convert_currency, clean_html,
)

from .base_crawler import ProductInfo


@dataclass
class PlaywrightConfig:
    """Playwright 爬蟲配置"""
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 800
    timeout_ms: int = 30000
    wait_for_selector: Optional[str] = None
    wait_for_load: str = "networkidle"
    scroll_pages: int = 1        # 滾動頁面次數（觸發 lazy load）
    delay_between_scrolls: float = 1.5  # 滾動間隔（秒）
    locale: str = "en-US"


class PlaywrightCrawler:
    """
    Playwright 爬蟲基類
    使用方式：
        class MyShopCrawler(PlaywrightCrawler):
            platform_name = "MyShop"
            REGION = "亞洲"
            SELECTORS = {...}  # 定義商品卡、價格、名稱的 CSS 選擇器

            def build_url(self, keyword: str, page: int) -> str:
                return f"https://myshop.com/search?q={keyword}&page={page}"
    """

    platform_name: str = "Playwright"
    REGION: str = "Global"
    currency: str = "USD"

    # 子類需覆寫
    SELECTORS: dict = None   # 必須定義：item, name, price, url

    def __init__(self, config: dict, pw_config: PlaywrightConfig | None = None):
        if not HAS_PLAYWRIGHT:
            raise ImportError("Playwright 未安裝，請執行：pip install playwright && python -m playwright install chromium")

        self.config = config
        self.pw_cfg = pw_config or PlaywrightConfig()
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._brand_map: dict = {}

    def _get_browser(self) -> Browser:
        if self._browser is None:
            pw = sync_playwright().start()
            self._browser = pw.chromium.launch(
                headless=self.pw_cfg.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
        return self._browser

    def _get_context(self) -> BrowserContext:
        if self._context is None:
            browser = self._get_browser()
            self._context = browser.new_context(
                viewport={"width": self.pw_cfg.viewport_width,
                          "height": self.pw_cfg.viewport_height},
                locale=self.pw_cfg.locale,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
            )
        return self._context

    def collect(self, brands: list[dict], keyword: str, pages: int = 1) -> list[ProductInfo]:
        """主收集方法"""
        if not self._brand_map:
            self._brand_map = build_brand_map(brands)

        all_products = []
        for page_num in range(1, pages + 1):
            logger.info(f"[{self.platform_name}] Playwright 抓取第 {page_num} 頁...")
            products = self._collect_page(keyword, page_num)
            all_products.extend(products)
            logger.info(f"[{self.platform_name}] 第 {page_num} 頁: {len(products)} 個商品")
            time.sleep(self.pw_cfg.delay_between_scrolls)
        return all_products

    def _collect_page(self, keyword: str, page_num: int) -> list[ProductInfo]:
        """抓取單個頁面"""
        url = self.build_url(keyword, page_num)
        context = self._get_context()
        page = context.new_page()

        try:
            page.goto(url, wait_until=self.pw_cfg.wait_for_load, timeout=self.pw_cfg.timeout_ms)

            # 滾動頁面觸發 lazy load
            for _ in range(self.pw_cfg.scroll_pages):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(self.pw_cfg.delay_between_scrolls * 1000)

            # 等待商品區塊出現
            if self.SELECTORS and "item" in self.SELECTORS:
                try:
                    page.wait_for_selector(self.SELECTORS["item"], timeout=10000)
                except Exception:
                    logger.warning(f"[{self.platform_name}] 無法等待選擇器: {self.SELECTORS['item']}")

            html = page.content()
            return self.parse_products(html, self._brand_map, page)

        except Exception as e:
            logger.error(f"[{self.platform_name}] Playwright 錯誤: {e}")
            return []
        finally:
            page.close()

    def build_url(self, keyword: str, page: int) -> str:
        """構建搜尋 URL（子類覆寫）"""
        q = keyword.replace(" ", "%20")
        return f"https://example.com/search?q={q}&page={page}"

    def parse_products(self, html: str, brand_map: dict, page: Page) -> list[ProductInfo]:
        """解析頁面（子類覆寫）"""
        products = []

        if not self.SELECTORS:
            logger.warning(f"[{self.platform_name}] 未定義 SELECTORS")
            return products

        try:
            # 使用 Playwright locator API（比正則更準確）
            items = page.locator(self.SELECTORS["item"]).all()

            for item in items:
                try:
                    name = self._get_text(item, self.SELECTORS.get("name"))
                    price_raw = self._get_text(item, self.SELECTORS.get("price"))
                    url = self._get_attr(item, self.SELECTORS.get("url"), "href")

                    if not name:
                        continue

                    brand = detect_brand(name, brand_map)
                    if not brand:
                        continue

                    # 價格標準化
                    price = normalize_price(price_raw)

                    product = ProductInfo(
                        platform=self.platform_name,
                        region=self.REGION,
                        brand=brand,
                        product_name=clean_html(name)[:200],
                        price=price,
                        original_price=price_raw,
                        currency=self.currency,
                        url=url or "",
                        wattage=extract_wattage(name),
                        certification=extract_certification(name),
                        timestamp=datetime.now().isoformat(),
                    )
                    products.append(product)
                except Exception as e:
                    logger.debug(f"[{self.platform_name}] 解析商品失敗: {e}")
        except Exception as e:
            logger.error(f"[{self.platform_name}] 頁面解析失敗: {e}")

        return products

    def _get_text(self, locator, selector: Optional[str]) -> Optional[str]:
        """從 locator 獲取文本"""
        if not selector:
            return None
        try:
            el = locator.locator(selector).first
            return el.inner_text().strip()
        except Exception:
            return None

    def _get_attr(self, locator, selector: Optional[str], attr: str) -> Optional[str]:
        """從 locator 獲取屬性"""
        if not selector:
            return None
        try:
            el = locator.locator(selector).first
            return el.get_attribute(attr)
        except Exception:
            return None

    def close(self):
        if self._context:
            self._context.close()
            self._context = None
        if self._browser:
            self._browser.close()
            self._browser = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
