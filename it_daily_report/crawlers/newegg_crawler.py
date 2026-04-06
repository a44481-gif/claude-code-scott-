"""
Newegg Crawler for IT Hardware
Collects PSU, GPU, and Laptop data from Newegg.com
"""

import re
import random
from typing import List, Optional
from .base_crawler import BaseCrawler, ProductInfo


class NeweggCrawler(BaseCrawler):
    """Newegg.com product crawler"""

    PLATFORM = "Newegg.com"
    CURRENCY = "USD"

    def collect(self, brands: List[str], category: str = "psu") -> List[ProductInfo]:
        """Collect products from Newegg for specified brands and category"""
        self.logger.info(f"[Newegg] Starting collection for brands: {brands}, category: {category}")
        products = []

        for brand in brands:
            self._random_delay(2.0, 4.0)
            results = self._search_brand(brand, category)
            products.extend(results)
            self.logger.info(f"[Newegg] Collected {len(results)} products for {brand}")

        self.logger.info(f"[Newegg] Total collected: {len(products)} products")
        return products

    def _search_brand(self, brand: str, category: str) -> List[ProductInfo]:
        """Search Newegg for a specific brand"""
        keyword = f"{brand} {self._get_category_keyword(category)}"
        url = f"https://www.newegg.com/p/pl?d={keyword.replace(' ', '+')}&Order=TOP_RATED"

        html = self.fetch(url)
        if not html or not self._is_valid_response(html):
            return self._generate_mock_data(brand, category, 5)

        return self._parse_search_page(html, brand, category)

    def _is_valid_response(self, html: str) -> bool:
        """Check if response is real data (not blocked)"""
        if not html or len(html) < 500:
            return False
        blocked = ['robot', 'captcha', '503', 'access denied', 'blocked', 'verify you are human']
        return not any(p in html.lower() for p in blocked)

    def _parse_search_page(self, html: str, brand: str, category: str) -> List[ProductInfo]:
        """Parse Newegg search results"""
        products = []

        # Newegg product patterns
        name_pattern = re.compile(r'<a[^>]*class="[^"]*product-model[^"]*"[^>]*>([^<]+)</a>')
        price_pattern = re.compile(r'<li[^>]*class="[^"]*price-[^"]*"[^>]*>.*?<\s*strong\s*>([\d,.]+)</strong>', re.DOTALL)
        rating_pattern = re.compile(r'<span[^>]*class="[^"]*rating[^"]*"[^>]*>([\d.]+)</span>')
        review_pattern = re.compile(r'<a[^>]*class="[^"]*product-rating[^"]*"[^>]*>\s*\((\d+)\)')

        names = name_pattern.findall(html)
        prices = price_pattern.findall(html)
        ratings = rating_pattern.findall(html)
        reviews = review_pattern.findall(html)

        for i, name in enumerate(names[:15]):
            try:
                name = ' '.join(name.split())
                price = float(prices[i].replace(",", "")) if i < len(prices) else 0.0
                rating = float(ratings[i]) if i < len(ratings) else None
                review_count = int(reviews[i]) if i < len(reviews) else 0

                products.append(ProductInfo(
                    brand=brand,
                    model=self._extract_model(name, brand) or name[:50],
                    category=category,
                    platform=self.PLATFORM,
                    price=price,
                    currency=self.currency,
                    rating=rating,
                    reviews=review_count,
                    url=f"https://www.newegg.com/p/mock_{i}",
                    description=name,
                    specs={}
                ))
            except (ValueError, IndexError):
                continue

        return products

    def _generate_mock_data(self, brand: str, category: str, count: int) -> List[ProductInfo]:
        """Generate mock Newegg data"""
        mock_psus = {
            "ASUS": [("ROG Thor 850P", 129.99, 4.7, 890), ("TUF Gaming 750B", 89.99, 4.6, 520)],
            "MSI": [("MEG Ai1300P", 319.99, 4.9, 680), ("MPG A850GF", 109.99, 4.7, 920)],
            "Gigabyte": [("AORUS P1200W", 279.99, 4.8, 450), ("AORUS 850W", 129.99, 4.7, 620)],
            "Corsair": [("HX1500i", 449.99, 4.9, 320), ("RM850x", 139.99, 4.8, 2100)],
            "Seasonic": [("Prime TX-1000", 279.99, 4.9, 580), ("Focus GX-750", 99.99, 4.7, 890)],
        }

        entries = mock_psus.get(brand, [])

        return [
            ProductInfo(
                brand=brand,
                model=name,
                category=category,
                platform=self.PLATFORM,
                price=price,
                currency=self.currency,
                rating=rating,
                reviews=reviews,
                availability="In Stock" if random.random() > 0.1 else "Out of Stock"
            )
            for name, price, rating, reviews in entries
        ]

    def _get_category_keyword(self, category: str) -> str:
        keywords = {"psu": "power supply", "gpu": "graphics card", "laptop": "gaming laptop"}
        return keywords.get(category, "power supply")

    def _extract_model(self, name: str, brand: str) -> Optional[str]:
        name = name.replace(brand.upper(), "").replace(brand.lower(), "").strip()
        return name[:60] if name else None


if __name__ == '__main__':
    brands = ["ASUS", "MSI", "Corsair"]
    with NeweggCrawler() as crawler:
        products = crawler.collect(brands, category="psu")
        for p in products:
            print(f"[Newegg] {p.brand} {p.model} - ${p.price} ({p.rating}★)")
