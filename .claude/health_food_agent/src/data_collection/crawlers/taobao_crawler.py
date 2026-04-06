"""
淘宝/1688 健康食品爬虫
"""
import asyncio
import json
import re
from typing import List, Dict, Optional
from .base_crawler import BaseCrawler
from loguru import logger


class ProductInfo:
    """产品信息数据结构"""

    def __init__(self):
        self.name = ""
        self.price = 0.0
        self.currency = "CNY"
        self.sales_count = 0
        self.seller = ""
        self.seller_rating = 0.0
        self.location = ""
        self.url = ""
        self.platform = ""
        self.category = ""
        self.images = []
        self.shipping = ""
        self.min_order = 1
        self.certification = ""
        self.weight = ""
        self.shelf_life = ""
        self.nutrition_info = {}
        self.timestamp = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "sales_count": self.sales_count,
            "seller": self.seller,
            "seller_rating": self.seller_rating,
            "location": self.location,
            "url": self.url,
            "platform": self.platform,
            "category": self.category,
            "images": self.images,
            "shipping": self.shipping,
            "min_order": self.min_order,
            "certification": self.certification,
            "weight": self.weight,
            "shelf_life": self.shelf_life,
            "nutrition_info": self.nutrition_info,
            "timestamp": self.timestamp,
        }


class TaobaoCrawler(BaseCrawler):
    """淘宝/1688 健康食品爬虫"""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.platform = "1688"  # 默认1688
        self.search_keywords = [
            "富硒米 5kg", "功能米 东北", "降糖米饭 主食",
            "荞麦面 全麦", "燕麦面 低GI", "青稞面 健康",
            "糙米 有机", "黑米 营养", "藜麦 进口", "代餐粉 营养"
        ]

    def set_platform(self, platform: str):
        self.platform = platform

    async def crawl(self, keyword: str = None, page: int = 1, **kwargs) -> List[Dict]:
        """爬取1688/淘宝产品"""
        if keyword is None:
            keyword = random.choice(self.search_keywords) if self.platform == "1688" else "富硒米"

        logger.info(f"爬取 {self.platform} 关键词: {keyword} 页码: {page}")

        if self.platform == "1688":
            return await self._crawl_1688(keyword, page)
        else:
            return await self._crawl_taobao(keyword, page)

    async def _crawl_1688(self, keyword: str, page: int) -> List[Dict]:
        """爬取1688批发平台"""
        # 1688移动端API - 更稳定
        api_url = f"https://m.1688.com/winport/asyncsearch.json"
        params = {
            "keyword": keyword,
            "beginPage": page,
            "pageSize": 20,
            "functionName": "offerlist_winport_search_v2",
        }

        headers = self._get_headers()
        headers.update({
            "Referer": "https://www.1688.com/",
            "Accept": "application/json",
        })

        html = await self._async_http_get(api_url, params=params, headers=headers)
        if not html:
            return []

        try:
            data = json.loads(html)
            items = data.get("result", {}).get("offerList", [])
        except json.JSONDecodeError:
            items = self._parse_html_items(html)

        products = []
        for item in items:
            p = ProductInfo()
            p.platform = "1688"
            p.name = item.get("title", "") or item.get("subject", "")
            p.price = float(item.get("price", 0))
            p.sales_count = int(item.get("saleCount", 0) or 0)
            p.seller = item.get("memberName", "") or item.get("companyName", "")
            p.location = item.get("location", "")
            p.url = f"https://detail.1688.com/offer/{item.get('id', '')}.html"
            p.category = keyword
            p.weight = item.get("weight", "")
            p.images = item.get("images", [])
            p.timestamp = str(asyncio.get_event_loop().time())
            products.append(p.to_dict())

        logger.info(f"1688 解析到 {len(products)} 条产品")
        return products

    def _parse_html_items(self, html: str) -> List[Dict]:
        """HTML解析模式(备选)"""
        soup = self.parse_html(html)
        items = []
        # 尝试多种选择器
        for card in soup.select(".offer-item, .list-item, .search-item, [data-id]"):
            try:
                item = {
                    "id": card.get("data-id", ""),
                    "title": card.select_one(".title, .name, .subject, h3") and card.select_one(".title, .name, .subject, h3").get_text(strip=True),
                    "price": re.search(r"[\d.]+", card.select_one(".price, .amount") and card.select_one(".price, .amount").get_text() or "0").group() if card.select_one(".price, .amount") else "0",
                    "saleCount": re.search(r"(\d+)", card.select_one(".sale, .sales, .num") and card.select_one(".sale, .sales, .num").get_text() or "0").group() if card.select_one(".sale, .sales, .num") else "0",
                }
                items.append(item)
            except:
                continue
        return items

    async def _crawl_taobao(self, keyword: str, page: int) -> List[Dict]:
        """爬取淘宝零售平台"""
        # 淘宝搜索API
        url = f"https://s.taobao.com/search"
        params = {
            "q": keyword,
            "page": page,
            "sort": "sale-desc",
        }

        headers = self._get_headers()
        headers["Referer"] = "https://www.taobao.com/"

        html = await self._async_http_get(url, params=params, headers=headers)
        if not html:
            return []

        soup = self.parse_html(html)
        products = []

        for item in soup.select(".item, .product-item"):
            try:
                p = ProductInfo()
                p.platform = "淘宝"
                title_el = item.select_one(".title, .productTitle")
                p.name = title_el.get_text(strip=True) if title_el else ""

                price_el = item.select_one(".price, .g_price")
                if price_el:
                    price_text = re.search(r"[\d.]+", price_el.get_text())
                    p.price = float(price_text.group()) if price_text else 0

                sales_el = item.select_one(".sale, .deal")
                if sales_el:
                    sales_text = re.search(r"(\d+)", sales_el.get_text())
                    p.sales_count = int(sales_text.group()) if sales_text else 0

                location_el = item.select_one(".location, .item-location")
                p.location = location_el.get_text(strip=True) if location_el else ""

                p.category = keyword
                p.timestamp = str(asyncio.get_event_loop().time())
                products.append(p.to_dict())
            except Exception as e:
                logger.debug(f"解析单项失败: {e}")
                continue

        logger.info(f"淘宝解析到 {len(products)} 条产品")
        return products

    async def crawl_all_keywords(self) -> List[Dict]:
        """爬取所有关键词"""
        all_products = []
        for keyword in self.search_keywords:
            try:
                products = await self.crawl(keyword=keyword, page=1)
                all_products.extend(products)
                await asyncio.sleep(2)  # 避免请求过快
            except Exception as e:
                logger.error(f"关键词 {keyword} 爬取失败: {e}")
        return all_products


# 便捷函数
async def crawl_health_food_products(config: Optional[Dict] = None) -> List[Dict]:
    """快速爬取健康食品产品"""
    crawler = TaobaoCrawler(config)
    return await crawler.crawl_all_keywords()
