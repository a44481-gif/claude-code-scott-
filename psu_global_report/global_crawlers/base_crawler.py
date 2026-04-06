"""
全球電商平台 PSU 爬蟲 — 通用基類
每個區域一個爬蟲類，繼承此基類
"""

import httpx
import time
import logging
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional
from .brand_utils import (
    build_brand_map, detect_brand, extract_wattage,
    extract_certification, normalize_price, convert_currency,
    clean_html,
)

logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    """統一商品資料結構（涵蓋全球各平台）"""
    platform: str           # 平台名稱（含區域，如 "Amazon US"、"京東"）
    region: str             # 地區（北美/歐洲/俄羅斯/亞洲等）
    brand: str              # 品牌（標準化名稱）
    product_name: str       # 商品名稱
    price: Optional[float]  # 價格（已轉為 USD）
    original_price: Optional[str] = None   # 原價（當地幣別）
    currency: str = "USD"   # 幣別
    sales_count: Optional[str] = None     # 銷量/評論數
    rating: Optional[str] = None          # 評分（5分制）
    url: str = ""
    seller: Optional[str] = None
    wattage: Optional[str] = None         # 瓦數
    certification: Optional[str] = None   # 80+ 認證
    reviews_count: Optional[str] = None   # 評論數
    stock_status: Optional[str] = None     # 庫存狀態
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class GlobalBaseCrawler(ABC):
    """全球爬蟲基類"""

    # 子類需設定的地區分類
    REGION: str = "Global"

    def __init__(self, config: dict):
        self.config = config
        crawler_cfg = config.get("crawler", {})
        self.timeout = crawler_cfg.get("timeout", 30)
        self.retry = crawler_cfg.get("retry", 3)
        self.delay = crawler_cfg.get("delay_between_requests", 2)
        self.user_agent = crawler_cfg.get(
            "user_agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self._client: Optional[httpx.Client] = None
        self._brand_map: dict[str, str] = {}

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
    def parse_products(self, html: str, brand_map: dict[str, str]) -> list[ProductInfo]:
        """解析 HTML，回傳商品列表"""
        pass

    def get_headers(self) -> dict:
        return {
            "User-Agent": self.user_agent,
            "Accept-Language": self.accept_language,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    @property
    def accept_language(self) -> str:
        return "en-US,en;q=0.9"

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.timeout,
                headers=self.get_headers(),
                follow_redirects=True,
            )
        return self._client

    def fetch(self, url: str, encoding: Optional[str] = None) -> Optional[str]:
        """帶重試的 HTTP GET"""
        client = self._get_client()
        for attempt in range(self.retry):
            try:
                resp = client.get(url)
                if resp.status_code == 403:
                    logger.warning(f"[{self.platform_name}] HTTP 403 (blocked) on {url}")
                    time.sleep(5 * (attempt + 1))
                    continue
                if resp.status_code != 200:
                    logger.warning(
                        f"[{self.platform_name}] HTTP {resp.status_code} "
                        f"attempt {attempt + 1}: {url}"
                    )
                    time.sleep(self.delay * (attempt + 1))
                    continue
                if encoding:
                    return resp.content.decode(encoding, errors="replace")
                # 自動偵測編碼
                try:
                    return resp.text
                except Exception:
                    return resp.content.decode("utf-8", errors="replace")
            except httpx.TimeoutException:
                logger.warning(f"[{self.platform_name}] Timeout on attempt {attempt + 1}: {url}")
                time.sleep(self.delay * (attempt + 1))
            except Exception as e:
                logger.error(f"[{self.platform_name}] Attempt {attempt + 1} failed: {e}")
                time.sleep(self.delay * (attempt + 1))
        return None

    def collect(self, brands: list[dict], keyword: str, pages: int = 2) -> list[ProductInfo]:
        """主收集方法"""
        if not self._brand_map:
            self._brand_map = build_brand_map(brands)

        all_products = []
        for page in range(1, pages + 1):
            url = self.build_search_url(keyword, page)
            logger.info(f"[{self.platform_name}] Fetching page {page}: {url}")
            html = self.fetch(url)
            if html:
                products = self.parse_products(html, self._brand_map)
                all_products.extend(products)
                logger.info(f"[{self.platform_name}] Page {page}: found {len(products)} items")
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

    # ── 通用解析輔助方法 ────────────────────────────────────────────

    def _safe_search(self, pattern: str, text: str, group: int = 1, flags: int = 0) -> Optional[str]:
        try:
            m = re.search(pattern, text, flags)
            return m.group(group) if m else None
        except Exception:
            return None

    def _safe_findall(self, pattern: str, text: str, group: int = 1, flags: int = 0) -> list[str]:
        try:
            return re.findall(pattern, text, flags)
        except Exception:
            return []

    def _build_product(
        self,
        name: str,
        brand: Optional[str],
        price: Optional[str],
        url: str,
        raw_html: str,
        currency: str = "USD",
        **kwargs
    ) -> Optional[ProductInfo]:
        """通用商品構建器 — 所有爬蟲共享"""
        if not brand:
            return None
        if not name:
            return None

        # 價格標準化
        price_val = None
        if price:
            price_val = normalize_price(price)
            if price_val and currency != "USD":
                price_val = convert_currency(price_val, currency)

        return ProductInfo(
            platform=self.platform_name,
            region=self.REGION,
            brand=brand,
            product_name=clean_html(name)[:200],
            price=price_val,
            original_price=price,
            currency="USD",
            url=url,
            wattage=extract_wattage(name),
            certification=extract_certification(name),
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
