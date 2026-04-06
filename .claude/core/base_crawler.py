"""
Unified Base Crawler - Hybrid sync/async HTTP crawler with retry, proxy, cookies, and rate-limiting.
Merges patterns from:
  - msi_psu_automation: requests + Selenium with human-scroll simulation
  - health_food_agent: httpx async with proxy rotation
"""
import httpx
import asyncio
import random
import time
import re
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from loguru import logger
import traceback

# Optional Selenium support
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


@dataclass
class CrawlerConfig:
    """Crawler configuration"""
    timeout: int = 30
    retry_times: int = 3
    concurrency: int = 5
    delay: float = 1.0  # Rate limit delay between requests
    proxies: List[str] = field(default_factory=list)
    cookies: Dict[str, str] = field(default_factory=dict)
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91",
    ])

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "CrawlerConfig":
        user_agents_cfg = config.get("user_agents")
        return cls(
            timeout=config.get("timeout", 30),
            retry_times=config.get("retry_times", 3),
            concurrency=config.get("concurrency", 5),
            delay=config.get("delay", 1.0),
            proxies=config.get("proxies", []),
            cookies=config.get("cookies", {}),
            # Only override default if config provides a non-empty list
            user_agents=(
                user_agents_cfg
                if isinstance(user_agents_cfg, list) and len(user_agents_cfg) > 0
                else [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                ]
            ),
        )


