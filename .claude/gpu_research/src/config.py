# -*- coding: utf-8 -*-
"""
配置管理模組
Configuration Management Module
"""

import os
from dataclasses import dataclass
from typing import List


@dataclass
class EmailConfig:
    """郵箱配置"""
    smtp_host: str = 'smtp.163.com'
    smtp_port: int = 465
    sender_email: str = 'h13751019800@163.com'
    sender_auth_code: str = 'JWxaQXzrCQCWtPu3'
    use_ssl: bool = True


@dataclass
class LarkConfig:
    """飛書配置"""
    app_id: str = ''
    app_secret: str = ''
    doc_token: str = ''
    sheet_token: str = ''


@dataclass
class ResearchConfig:
    """研究配置"""
    topics: List[str] = None
    platforms_en: List[str] = None
    platforms_cn: List[str] = None
    platforms_jp: List[str] = None
    platforms_eu: List[str] = None

    def __post_init__(self):
        if self.topics is None:
            self.topics = [
                'RTX 4090 12VHPWR 熔化',
                '顯卡供電接口燒毀',
                'GPU power connector burn',
                '12VHPWR melted cable',
            ]
        if self.platforms_en is None:
            self.platforms_en = [
                'Reddit',
                "Tom's Hardware",
                'Gamers Nexus',
                'VideoCardz',
                'TechPowerUp',
                'Overclock.net',
                'Guru3D',
                'AnandTech',
            ]
        if self.platforms_cn is None:
            self.platforms_cn = [
                '知乎',
                'Bilibili',
                'NGA',
                '百度貼吧',
                'ChipHell',
                'PCEVA',
                'ZOL',
            ]
        if self.platforms_jp is None:
            self.platforms_jp = [
                '価格.com',
                'AKIBA PC Hotline!',
                '5ch',
            ]
        if self.platforms_eu is None:
            self.platforms_eu = [
                'Hardwareluxx',
                'Guru3D',
                'Scan',
                'ComputerBase',
            ]


class Config:
    """配置管理器"""

    def __init__(self):
        self.email = EmailConfig()
        self.lark = LarkConfig()
        self.research = ResearchConfig()

        # 嘗試從環境變量加載
        self._load_from_env()

    def _load_from_env(self):
        """從環境變量加載配置"""
        # 郵箱配置
        if os.getenv('SMTP_HOST'):
            self.email.smtp_host = os.getenv('SMTP_HOST')
        if os.getenv('SMTP_PORT'):
            self.email.smtp_port = int(os.getenv('SMTP_PORT'))
        if os.getenv('SENDER_EMAIL'):
            self.email.sender_email = os.getenv('SENDER_EMAIL')
        if os.getenv('SENDER_AUTH_CODE'):
            self.email.sender_auth_code = os.getenv('SENDER_AUTH_CODE')

        # 飛書配置
        if os.getenv('LARK_APP_ID'):
            self.lark.app_id = os.getenv('LARK_APP_ID')
        if os.getenv('LARK_APP_SECRET'):
            self.lark.app_secret = os.getenv('LARK_APP_SECRET')
        if os.getenv('LARK_DOC_TOKEN'):
            self.lark.doc_token = os.getenv('LARK_DOC_TOKEN')

    def update_email(self, host: str = None, port: int = None,
                     email: str = None, auth_code: str = None):
        """更新郵箱配置"""
        if host:
            self.email.smtp_host = host
        if port:
            self.email.smtp_port = port
        if email:
            self.email.sender_email = email
        if auth_code:
            self.email.sender_auth_code = auth_code

    def update_lark(self, app_id: str = None, app_secret: str = None,
                    doc_token: str = None):
        """更新飛書配置"""
        if app_id:
            self.lark.app_id = app_id
        if app_secret:
            self.lark.app_secret = app_secret
        if doc_token:
            self.lark.doc_token = doc_token

    def validate(self) -> tuple:
        """
        驗證配置
        返回: (is_valid, errors)
        """
        errors = []

        # 郵箱驗證
        if not self.email.sender_email:
            errors.append('郵箱地址未設置')
        if not self.email.sender_auth_code:
            errors.append('郵箱授權碼未設置')

        # 飛書驗證
        if self.lark.app_id and not self.lark.app_secret:
            errors.append('飛書 App Secret 未設置')

        return len(errors) == 0, errors


# 全局配置實例
config = Config()
