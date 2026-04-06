"""
基礎爬蟲類 - MSI電源數據收集系統
提供通用的爬蟲功能和方法
"""

import logging
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProductData:
    """產品數據結構"""
    model_name: str
    model_number: str
    power_watts: int
    efficiency_rating: str  # 如 "80 PLUS Gold"
    price_usd: float
    price_original: float
    currency: str
    availability: str
    rating: Optional[float] = None
    review_count: Optional[int] = None
    source: str
    region: str
    url: str
    collection_timestamp: str
    features: Optional[List[str]] = None
    specifications: Optional[Dict[str, str]] = None


class BaseCrawler(ABC):
    """基礎爬蟲抽象類"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        self.setup_session()
        self.driver = None
        self.products = []
        
    def setup_session(self):
        """設置HTTP會話"""
        headers = {
            'User-Agent': self.config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(headers)
        
        # 設置請求超時
        self.timeout = self.config.get('request_timeout', 30)
        
    def setup_selenium(self):
        """設置Selenium驅動器"""
        try:
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # 避免被檢測為機器人
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 執行JavaScript避免被檢測
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Selenium驅動器初始化成功")
            
        except Exception as e:
            logger.error(f"初始化Selenium時發生錯誤: {e}")
            self.driver = None
    
    @abstractmethod
    def crawl(self) -> List[ProductData]:
        """爬取數據的抽象方法"""
        pass
    
    def fetch_page(self, url: str, use_selenium: bool = False) -> Optional[str]:
        """獲取頁面內容"""
        try:
            if use_selenium and self.driver:
                return self._fetch_with_selenium(url)
            else:
                return self._fetch_with_requests(url)
        except Exception as e:
            logger.error(f"獲取頁面時發生錯誤: {e}")
            return None
    
    def _fetch_with_requests(self, url: str) -> Optional[str]:
        """使用requests庫獲取頁面"""
        try:
            # 隨機延遲，避免觸發反爬蟲
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 檢查返回內容類型
            content_type = response.headers.get('Content-Type', '')
            if 'html' not in content_type.lower():
                logger.warning(f"非HTML內容類型: {content_type}")
                return None
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"請求失敗: {e}")
            return None
    
    def _fetch_with_selenium(self, url: str) -> Optional[str]:
        """使用Selenium獲取頁面"""
        if not self.driver:
            self.setup_selenium()
            if not self.driver:
                return None
        
        try:
            self.driver.get(url)
            
            # 等待頁面加載
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 模擬人類滾動行為
            self._simulate_human_scroll()
            
            # 等待可能的動態加載
            time.sleep(random.uniform(2, 4))
            
            return self.driver.page_source
            
        except (TimeoutException, WebDriverException) as e:
            logger.error(f"Selenium獲取頁面失敗: {e}")
            return None
    
    def _simulate_human_scroll(self):
        """模擬人類滾動行為"""
        try:
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            scroll_step = random.randint(300, 600)
            
            while current_position < total_height:
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                current_position += scroll_step
                time.sleep(random.uniform(0.5, 1.5))
            
            # 滾回頂部
            self.driver.execute_script("window.scrollTo(0, 0);")
            
        except Exception as e:
            logger.warning(f"模擬滾動時發生錯誤: {e}")
    
    def parse_html(self, html: str, parser: str = 'lxml') -> Optional[BeautifulSoup]:
        """解析HTML內容"""
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, parser)
            return soup
        except Exception as e:
            logger.error(f"解析HTML時發生錯誤: {e}")
            return None
    
    def extract_text(self, element) -> str:
        """安全提取文本"""
        if element:
            text = element.get_text(strip=True)
            return text if text else ""
        return ""
    
    def extract_float(self, text: str) -> Optional[float]:
        """從文本中提取浮點數"""
        try:
            # 移除貨幣符號和空格
            cleaned = ''.join(c for c in text if c.isdigit() or c in ['.', ',', '-'])
            cleaned = cleaned.replace(',', '')
            return float(cleaned)
        except ValueError:
            return None
    
    def cleanup(self):
        """清理資源"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"關閉Selenium驅動器時發生錯誤: {e}")
        
        self.session.close()
        logger.info("爬蟲資源已清理")