class BaseCrawler(ABC):
    """
    Unified crawler base class supporting both sync and async HTTP requests,
    with Selenium fallback for JavaScript-rendered pages.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = CrawlerConfig.from_dict(config or {})
        self.session: Optional[httpx.AsyncClient] = None
        self.driver = None
        self.results: List[Dict] = []
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "start_time": datetime.now(),
        }

    # ── HTTP Helpers ───────────────────────────────────────────

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(self.config.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _get_proxy(self) -> Optional[str]:
        if not self.config.proxies:
            return None
        return random.choice(self.config.proxies)  # single proxy URL string

    def _merge_cookies(self, extra: Dict[str, str] = None) -> Dict[str, str]:
        merged = dict(self.config.cookies)
        if extra:
            merged.update(extra)
        return merged

    # ── Async HTTP GET ─────────────────────────────────────────

    async def async_http_get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Optional[str]:
        """Async HTTP GET with retry and proxy rotation."""
        headers = headers or self._get_headers()
        cookies = self._merge_cookies(cookies)
        self.stats["total_requests"] += 1

        for attempt in range(self.config.retry_times):
            try:
                proxy = self._get_proxy()
                async with httpx.AsyncClient(
                    proxy=proxy,
                    timeout=self.config.timeout,
                    follow_redirects=True,
                    headers=headers,
                    cookies=cookies,
                ) as client:
                    response = await client.get(url, **kwargs)
                    if response.status_code == 200:
                        self.stats["successful_requests"] += 1
                        await asyncio.sleep(self.config.delay)
                        return response.text
                    elif response.status_code == 403:
                        logger.warning(f"[{self.__class__.__name__}] 403 禁止访问: {url}")
                        await asyncio.sleep(5 * (attempt + 1))
                    elif response.status_code == 404:
                        logger.warning(f"[{self.__class__.__name__}] 404 未找到: {url}")
                        return None
                    else:
                        logger.warning(f"[{self.__class__.__name__}] 状态码 {response.status_code}: {url}")
            except httpx.TimeoutException:
                logger.warning(f"[{self.__class__.__name__}] 超时 (尝试 {attempt+1}/{self.config.retry_times}): {url}")
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] 请求异常 (尝试 {attempt+1}/{self.config.retry_times}): {url} - {e}")
                await asyncio.sleep(2 ** attempt)

        self.stats["failed_requests"] += 1
        return None

    # ── Sync HTTP GET ──────────────────────────────────────────

    def sync_http_get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Optional[str]:
        """Sync HTTP GET with retry and proxy rotation."""
        headers = headers or self._get_headers()
        cookies = self._merge_cookies(cookies)
        self.stats["total_requests"] += 1

        for attempt in range(self.config.retry_times):
            try:
                proxy = self._get_proxy()
                response = httpx.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    proxy=proxy,
                    timeout=self.config.timeout,
                    follow_redirects=True,
                )
                if response.status_code == 200:
                    self.stats["successful_requests"] += 1
                    time.sleep(self.config.delay)
                    return response.text
                elif response.status_code == 403:
                    logger.warning(f"[{self.__class__.__name__}] 403: {url}")
                    time.sleep(5 * (attempt + 1))
                elif response.status_code == 404:
                    logger.warning(f"[{self.__class__.__name__}] 404: {url}")
                    return None
                else:
                    logger.warning(f"[{self.__class__.__name__}] 状态码 {response.status_code}: {url}")
            except httpx.TimeoutException:
                logger.warning(f"[{self.__class__.__name__}] 超时: {url}")
                time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] 请求异常: {url} - {e}")
                time.sleep(2 ** attempt)

        self.stats["failed_requests"] += 1
        return None

    # ── Selenium ───────────────────────────────────────────────

    def setup_selenium(self, headless: bool = True):
        """Initialize Selenium WebDriver with anti-detection."""
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium 未安装，跳过 Selenium 设置")
            return

        try:
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            options = Options()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument("--disable-blink-features=AutomationControlled")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Selenium 驱动初始化成功")
        except Exception as e:
            logger.error(f"Selenium 初始化失败: {e}")
            self.driver = None

    def selenium_get(self, url: str, wait_selector: str = "body", scroll: bool = True) -> Optional[str]:
        """Fetch page using Selenium with human-like scroll."""
        if not self.driver:
            self.setup_selenium()
            if not self.driver:
                return None

        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
            )
            if scroll:
                self._simulate_human_scroll()
            time.sleep(random.uniform(1, 3))
            return self.driver.page_source
        except (TimeoutException, WebDriverException) as e:
            logger.error(f"Selenium 获取页面失败: {e}")
            return None

    def _simulate_human_scroll(self):
        """Simulate human scrolling behavior."""
        try:
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            current = 0
            step = random.randint(300, 600)
            while current < total_height:
                self.driver.execute_script(f"window.scrollTo(0, {current});")
                current += step
                time.sleep(random.uniform(0.5, 1.5))
            self.driver.execute_script("window.scrollTo(0, 0);")
        except Exception as e:
            logger.warning(f"模拟滚动失败: {e}")

    # ── HTML Parsing ───────────────────────────────────────────

    def parse_html(self, html: str, parser: str = "lxml") -> Optional[BeautifulSoup]:
        if not html:
            return None
        try:
            return BeautifulSoup(html, parser)
        except Exception as e:
            logger.error(f"HTML 解析失败: {e}")
            return None

    # ── Text Extraction Helpers ────────────────────────────────

    @staticmethod
    def extract_text(element, strip: bool = True) -> str:
        if element:
            text = element.get_text(strip=strip)
            return text if text else ""
        return ""

    @staticmethod
    def extract_float(text: str) -> Optional[float]:
        try:
            cleaned = "".join(c for c in text if c.isdigit() or c in [".", ","])
            cleaned = cleaned.replace(",", "")
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def extract_int(text: str) -> Optional[int]:
        val = BaseCrawler.extract_float(text)
        return int(val) if val is not None else None

    @staticmethod
    def clean_price(text: str) -> Optional[float]:
        """Extract price from text like '$1,299.00' or 'NT$12,800'."""
        patterns = [
            r"[\$¥€£]?\s*([\d,]+(?:\.\d{2})?)",
            r"([\d,]+(?:\.\d{2})?)\s*[\$¥€£]?",
            r"NT\$?\s*([\d,]+)",
            r"CNY\s*([\d,]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text.replace(",", ""))
            if match:
                try:
                    return float(match.group(1).replace(",", ""))
                except ValueError:
                    continue
        return None

    # ── Crawl Result ─────────────────────────────────────────

    def add_result(self, item: Dict):
        self.results.append(item)

    def get_results(self) -> List[Dict]:
        return self.results

    def clear_results(self):
        self.results = []

    def get_stats(self) -> Dict[str, Any]:
        elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
        return {
            **self.stats,
            "elapsed_seconds": elapsed,
            "success_rate": (
                self.stats["successful_requests"] / self.stats["total_requests"]
                if self.stats["total_requests"] > 0
                else 0
            ),
        }

    # ── Cleanup ───────────────────────────────────────────────

    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium 驱动已关闭")
            except Exception as e:
                logger.error(f"关闭 Selenium 失败: {e}")
        self.stats["start_time"] = datetime.now()

    # ── Abstract crawl method ─────────────────────────────────

    @abstractmethod
    async def crawl(self, **kwargs) -> List[Dict]:
        """子类必须实现的异步爬取逻辑。返回 [{...}, ...] 格式的列表。"""
        pass

    async def run(self, **kwargs) -> List[Dict]:
        """标准运行入口。"""
        logger.info(f"[{self.__class__.__name__}] 开始爬取...")
        start = datetime.now()
        try:
            self.results = await self.crawl(**kwargs)
            elapsed = (datetime.now() - start).total_seconds()
            logger.info(
                f"[{self.__class__.__name__}] 爬取完成: {len(self.results)} 条记录, "
                f"耗时 {elapsed:.1f}秒, 成功率 {self.get_stats()['success_rate']:.1%}"
            )
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] 爬取异常: {e}\n{traceback.format_exc()}")
            self.results = []
        return self.results
