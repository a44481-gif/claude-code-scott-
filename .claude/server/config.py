# -*- coding: utf-8 -*-
"""
配置管理模块 - 豆包运营代理人
支持从环境变量和配置文件加载配置
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class Config:
    """应用配置类"""

    # 支付宝配置
    alipay_mode: str = "personal"
    alipay_app_id: str = ""
    alipay_private_key: str = ""
    alipay_public_key: str = ""
    alipay_notify_url: str = ""
    alipay_return_url: str = ""
    personal_alipay_account: str = ""

    # 邮件配置
    smtp_server: str = "smtp.qq.com"
    smtp_port: int = 465
    sender_email: str = ""
    sender_password: str = ""
    smtp_ssl: bool = True

    # 数据库配置
    db_path: str = "./data/orders.db"

    # 服务配置
    server_host: str = "0.0.0.0"
    server_port: int = 5000
    debug: bool = True
    domain: str = "http://localhost:5000"

    # 通知配置
    enable_email: bool = True
    enable_sms: bool = False
    admin_email: str = ""

    # 运营配置
    min_amount: int = 99
    order_expire_minutes: int = 120
    auto_cancel_minutes: int = 1440

    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量加载配置"""
        import os as _os
        return cls(
            # 支付宝配置
            alipay_mode=_os.getenv('ALIPAY_MODE', 'personal'),
            alipay_app_id=_os.getenv('ALIPAY_APP_ID', ''),
            alipay_private_key=_os.getenv('ALIPAY_PRIVATE_KEY', ''),
            alipay_public_key=_os.getenv('ALIPAY_PUBLIC_KEY', ''),
            alipay_notify_url=_os.getenv('ALIPAY_NOTIFY_URL', ''),
            alipay_return_url=_os.getenv('ALIPAY_RETURN_URL', ''),
            personal_alipay_account=_os.getenv('PERSONAL_ALIPAY_ACCOUNT', ''),

            # 邮件配置
            smtp_server=os.getenv('SMTP_SERVER', 'smtp.qq.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '465')),
            sender_email=os.getenv('SENDER_EMAIL', ''),
            sender_password=os.getenv('SENDER_PASSWORD', ''),
            smtp_ssl=os.getenv('SMTP_SSL', 'true').lower() == 'true',

            # 数据库配置
            db_path=os.getenv('DB_PATH', './data/orders.db'),

            # 服务配置
            server_host=os.getenv('SERVER_HOST', '0.0.0.0'),
            server_port=int(os.getenv('SERVER_PORT', '5000')),
            debug=os.getenv('DEBUG', 'true').lower() == 'true',
            domain=os.getenv('DOMAIN', 'http://localhost:5000'),

            # 通知配置
            enable_email=os.getenv('ENABLE_EMAIL', 'true').lower() == 'true',
            enable_sms=os.getenv('ENABLE_SMS', 'false').lower() == 'true',
            admin_email=os.getenv('ADMIN_EMAIL', ''),

            # 运营配置
            min_amount=int(os.getenv('MIN_AMOUNT', '99')),
            order_expire_minutes=int(os.getenv('ORDER_EXPIRE_MINUTES', '120')),
            auto_cancel_minutes=int(os.getenv('AUTO_CANCEL_MINUTES', '1440')),
        )

    def validate(self) -> list:
        """
        验证配置，返回错误列表
        空列表表示配置正确
        """
        errors = []

        if self.alipay_mode == 'merchant':
            if not self.alipay_app_id:
                errors.append('支付宝商户模式需要配置 ALIPAY_APP_ID')
            if not self.alipay_private_key:
                errors.append('支付宝商户模式需要配置 ALIPAY_PRIVATE_KEY')
            if not self.alipay_public_key:
                errors.append('支付宝商户模式需要配置 ALIPAY_PUBLIC_KEY')
            if not self.alipay_notify_url:
                errors.append('支付宝商户模式需要配置 ALIPAY_NOTIFY_URL（公网可访问）')
        else:
            if not self.personal_alipay_account:
                errors.append('个人模式建议配置 PERSONAL_ALIPAY_ACCOUNT')

        if self.enable_email:
            if not self.sender_email:
                errors.append('启用邮件通知需要配置 SENDER_EMAIL')
            if not self.sender_password:
                errors.append('启用邮件通知需要配置 SENDER_PASSWORD')

        if self.min_amount < 1:
            errors.append('最小金额 MIN_AMOUNT 必须大于0')

        return errors


def get_config() -> Config:
    """获取配置实例"""
    return Config.from_env()


def print_config_guide():
    """打印配置指南"""
    guide = """
    ╔════════════════════════════════════════════════════════════════╗
    ║          豆包运营代理人 - 支付宝收款配置指南                      ║
    ╠════════════════════════════════════════════════════════════════╣
    ║                                                                ║
    ║  方式一：个人快速收款（无需申请商户）                              ║
    ║  ─────────────────────────────────────────                     ║
    ║  1. 打开支付宝 → 我的 → 收款码                                   ║
    ║  2. 获取收款码图片                                              ║
    ║  3. 将收款码图片放到 server/data/ 目录                           ║
    ║  4. 配置: ALIPAY_MODE=personal                                 ║
    ║             PERSONAL_ALIPAY_ACCOUNT=你的支付宝账号               ║
    ║                                                                ║
    ║  方式二：商户API收款（支持自动回调）                              ║
    ║  ─────────────────────────────────────────                     ║
    ║  1. 申请支付宝当面付                                            ║
    ║     https://b.alipay.com/sms/product/f2f.htm                   ║
    ║                                                                ║
    ║  2. 创建应用获取 AppID                                         ║
    ║     https://open.alipay.com/develop/manage                    ║
    ║                                                                ║
    ║  3. 配置以下环境变量:                                           ║
    ║     ALIPAY_MODE=merchant                                       ║
    ║     ALIPAY_APP_ID=你的应用ID                                    ║
    ║     ALIPAY_PRIVATE_KEY=应用私钥                                 ║
    ║     ALIPAY_PUBLIC_KEY=支付宝公钥                                ║
    ║     ALIPAY_NOTIFY_URL=https://你的域名/api/alipay-notify        ║
    ║                                                                ║
    ║  邮件配置（用于发送订单确认、合同等）                              ║
    ║  ─────────────────────────────────────────                     ║
    ║  推荐使用QQ邮箱:                                                ║
    ║  1. 登录 mail.qq.com                                           ║
    ║  2. 设置 → 账户 → POP3/SMTP服务 → 开启                          ║
    ║  3. 获取授权码                                                  ║
    ║  4. 配置:                                                      ║
    ║     SMTP_SERVER=smtp.qq.com                                    ║
    ║     SENDER_EMAIL=your-email@qq.com                            ║
    ║     SENDER_PASSWORD=授权码（不是密码）                          ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(guide)
