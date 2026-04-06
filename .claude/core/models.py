"""
Pydantic data models for all agents.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


# ── Product Models ────────────────────────────────────────────────

class ProductData(BaseModel):
    """通用产品数据模型"""
    model_name: str
    brand: str  # NVIDIA, AMD, Intel, Samsung, Kingston, Corsair, MSI, ASUS 等
    category: str  # GPU, CPU, RAM, SSD, PSU, Motherboard
    price: float
    currency: str = "CNY"
    source: str  # JD, Amazon, Newegg, B&H
    url: str
    collected_at: datetime = Field(default_factory=datetime.now)
    rating: Optional[float] = None
    review_count: Optional[int] = None
    wattage: Optional[str] = None  # PSU 瓦数
    certification: Optional[str] = None  # 80+ Gold/Platinum 等
    specs: Optional[Dict[str, str]] = None


# ── News Models ────────────────────────────────────────────────────

class NewsItem(BaseModel):
    """新闻文章模型"""
    title: str
    url: str
    source: str  # TechCrunch, AnandTech, Tom's Hardware, ZOL, IT之家
    category: str = "General"  # AI Infrastructure, PC Components, Storage, Cloud Services
    published_at: Optional[datetime] = None
    summary: str = ""
    collected_at: datetime = Field(default_factory=datetime.now)
    image_url: Optional[str] = None
    tags: List[str] = []


# ── Price Record Models ────────────────────────────────────────────

class PriceRecord(BaseModel):
    """价格历史记录"""
    product_id: str  # 唯一产品 ID (如 SKU 或品牌+型号)
    model_name: str
    brand: str
    category: str
    price: float
    currency: str = "CNY"
    source: str
    recorded_at: datetime = Field(default_factory=datetime.now)
    url: str = ""


class PriceAlert(BaseModel):
    """价格提醒规则"""
    product_id: str
    model_name: str
    alert_type: str = "drop"  # drop, below, change
    threshold: float
    current_price: Optional[float] = None
    last_checked: datetime = Field(default_factory=datetime.now)
    triggered: bool = False


# ── MSI Update Models ──────────────────────────────────────────────

class MsiUpdate(BaseModel):
    """MSI 产品/驱动/BIOS 更新"""
    update_type: str  # new_product, driver_update, BIOS, firmware, news
    title: str
    url: str
    source: str  # msi_official, msi_rss, msi_social
    published_at: Optional[datetime] = None
    collected_at: datetime = Field(default_factory=datetime.now)
    description: str = ""
    version: Optional[str] = None  # 驱动/Bios 版本号


# ── Report Models ──────────────────────────────────────────────────

class AgentReport(BaseModel):
    """通用 Agent 报告包装"""
    agent_name: str
    agent_id: str
    generated_at: datetime = Field(default_factory=datetime.now)
    summary: str
    data: Dict[str, Any] = {}
    attachments: List[str] = []  # file paths
    status: str = "success"  # success, partial, failed
    error_message: Optional[str] = None


class DailyBriefing(BaseModel):
    """每日简报"""
    date: str
    title: str
    ai_summary: str = ""
    categories: Dict[str, List[Dict[str, str]]] = {}  # category -> [{title, url, summary}]
    key_highlights: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.now)


# ── Crawler Result ──────────────────────────────────────────────────

class CrawlerResult(BaseModel):
    """爬虫结果包装"""
    crawler_name: str
    items: List[Dict[str, Any]]
    collected_at: datetime = Field(default_factory=datetime.now)
    stats: Dict[str, Any] = {}  # total_requests, successful_requests, etc.
    errors: List[str] = []


# ── Social Media Models ────────────────────────────────────────────

class SocialPost(BaseModel):
    """社交媒体帖子"""
    platform: str  # douyin, tiktok, kuaishou
    title: str
    content: str
    tags: List[str] = []
    scheduled_at: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, posted, failed
    video_url: Optional[str] = None
    metrics: Dict[str, Any] = {}  # views, likes, comments


class SocialMetrics(BaseModel):
    """社交媒体指标"""
    platform: str
    date: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    followers: int = 0
    engagement_rate: float = 0.0


# ── System Models ───────────────────────────────────────────────────

class AgentStatus(BaseModel):
    """Agent 运行状态"""
    agent_name: str
    agent_id: str
    status: str = "idle"  # idle, running, completed, failed
    last_run: Optional[datetime] = None
    last_success: Optional[datetime] = None
    consecutive_failures: int = 0
    error_message: Optional[str] = None
