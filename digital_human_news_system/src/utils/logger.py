#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志工具模块
Logger Utility Module
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str,
    log_dir: str = "logs",
    level: int = logging.INFO,
    console: bool = True
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        log_dir: 日志目录
        level: 日志级别
        console: 是否输出到控制台

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)

    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件处理器
    log_file = os.path.join(
        log_dir,
        f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台处理器
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """获取已存在的日志记录器"""
    return logging.getLogger(name)
