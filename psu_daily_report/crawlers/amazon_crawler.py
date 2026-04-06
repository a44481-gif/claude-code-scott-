"""
亞馬遜 (Amazon) 爬蟲
URL: https://www.amazon.com/s?k=power+supply+unit
"""

import re
import logging
from datetime import datetime
from .base_crawler import BaseCrawler, ProductInfo

logger = logging.getLogger(__name__)


class AmazonCrawler(BaseCrawler):
    platform_name = "Amazon"

    # 熱門 PSU 關鍵字組合
    KEYWORDS = [
        "power supply unit",
        "PSU computer",
        "ATX power supply",
        "computer power supply",
    ]

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        # Amazon 分頁用 &page=X
        encoded = keyword.replace(" ", "+")
        return (
            f"https://www.amazon.com/s?k={encoded}"
            f"&page={page}"
        )

    def get_headers(self) -> dict:
        headers = super().get_headers()
        headers["Accept-Language"] = "en-US,en;q=0.9"
        headers["Upgrade-Insecure-Requests"] = "1"
        return headers

    def parse_products(self, html: str, brands: list) -> list[ProductInfo]:
        products = []

        brand_names = [b["name"] for b in brands]
        brand_aliases: dict[str, str] = {}
        for b in brands:
            brand_aliases[b["name"]] = b["name"]
            for alias in b.get("aliases", []):
                brand_aliases[alias.lower()] = b["name"]

        # Amazon 商品區塊：data-component-type="s-search-result"
        item_pattern = re.compile(
            r'<div[^>]*data-component-type="s-search-result"[^>]*>(.*?)</div>\s*</div>\s*</div>',
            re.DOTALL
        )
        items = item_pattern.findall(html)

        for item_html in items:
            try:
                # 商品名稱
                name_match = re.search(
                    r'<span[^>]*class="a-size-medium[^"]*a-color-base[^"]*a-text-normal"[^>]*>(.*?)</span>',
                    item_html, re.DOTALL
                )
                if not name_match:
                    # 備用名稱解析
                    name_match = re.search(
                        r'<a[^>]*class="a-link-normal[^"]*a-text-normal"[^>]*title="([^"]+)"',
                        item_html, re.DOTALL
                    )
                if not name_match:
                    continue
                full_name = re.sub(r'<[^>]+>', "", name_match.group(1)).strip()

                # 偵測品牌（Amazon 商品有時在名稱開頭就帶品牌）
                detected_brand = self._detect_brand(full_name, brand_aliases)
                if not detected_brand:
                    continue

                # 價格
                price_match = re.search(
                    r'<span[^>]*class="a-price-whole"[^>]*>(\d+)</span>',
                    item_html
                )
                price = price_match.group(1) if price_match else None

                # 評分
                rating_match = re.search(
                    r'<span[^>]*class="a-icon-alt"[^>]*>([^<]+)</span>',
                    item_html
                )
                rating = rating_match.group(1).strip() if rating_match else None

                # 評論數
                reviews_match = re.search(
                    r'<span[^>]*class="a-size-base s-underline-text"[^>]*>\((\d+,?\d*)\)</span>',
                    item_html
                )
                if not reviews_match:
                    reviews_match = re.search(
                        r'(\d+,?\d*)\s+ratings',
                        item_html
                    )
                reviews = reviews_match.group(1) if reviews_match else None

                # 連結
                url_match = re.search(
                    r'<a[^>]*class="a-link-normal s-no-outline[^"]*"[^>]*href="([^"]+)"',
                    item_html
                )
                url = "https://www.amazon.com" + url_match.group(1) if url_match else ""

                # 瓦數
                wattage = self._extract_wattage(full_name)
                certification = self._extract_certification(full_name)

                products.append(ProductInfo(
                    platform=self.platform_name,
                    brand=detected_brand,
                    product_name=full_name[:200],
                    price=price,
                    currency="USD",
                    rating=rating,
                    sales_count=reviews,
                    url=url,
                    timestamp=datetime.now().isoformat(),
                    wattage=wattage,
                    certification=certification,
                ))
            except Exception as e:
                logger.debug(f"[Amazon] 解析商品失敗: {e}")

        return products

    def _detect_brand(self, text: str, brand_aliases: dict[str, str]) -> str | None:
        text_lower = text.lower()
        for alias, canonical in brand_aliases.items():
            if alias.lower() in text_lower:
                return canonical
        return None

    def _extract_wattage(self, text: str) -> str | None:
        m = re.search(r'(\d{3,4})\s*W', text, re.IGNORECASE)
        return m.group(1) + "W" if m else None

    def _extract_certification(self, text: str) -> str | None:
        cert_match = re.search(
            r'(80\s*plus\s*(?:Bronze|Silver|Gold|Platinum|Titanium))',
            text, re.IGNORECASE
        )
        return cert_match.group(1).replace(" ", "").title() if cert_match else None
