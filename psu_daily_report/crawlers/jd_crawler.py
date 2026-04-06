"""
京東 (JD.com) 爬蟲
URL: https://search.jd.com/Search?keyword=電源供應器
"""

import re
import logging
from datetime import datetime
from .base_crawler import BaseCrawler, ProductInfo

logger = logging.getLogger(__name__)


class JDCrawler(BaseCrawler):
    platform_name = "京東"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        # JD 每頁約 30 個商品，page 參數從 1 開始
        # encoding 參數很重要
        encoded = keyword.encode("gbk").decode("gbk")
        return (
            f"https://search.jd.com/Search?keyword={encoded}"
            f"&enc=utf-8&page={page}"
        )

    def parse_products(self, html: str, brands: list) -> list[ProductInfo]:
        products = []
        # 京東商品列表在 <li class="gl-item">...</li> 裡
        item_pattern = re.compile(r'<li class="gl-item"[^>]*>(.*?)</li>', re.DOTALL)
        items = item_pattern.findall(html)

        brand_names = [b["name"] for b in brands]
        brand_aliases: dict[str, str] = {}
        for b in brands:
            brand_aliases[b["name"]] = b["name"]
            for alias in b.get("aliases", []):
                brand_aliases[alias.lower()] = b["name"]

        for item_html in items:
            try:
                # 商品名稱
                name_match = re.search(
                    r'<div class="p-name p-name-type2">.*?<em>(.*?)</em>(.*?)</a>',
                    item_html, re.DOTALL
                )
                if not name_match:
                    continue
                full_name = name_match.group(1) + name_match.group(2)
                full_name = re.sub(r'<[^>]+>', "", full_name).strip()

                # 偵測品牌
                detected_brand = self._detect_brand(full_name, brand_aliases)
                if not detected_brand:
                    continue

                # 價格
                price_match = re.search(
                    r'<i class="price">.*?([\d,.]+)</i>', item_html
                )
                price = price_match.group(1) if price_match else None

                # 銷量（京東有確認收货數量）
                sales_match = re.search(
                    r'<div class="p-commit">.*?(\d+)[萬百千]?', item_html, re.DOTALL
                )
                sales = sales_match.group(0) if sales_match else None
                if sales:
                    sales = re.sub(r'<[^>]+>', "", sales).strip()

                # 商品連結
                url_match = re.search(
                    r'href="(//item\.jd\.com/\d+\.html[^"]*)"',
                    item_html
                )
                url = "https:" + url_match.group(1) if url_match else ""

                # 瓦數
                wattage = self._extract_wattage(full_name)

                products.append(ProductInfo(
                    platform=self.platform_name,
                    brand=detected_brand,
                    product_name=full_name[:200],
                    price=price,
                    currency="CNY",
                    sales_count=sales,
                    url=url,
                    timestamp=datetime.now().isoformat(),
                    wattage=wattage,
                ))
            except Exception as e:
                logger.debug(f"[京東] 解析商品失敗: {e}")

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
