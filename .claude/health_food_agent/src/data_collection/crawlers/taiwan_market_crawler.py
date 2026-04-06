"""
台湾市场行情爬虫 - 虾皮/乐天/PChome
"""
import asyncio
import json
import re
import random
import httpx
from typing import List, Dict, Optional
from .base_crawler import BaseCrawler
from loguru import logger


class TaiwanMarketCrawler(BaseCrawler):
    """台湾电商平台市场行情爬虫"""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.search_keywords = [
            "富硒米", "功能米", "降糖食品", "荞麦面",
            "燕麦", "糙米", "黑米", "青稞面", "代餐"
        ]

    async def crawl(self, platform: str = "shopee", keyword: str = None, **kwargs) -> List[Dict]:
        """爬取指定台湾电商平台"""
        if keyword is None:
            keyword = random.choice(self.search_keywords)

        if platform == "shopee":
            return await self._crawl_shopee(keyword)
        elif platform == "rakuten":
            return await self._crawl_rakuten(keyword)
        elif platform == "pchome":
            return await self._crawl_pchome(keyword)
        else:
            return []

    async def _crawl_shopee(self, keyword: str) -> List[Dict]:
        """爬取虾皮购物"""
        # 虾皮API
        url = "https://shopee.tw/api/v4/search/search_items"
        params = {
            "keyword": keyword,
            "by": "sales",
            "order": "desc",
            "limit": 50,
            "newest": 0,
            "categoryid": 0,
        }

        headers = self._get_headers()
        headers.update({
            "Accept": "application/json",
            "Referer": "https://shopee.tw/",
            "X-Shopee-Language": "zh-TW",
            "X-Requested-With": "XMLHttpRequest",
        })

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    results = self._parse_shopee_items(items, keyword)
                    logger.info(f"虾皮 {keyword} 解析到 {len(results)} 条")
                    return results
        except Exception as e:
            logger.error(f"虾皮爬取失败: {e}")

        # HTML备选方案
        return await self._crawl_shopee_html(keyword)

    async def _crawl_shopee_html(self, keyword: str) -> List[Dict]:
        """虾皮HTML解析备选"""
        search_url = f"https://shopee.tw/search?keyword={keyword}&sortBy=sales"
        html = await self._async_http_get(search_url)
        if not html:
            return []

        soup = self.parse_html(html)
        products = []

        for item in soup.select(".shopee-search-item"):
            try:
                p = {
                    "platform": "虾皮",
                    "name": "",
                    "price": 0.0,
                    "currency": "TWD",
                    "sales_count": 0,
                    "seller": "",
                    "rating": 0.0,
                    "location": "台湾",
                    "category": keyword,
                    "timestamp": "",
                }

                title_el = item.select_one(".Cve6f")
                if title_el:
                    p["name"] = title_el.get_text(strip=True)

                price_el = item.select_one("._1ApG6")
                if price_el:
                    price_text = re.sub(r"[^\d.]", "", price_el.get_text())
                    p["price"] = float(price_text) if price_text else 0

                sales_el = item.select_one(".rSVjs")
                if sales_el:
                    sales_text = re.sub(r"[^\d]", "", sales_el.get_text())
                    p["sales_count"] = int(sales_text) if sales_text else 0

                products.append(p)
            except:
                continue

        return products

    def _parse_shopee_items(self, items: List, keyword: str) -> List[Dict]:
        """解析虾皮API数据"""
        results = []
        for item in items:
            p = {
                "platform": "虾皮",
                "name": item.get("title", ""),
                "price": item.get("price", 0) / 100000 if item.get("price") else 0,
                "currency": "TWD",
                "sales_count": item.get("historical_sales", 0),
                "seller": item.get("shop_name", ""),
                "shopid": item.get("shopid", 0),
                "itemid": item.get("itemid", 0),
                "rating": item.get("item_rating", {}).get("rating_star", 0),
                "location": item.get("shop_location", "台湾"),
                "category": keyword,
                "price_before_discount": item.get("price_before_discount", 0) / 100000,
                "timestamp": str(asyncio.get_event_loop().time()),
            }
            results.append(p)
        return results

    async def _crawl_rakuten(self, keyword: str) -> List[Dict]:
        """爬取台湾乐天市场"""
        url = f"https://www.rakuten.com.tw/search/{keyword}/"
        headers = self._get_headers()
        headers["Accept-Language"] = "zh-TW"

        html = await self._async_http_get(url, headers=headers)
        if not html:
            return []

        soup = self.parse_html(html)
        products = []

        for item in soup.select(".search-result-item, .product-item"):
            try:
                p = {
                    "platform": "乐天",
                    "name": "",
                    "price": 0.0,
                    "currency": "TWD",
                    "sales_count": 0,
                    "seller": "",
                    "rating": 0.0,
                    "location": "台湾",
                    "category": keyword,
                    "timestamp": "",
                }

                title_el = item.select_one("h3, .title, .product-name")
                if title_el:
                    p["name"] = title_el.get_text(strip=True)

                price_el = item.select_one(".price, .product-price")
                if price_el:
                    price_text = re.sub(r"[^\d.]", "", price_el.get_text())
                    p["price"] = float(price_text) if price_text else 0

                products.append(p)
            except:
                continue

        logger.info(f"乐天 {keyword} 解析到 {len(products)} 条")
        return products

    async def _crawl_pchome(self, keyword: str) -> List[Dict]:
        """爬取PChome"""
        # PChome API
        url = f"https://ecshweb.pchome.com.tw/search/v3.3/all/results"
        params = {
            "q": keyword,
            "sort": "sale/D",
            "page": 1,
            "ind": "food",
        }

        html = await self._async_http_get(url, params=params)
        if not html:
            return []

        try:
            data = json.loads(html)
            prods = data.get("prods", [])
            results = []
            for item in prods:
                p = {
                    "platform": "PChome",
                    "name": item.get("Name", ""),
                    "price": float(item.get("Price", 0)),
                    "currency": "TWD",
                    "sales_count": 0,
                    "rating": 0.0,
                    "location": "台湾",
                    "category": keyword,
                    "timestamp": "",
                }
                results.append(p)
            logger.info(f"PChome {keyword} 解析到 {len(results)} 条")
            return results
        except:
            return []

    async def crawl_all_platforms(self) -> List[Dict]:
        """爬取所有台湾平台"""
        all_data = []
        platforms = ["shopee", "rakuten", "pchome"]
        for platform in platforms:
            for keyword in self.search_keywords[:3]:  # 每个平台限制3个关键词
                try:
                    data = await self.crawl(platform=platform, keyword=keyword)
                    all_data.extend(data)
                    await asyncio.sleep(1.5)
                except Exception as e:
                    logger.error(f"{platform} {keyword} 失败: {e}")
        return all_data

    async def get_market_price_ranges(self) -> Dict[str, Dict]:
        """获取各品类市场价格区间"""
        ranges = {}
        for keyword in self.search_keywords:
            try:
                data = await self.crawl(platform="shopee", keyword=keyword)
                if data:
                    prices = [p["price"] for p in data if p.get("price", 0) > 0]
                    if prices:
                        ranges[keyword] = {
                            "min": min(prices),
                            "max": max(prices),
                            "avg": sum(prices) / len(prices),
                            "count": len(prices),
                            "currency": "TWD",
                        }
                await asyncio.sleep(1)
            except Exception as e:
                logger.debug(f"价格区间 {keyword}: {e}")
        return ranges
