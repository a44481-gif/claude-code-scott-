"""
竞争对手分析爬虫
"""
import asyncio
import json
import re
import httpx
from typing import List, Dict, Optional
from .base_crawler import BaseCrawler
from loguru import logger


class CompetitorCrawler(BaseCrawler):
    """台湾健康食品竞争对手爬虫"""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        # 台湾主要健康食品品牌
        self.competitors = {
            # 台湾本地品牌
            "联华食品": "https://www.lianhua.com.tw",
            "新东阳": "https://www.sintong.com.tw",
            "黑橋牌": "https://www.heqiao.com.tw",
            "泉发": "https://www.chuanfa.com.tw",
            "新光三越食品": "https://www.skc.com.tw",
            # 日本进口品牌
            "YAMAKI": "https://www.yamaki.jp",
            "神明味噌": "https://www.shinmei.co.jp",
            # 知名健康食品电商
            "大医生技": "https://www.yiteng.tw",
            "娘家": "https://www.niangg.com",
            "葡萄王": "https://www.grapeking.com.tw",
        }
        self.search_terms = ["富硒米", "功能米", "降糖食品", "健康面食", "营养代餐"]

    async def crawl(self, competitor_name: str = None, **kwargs) -> List[Dict]:
        """爬取竞争对手信息"""
        if competitor_name:
            return await self._crawl_competitor(competitor_name)
        else:
            return await self._crawl_all_competitors()

    async def _crawl_competitor(self, name: str) -> List[Dict]:
        """爬取单个竞争对手"""
        url = self.competitors.get(name, "")
        if not url:
            return []

        # 尝试搜索该品牌在虾皮的产品
        return await self._search_competitor_on_shopee(name)

    async def _crawl_all_competitors(self) -> List[Dict]:
        """爬取所有竞争对手"""
        all_data = []
        for name in self.competitors.keys():
            try:
                data = await self._crawl_competitor(name)
                all_data.extend(data)
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"竞争对手 {name} 爬取失败: {e}")
        return all_data

    async def _search_competitor_on_shopee(self, brand: str) -> List[Dict]:
        """在虾皮搜索竞争对手产品"""
        keyword = f"{brand} 健康食品"
        url = "https://shopee.tw/api/v4/search/search_items"
        params = {
            "keyword": brand,
            "by": "sales",
            "order": "desc",
            "limit": 20,
            "newest": 0,
        }

        headers = self._get_headers()
        headers.update({
            "Accept": "application/json",
            "Referer": "https://shopee.tw/",
            "X-Shopee-Language": "zh-TW",
        })

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    results = []
                    for item in items:
                        results.append({
                            "competitor": brand,
                            "name": item.get("title", ""),
                            "price": item.get("price", 0) / 100000 if item.get("price") else 0,
                            "currency": "TWD",
                            "sales_count": item.get("historical_sales", 0),
                            "rating": item.get("item_rating", {}).get("rating_star", 0),
                            "shop_name": item.get("shop_name", ""),
                            "shop_location": item.get("shop_location", ""),
                            "platform": "虾皮",
                            "timestamp": str(asyncio.get_event_loop().time()),
                        })
                    logger.info(f"竞争对手 {brand} 在虾皮找到 {len(results)} 个产品")
                    return results
        except Exception as e:
            logger.error(f"虾皮搜索 {brand} 失败: {e}")
        return []

    async def get_competitive_pricing(self) -> Dict:
        """获取竞争对手价格策略"""
        pricing_data = {}
        for term in self.search_terms:
            try:
                url = "https://shopee.tw/api/v4/search/search_items"
                params = {
                    "keyword": term,
                    "by": "price",
                    "order": "asc",
                    "limit": 50,
                }

                headers = self._get_headers()
                headers.update({
                    "Accept": "application/json",
                    "Referer": "https://shopee.tw/",
                    "X-Shopee-Language": "zh-TW",
                })

                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(url, params=params, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get("items", [])
                        prices = [item.get("price", 0) / 100000 for item in items if item.get("price")]
                        if prices:
                            pricing_data[term] = {
                                "lowest": min(prices),
                                "highest": max(prices),
                                "avg": sum(prices) / len(prices),
                                "count": len(prices),
                            }
                await asyncio.sleep(1.5)
            except Exception as e:
                logger.debug(f"价格策略 {term}: {e}")
        return pricing_data

    async def analyze_competitor_landscape(self) -> Dict:
        """分析竞争格局"""
        market_data = await self.get_competitive_pricing()

        # 获取各品类的TOP销售产品
        top_products = {}
        for term in self.search_terms:
            try:
                url = "https://shopee.tw/api/v4/search/search_items"
                params = {
                    "keyword": term,
                    "by": "sales",
                    "order": "desc",
                    "limit": 10,
                }

                headers = self._get_headers()
                headers.update({
                    "Accept": "application/json",
                    "Referer": "https://shopee.tw/",
                    "X-Shopee-Language": "zh-TW",
                })

                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(url, params=params, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get("items", [])
                        top_products[term] = [
                            {
                                "name": item.get("title", ""),
                                "shop_name": item.get("shop_name", ""),
                                "price": item.get("price", 0) / 100000,
                                "sales": item.get("historical_sales", 0),
                            }
                            for item in items[:5]
                        ]
                await asyncio.sleep(1.5)
            except Exception as e:
                logger.debug(f"TOP产品 {term}: {e}")

        return {
            "price_ranges": market_data,
            "top_products": top_products,
            "competitors": list(self.competitors.keys()),
            "analysis_date": str(asyncio.get_event_loop().time()),
        }
