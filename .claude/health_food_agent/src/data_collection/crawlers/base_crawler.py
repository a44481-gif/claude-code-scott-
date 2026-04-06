"""
通用爬虫基类 - 支持代理IP + Cookies
"""
import httpx
import asyncio
import random
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
from bs4 import BeautifulSoup
from loguru import logger
from abc import ABC, abstractmethod


class BaseCrawler(ABC):
    """爬虫基类 - 支持代理IP + Cookies"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.timeout = self.config.get("timeout", 30)
        self.max_retries = self.config.get("retry_times", 3)
        self.concurrency = self.config.get("concurrency", 3)

        # 代理配置 - B方案
        self.proxies = self.config.get("proxies", [])

        # Cookies配置 - B方案
        self.cookies = self.config.get("cookies", {})

        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        self.session = None
        self._rate_limit_delay = 1.0

    def _get_headers(self) -> Dict[str, str]:
        """生成随机请求头"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """获取代理"""
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return {
            "http://": proxy,
            "https://": proxy,
        }

    def _merge_cookies(self, additional_cookies: Dict = None) -> Dict:
        """合并Cookies"""
        merged = dict(self.cookies)
        if additional_cookies:
            merged.update(additional_cookies)
        return merged

    async def _async_http_get(self, url: str, headers: Optional[Dict] = None,
                              cookies: Optional[Dict] = None, **kwargs) -> Optional[str]:
        """异步HTTP GET请求"""
        headers = headers or self._get_headers()
        cookies = self._merge_cookies(cookies)

        for attempt in range(self.max_retries):
            try:
                proxy = self._get_proxy()
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(
                        url,
                        headers=headers,
                        cookies=cookies,
                        proxies=proxy,
                        **kwargs
                    )
                    if response.status_code == 200:
                        await asyncio.sleep(self._rate_limit_delay)
                        return response.text
                    elif response.status_code == 403:
                        logger.warning(f"403 禁止访问: {url}")
                        await asyncio.sleep(5 * (attempt + 1))
                    elif response.status_code == 404:
                        logger.warning(f"404 未找到: {url}")
                        return None
                    else:
                        logger.warning(f"状态码 {response.status_code}: {url}")
            except Exception as e:
                logger.error(f"请求失败 (尝试 {attempt+1}/{self.max_retries}): {url} - {e}")
                await asyncio.sleep(2 ** attempt)

        return None

    def _sync_http_get(self, url: str, headers: Optional[Dict] = None,
                       cookies: Optional[Dict] = None, **kwargs) -> Optional[str]:
        """同步HTTP GET请求"""
        headers = headers or self._get_headers()
        cookies = self._merge_cookies(cookies)

        for attempt in range(self.max_retries):
            try:
                proxy = self._get_proxy()
                response = httpx.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    proxies=proxy,
                    timeout=self.timeout,
                    follow_redirects=True
                )
                if response.status_code == 200:
                    time.sleep(self._rate_limit_delay)
                    return response.text
                elif response.status_code == 403:
                    logger.warning(f"403 禁止访问: {url}")
                    time.sleep(5 * (attempt + 1))
                else:
                    logger.warning(f"状态码 {response.status_code}: {url}")
            except Exception as e:
                logger.error(f"请求失败 (尝试 {attempt+1}/{self.max_retries}): {url} - {e}")
                time.sleep(2 ** attempt)
        return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """解析HTML"""
        return BeautifulSoup(html, "lxml")

    def extract_json(self, text: str, key: str) -> Optional[Any]:
        """从页面中提取JSON数据"""
        import re
        pattern = r'\{[^{}]*"' + re.escape(key) + r'"[^{}]*\}'
        matches = re.findall(pattern, text)
        if matches:
            import json
            try:
                return json.loads(matches[0])
            except:
                pass
        return None

    @abstractmethod
    async def crawl(self, **kwargs) -> List[Dict]:
        """子类必须实现的爬取逻辑"""
        pass

    async def run(self, **kwargs) -> List[Dict]:
        """爬虫执行入口"""
        logger.info(f"开始爬取: {self.__class__.__name__}")
        if self.proxies:
            logger.info(f"使用代理: {len(self.proxies)} 个代理")
        start = datetime.now()
        try:
            results = await self.crawl(**kwargs)
            elapsed = (datetime.now() - start).total_seconds()
            logger.info(f"爬取完成: {len(results)} 条记录, 耗时 {elapsed:.1f}秒")
            return results
        except Exception as e:
            logger.error(f"爬取异常: {e}")
            return []
