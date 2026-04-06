"""
天貓 (Tmall) 爬蟲
URL: https://list.tmall.com/search_product.htm?q=電源供應器
"""

import re
import logging
from datetime import datetime
from .base_crawler import BaseCrawler, ProductInfo

logger = logging.getLogger(__name__)


class TmallCrawler(BaseCrawler):
    platform_name = "天貓"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        encoded = keyword.encode("gbk").decode("gbk")
        return (
            f"https://list.tmall.com/search_product.htm?q={encoded}"
            f"&page={page}"
        )

    def get_headers(self) -> dict:
        headers = super().get_headers()
        headers["Referer"] = "https://www.tmall.com/"
        return headers

    def parse_products(self, html: str, brands: list) -> list[ProductInfo]:
        products = []

        brand_names = [b["name"] for b in brands]
        brand_aliases: dict[str, str] = {}
        for b in brands:
            brand_aliases[b["name"]] = b["name"]
            for alias in b.get("aliases", []):
                brand_aliases[alias.lower()] = b["name"]

        # 天貓商品在 <div class="product"> 或 <div class="item">
        item_pattern = re.compile(
            r'<div[^>]*class="product[^\"]*\s*[^>]*>(.*?)</div>\s*</div>',
            re.DOTALL
        )
        items = item_pattern.findall(html)
        if not items:
            # 備用 pattern
            item_pattern = re.compile(
                r'<div[^>]*class="item[^"]*"[^>]*>(.*?)</div>\s*</div>',
                re.DOTALL
            )
            items = item_pattern.findall(html)

        for item_html in items:
            try:
                # 商品名稱
                name_match = re.search(
                    r'<a[^>]*class="productTitle[^"]*"[^>]*>(.*?)</a>',
                    item_html, re.DOTALL
                )
                if not name_match:
                    name_match = re.search(
                        r'<p[^>]*class="title[^"]*"[^>]*>(.*?)</p>',
                        item_html, re.DOTALL
                    )
                if not name_match:
                    continue
                full_name = re.sub(r'<[^>]+>', "", name_match.group(1)).strip()

                detected_brand = self._detect_brand(full_name, brand_aliases)
                if not detected_brand:
                    continue

                # 價格
                price_match = re.search(
                    r'<em[^>]*class="price[^"]*"[^>]*>.*?(\d+\.?\d*)</em>',
                    item_html, re.DOTALL
                )
                if not price_match:
                    price_match = re.search(
                        r'(&yen|¥)\s*(\d+\.?\d*)', item_html
                    )
                price = price_match.group(2) if price_match else (
                    price_match.group(1) if price_match else None
                )

                # 銷量
                sales_match = re.search(
                    r'<em[^>]*class="sale-num[^"]*"[^>]*>(\d+)</em>',
                    item_html, re.DOTALL
                )
                sales = sales_match.group(1) if sales_match else None

                # 店鋪名稱（作為賣家）
                shop_match = re.search(
                    r'<a[^>]*class="productShop-name[^"]*"[^>]*>(.*?)</a>',
                    item_html, re.DOTALL
                )
                seller = re.sub(r'<[^>]+>', "", shop_match.group(1)).strip() if shop_match else None

                # 連結
                url_match = re.search(
                    r'<a[^>]*class="productTitle[^"]*"[^>]*href="([^"]+)"',
                    item_html
                )
                if not url_match:
                    url_match = re.search(r'href="(//detail[^"]+)"', item_html)
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
                    seller=seller,
                    url=url,
                    timestamp=datetime.now().isoformat(),
                    wattage=wattage,
                ))
            except Exception as e:
                logger.debug(f"[天貓] 解析商品失敗: {e}")

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
