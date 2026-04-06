# -*- coding: utf-8 -*-
"""
GPU 電源線燒毀研究工具套件
GPU Power Cable Burn Research Toolkit

主要模組:
- collector: 資料收集器
- generator: 報告生成器
- sender: 郵件發送器
- lark_sync: 飛書同步工具
"""

__version__ = '2.0.0'
__author__ = 'AI Assistant'
__email__ = 'h13751019800@163.com'

from .collector import GPUCollector
from .generator import ReportGenerator
from .sender import EmailSender

__all__ = [
    'GPUCollector',
    'ReportGenerator',
    'EmailSender',
]
