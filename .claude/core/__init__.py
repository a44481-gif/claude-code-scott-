"""
AI Business Intelligence Platform - Shared Core Library
=======================================================
A unified core library providing crawler, AI analysis, email, scheduling,
and 飞书 integration capabilities for all 5 agents.

Reuses patterns from:
  - msi_psu_automation: requests + Selenium BaseCrawler, sklearn/NLTK AIAnalyzer, Jinja2 EmailSender
  - health_food_agent: httpx async BaseCrawler, MiniMax API Analyzer, APScheduler

Usage:
  from core import BaseCrawler, MiniMaxAnalyzer, EmailSender, TaskScheduler, load_config, setup_logger
  from core import ProductData, NewsItem, PriceRecord, MsiUpdate, AgentReport
  from core import classify_brand, BRAND_ALIASES, CATEGORY_TAGS
"""

from .base_crawler import BaseCrawler
from .ai_analyzer import MiniMaxAnalyzer
from .models import ProductData, NewsItem, PriceRecord, MsiUpdate, AgentReport, CrawlerResult
from .brand_utils import classify_brand, classify_news_category, classify_category, extract_wattage, extract_certification, BRAND_ALIASES, PC_CATEGORY_TAGS, NEWS_CATEGORY_TAGS, CANONICAL_BRANDS
from .email_sender import EmailSender
from .scheduler import TaskScheduler
from .lark_client import LarkClient
from .config import load_config
from .logger import setup_logger

__version__ = "1.0.0"
__all__ = [
    # Crawler
    "BaseCrawler",
    # AI Analysis
    "MiniMaxAnalyzer",
    # Data Models
    "ProductData",
    "NewsItem",
    "PriceRecord",
    "MsiUpdate",
    "AgentReport",
    "CrawlerResult",
    # Brand Utilities
    "classify_brand",
    "classify_news_category",
    "classify_category",
    "extract_wattage",
    "extract_certification",
    "BRAND_ALIASES",
    "PC_CATEGORY_TAGS",
    "NEWS_CATEGORY_TAGS",
    "CANONICAL_BRANDS",
    # Email
    "EmailSender",
    # Scheduler
    "TaskScheduler",
    # Lark (飞书)
    "LarkClient",
    # Config & Logger
    "load_config",
    "setup_logger",
]
