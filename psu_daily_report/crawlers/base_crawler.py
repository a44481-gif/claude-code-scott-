"""
Base crawler module for PSU sales data collection.
Provides common functionality for all platform crawlers.
"""

import httpx
import time
import logging
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    """單一商品資料結構"""
    platform: str          # 電商平台名稱
    brand: str              # 品牌（對應我們的目標品牌）
    product_name: str       # 商品名稱
    price: Optional[str]    # 價格（可能為字串，含幣別）
    currency: str = "CNY"   # 幣別
    sales_count: Optional[str] = None  # 銷量/評論數
    rating: Optional[str] = None        # 評分
    url: str = ""           # 商品連結
    seller: Optional[str] = None        # 賣家
    wattage: Optional[str] = None       # 瓦數（如 750W）
    certification: Optional[str] = None # 認證（如 80+ Gold）
    timestamp: str = ""     # 抓取時間


class BaseCrawler(ABC):
    """爬蟲基類"""

    def __init__(self, config: dict):
        self.config = config
        self.timeout = config.get("crawler", {}).get("timeout", 30)
        self.retry = config.get("crawler", {}).get("retry", 3)
        self.delay = config.get("crawler", {}).get("delay_between_requests", 2)
        self.user_agent = config.get("crawler", {}).get(
            "user_agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self._client: Optional[httpx.Client] = None

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """平台名稱"""
        pass

    @abstractmethod
    def build_search_url(self, keyword: str, page: int = 1) -> str:
        """構建搜尋 URL"""
        pass

    @abstractmethod
    def parse_products(self, html: str, brands: list) -> list[ProductInfo]:
        """解析 HTML，回傳商品列表"""
        pass

    def get_headers(self) -> dict:
        """HTTP 請求頭"""
        return {
            "User-Agent": self.user_agent,
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.timeout,
                headers=self.get_headers(),
                follow_redirects=True,
            )
        return self._client

    def fetch(self, url: str) -> Optional[str]:
        """帶重試的 HTTP GET"""
        client = self._get_client()
        for attempt in range(self.retry):
            try:
                resp = client.get(url)
                if resp.status_code == 200:
                    return resp.text
                logger.warning(
                    f"[{self.platform_name}] HTTP {resp.status_code} "
                    f"on attempt {attempt + 1}: {url}"
                )
            except Exception as e:
                logger.error(
                    f"[{self.platform_name}] Attempt {attempt + 1} failed: {e}"
                )
            time.sleep(self.delay * (attempt + 1))
        return None

    def collect(self, brands: list, keyword: str = "電源供應器") -> list[ProductInfo]:
        """
        主收集方法：搜尋關鍵字，解析各頁結果
        """
        all_products = []
        # 通常抓前 2 頁就夠了
        for page in range(1, 3):
            url = self.build_search_url(keyword, page)
            logger.info(f"[{self.platform_name}] Fetching page {page}: {url}")
            html = self.fetch(url)
            if html:
                products = self.parse_products(html, brands)
                all_products.extend(products)
                logger.info(
                    f"[{self.platform_name}] Page {page}: found {len(products)} items"
                )
            time.sleep(self.delay)
        return all_products

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
