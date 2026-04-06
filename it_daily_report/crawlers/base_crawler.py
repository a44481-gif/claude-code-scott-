"""
Base Crawler for IT Hardware Daily Report
Provides httpx-based HTTP client with retry, anti-detection, and logging
"""

import os
import sys
import time
import random
import logging
import httpx
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import config
try:
    import json
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.json')
    if os.path.exists(config_path):
        with open(config_path, encoding='utf-8') as f:
            CONFIG = json.load(f)
    else:
        CONFIG = {}
except Exception:
    CONFIG = {}


@dataclass
class ProductInfo:
    """Standardized product data structure"""
    brand: str
    model: str
    category: str
    platform: str
    price: float
    currency: str = "USD"
    rating: Optional[float] = None
    reviews: Optional[int] = None
    sales: Optional[int] = None
    availability: str = "In Stock"
    url: str = ""
    image_url: str = ""
    description: str = ""
    specs: Dict[str, str] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]


class BaseCrawler(ABC):
    """Abstract base crawler with httpx + retry + anti-detection"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = self._setup_logger()
        self._client: Optional[httpx.Client] = None
        self.session_id = random.randint(1000, 9999)

        # Load from global config
        self.timeout = self.config.get('request_timeout', CONFIG.get('data_collection', {}).get('request_timeout', 30))
        self.max_retries = self.config.get('retry_attempts', CONFIG.get('data_collection', {}).get('retry_attempts', 3))
        self.retry_delay = self.config.get('retry_delay', CONFIG.get('data_collection', {}).get('retry_delay', 5))
        self.delay_between = self.config.get('delay_between_requests', CONFIG.get('data_collection', {}).get('delay_between_requests', 2))

    def _setup_logger(self) -> logging.Logger:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(
                f'%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%H:%M:%S'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.timeout,
                follow_redirects=True,
                headers={'User-Agent': random.choice(USER_AGENTS)}
            )
        return self._client

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        time.sleep(random.uniform(min_sec, max_sec))

    def _rotate_user_agent(self):
        if self._client:
            self._client.headers['User-Agent'] = random.choice(USER_AGENTS)

    def fetch(self, url: str, use_proxy: bool = False) -> Optional[str]:
        """Fetch a URL with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self._rotate_user_agent()
                response = self.client.get(url, timeout=self.timeout)
                response.raise_for_status()
                self.logger.debug(f"[{self.__class__.__name__}] Fetched: {url} ({response.status_code})")
                return response.text
            except httpx.HTTPStatusError as e:
                self.logger.warning(f"[{self.__class__.__name__}] HTTP {e.response.status_code} for {url} (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
            except Exception as e:
                self.logger.warning(f"[{self.__class__.__name__}] Error fetching {url}: {e} (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        return None

    def post(self, url: str, data: Dict, headers: Optional[Dict] = None) -> Optional[str]:
        """POST request with retry"""
        for attempt in range(self.max_retries):
            try:
                self._rotate_user_agent()
                response = self.client.post(url, data=data, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except Exception as e:
                self.logger.warning(f"[{self.__class__.__name__}] POST error {url}: {e} (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        return None

    @abstractmethod
    def collect(self, brands: List[str], category: str = "psu") -> List[ProductInfo]:
        """Main collection method — must be implemented by subclasses"""
        pass

    def save_results(self, products: List[ProductInfo], filename: Optional[str] = None) -> str:
        """Save collected products to JSON file"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.__class__.__name__.replace('Crawler', '').lower()}_{timestamp}.json"
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([p.to_dict() for p in products], f, ensure_ascii=False, indent=2)
        self.logger.info(f"Saved {len(products)} products to {filepath}")
        return filepath

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def merge_results(*lists: List[ProductInfo]) -> List[ProductInfo]:
    """Merge multiple product lists and deduplicate by brand+model+platform+price"""
    seen = set()
    merged = []
    for p in sum(lists, []):
        key = (p.brand, p.model, p.platform, round(p.price, 2))
        if key not in seen:
            seen.add(key)
            merged.append(p)
    return merged
