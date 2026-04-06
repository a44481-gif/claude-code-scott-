#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI数字人新闻内容生产与全球分发系统
Digital Human News Production & Global Distribution System

模块初始化文件
"""

__version__ = '1.0.0'
__author__ = 'Digital Human News System'

# 导入核心模块
from .news.news_fetcher import NewsFetcher
from .filter.content_filter import ContentFilter
from .creator.ai_creator import AICreator
from .human.digital_human import DigitalHumanGenerator
from .publisher.publisher import PlatformPublisher
from .notifier.email_notifier import EmailNotifier

__all__ = [
    'NewsFetcher',
    'ContentFilter',
    'AICreator',
    'DigitalHumanGenerator',
    'PlatformPublisher',
    'EmailNotifier',
]
