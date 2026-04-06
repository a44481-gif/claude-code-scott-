#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置文件加载工具
Config Loader Utility
"""

import json
import os
from typing import Any, Dict


class Config:
    """配置管理类"""

    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """加载配置文件"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config',
            'settings.json'
        )

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        Args:
            key: 配置键，支持点号分隔的路径 (如 'news_sources.buddhism')
            default: 默认值
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default

        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置区块"""
        return self._config.get(section, {})

    @property
    def all(self) -> Dict[str, Any]:
        """获取全部配置"""
        return self._config.copy()


def get_config() -> Config:
    """获取配置单例"""
    return Config()
