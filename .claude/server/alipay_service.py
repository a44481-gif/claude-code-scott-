# -*- coding: utf-8 -*-
"""
支付宝服务模块 - SCOTT豆包賺錢代理人
支持当面付、个人收款、商户API多种模式
"""

import hashlib
import time
import json
import os
import qrcode
import base64
from io import BytesIO
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# 配置类
@dataclass
class AlipayConfig:
    """支付宝配置"""
    # 模式: personal(个人) / merchant(商户)
    mode: str = "personal"

    # 商户模式配置
    app_id: str = ""           # 支付宝应用ID
    private_key: str = ""      # 应用私钥
    alipay_public_key: str = "" # 支付宝公钥

    # 个人模式配置 (使用收款码)
    personal_qr_url: str = ""   # 个人支付宝收款码链接
    personal_qr_image: str = ""  # 个人支付宝收款码图片路径

    # 回调配置
    notify_url: str = ""        # 异步回调地址
    return_url: str = ""         # 同步跳转地址

    # 商户PID
    pid: str = ""               # 商户PID

class AlipayService:
    """支付宝服务类"""

    def __init__(self, config: AlipayConfig):
        self.config = config
        # 检查收款码图片是否存在
        self.qr_image_path = config.personal_qr_image
        if not self.qr_image_path or not os.path.exists(self.qr_image_path):
            # 尝试查找收款码图片（支持png和jpg/jpeg）
            base_dir = os.path.dirname(__file__)
            for fname in ['alipay_qr.png', 'alipay_qr.jpg', 'alipay_qr.jpeg']:
                path = os.path.join(base_dir, 'data', fname)
                if os.path.exists(path):
                    self.qr_image_path = path
                    break
            else:
                self.qr_image_path = ""
        # 确定图片类型
        if self.qr_image_path:
            if self.qr_image_path.lower().endswith(('.jpg', '.jpeg')):
                self.qr_image_type = 'jpeg'
            else:
                self.qr_image_type = 'png'
        else:
            self.qr_image_type = 'png'

    def create_qr_code(self, amount: float, subject: str, out_trade_no: str) -> Dict[str, Any]:
        """
        创建支付二维码

        Args:
            amount: 支付金额
            subject: 订单标题
            out_trade_no: 商户订单号

        Returns:
            包含二维码和订单信息的字典
        """
        if self.config.mode == "merchant":
            return self._create_merchant_qr(amount, subject, out_trade_no)
        else:
            return self._create_personal_qr(amount, subject, out_trade_no)

    def _create_merchant_qr(self, amount: float, subject: str, out_trade_no: str) -> Dict[str, Any]:
        """
        商户模式：使用支付宝当面付API生成二维码
        需要申请支付宝商户账号和应用
        """
        from alipay import AliPay

        alipay = AliPay(
            appid=self.config.app_id,
            app_notify_url=self.config.notify_url,
            app_private_key_string=self.config.private_key,
            alipay_public_key_string=self.config.alipay_public_key,
            sign_type="RSA2"
        )

        # 生成扫码支付链接
        pay_params = {
            'out_trade_no': out_trade_no,
            'total_amount': amount,
            'subject': subject,
            'qr_code': 'alipay://'  # 生成二维码的标志
        }

        # 获取扫码支付URL
        pay_url = alipay.api_alipay_trade_precreate(
            out_trade_no=out_trade_no,
            total_amount=amount,
            subject=subject
        )

        # 生成二维码图片
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(pay_url.get('qr_code', ''))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # 转换为base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            'success': True,
            'qr_code': f'data:image/png;base64,{qr_code_base64}',
            'pay_url': pay_url.get('qr_code', ''),
            'out_trade_no': out_trade_no,
            'amount': amount,
            'mode': 'merchant'
        }

    def _create_personal_qr(self, amount: float, subject: str, out_trade_no: str) -> Dict[str, Any]:
        """
        个人模式：使用收款码图片 + 金额提示
        """
        # 如果有收款码图片，使用图片
        if self.qr_image_path and os.path.exists(self.qr_image_path):
            with open(self.qr_image_path, 'rb') as f:
                qr_code_base64 = base64.b64encode(f.read()).decode()

            return {
                'success': True,
                'qr_code': f'data:image/{self.qr_image_type};base64,{qr_code_base64}',
                'pay_url': '',
                'out_trade_no': out_trade_no,
                'amount': amount,
                'mode': 'personal',
                'use_real_qr': True,
                'instructions': [
                    f'应付金额：¥{amount}',
                    '1. 打开手机支付宝',
                    '2. 扫一扫上方收款码',
                    f'3. 输入金额 {amount} 元',
                    '4. 完成支付'
                ]
            }
        else:
            # 没有收款码图片，生成链接二维码
            qr_url = self._generate_personal_pay_url(amount, subject, out_trade_no)

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

            return {
                'success': True,
                'qr_code': f'data:image/png;base64,{qr_code_base64}',
                'pay_url': qr_url,
                'out_trade_no': out_trade_no,
                'amount': amount,
                'mode': 'personal',
                'instructions': [
                    f'应付金额：¥{amount}',
                    '1. 打开手机支付宝',
                    '2. 点击首页的"收付款"',
                    '3. 选择"向商家付款"',
                    '4. 扫描上方二维码'
                ]
            }

    def _generate_personal_pay_url(self, amount: float, subject: str, out_trade_no: str) -> str:
        """
        生成个人支付宝收款链接
        使用支付宝转账码格式
        """
        amount_str = f"{amount:.2f}"
        return f"https://qr.alipay.com/fkx{int(time.time())}{str(amount).replace('.', '')}"

    def verify_notification(self, data: Dict) -> bool:
        """
        验证支付宝回调通知

        Args:
            data: 回调数据

        Returns:
            验证是否通过
        """
        if self.config.mode != "merchant":
            return True

        from alipay import AliPay

        alipay = AliPay(
            appid=self.config.app_id,
            app_notify_url=self.config.notify_url,
            app_private_key_string=self.config.private_key,
            alipay_public_key_string=self.config.alipay_public_key,
            sign_type="RSA2"
        )

        signature = data.get('sign', '')
        # 移除sign字段
        params = {k: v for k, v in data.items() if k != 'sign'}

        return alipay.verify(params, signature)

    def query_order(self, out_trade_no: str) -> Dict[str, Any]:
        """
        查询订单状态

        Args:
            out_trade_no: 商户订单号

        Returns:
            订单状态信息
        """
        if self.config.mode != "merchant":
            # 个人模式无法查询订单状态，返回模拟数据
            return {
                'success': False,
                'message': '个人模式不支持实时查询，请留意到账通知'
            }

        from alipay import AliPay

        alipay = AliPay(
            appid=self.config.app_id,
            app_notify_url=self.config.notify_url,
            app_private_key_string=self.config.private_key,
            alipay_public_key_string=self.config.alipay_public_key,
            sign_type="RSA2"
        )

        try:
            result = alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
            return {
                'success': True,
                'trade_status': result.get('trade_status', ''),
                'amount': result.get('total_amount', ''),
                'trade_no': result.get('trade_no', '')
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }


# 配置示例
def get_default_config() -> AlipayConfig:
    """获取默认配置"""
    return AlipayConfig(
        mode="personal",  # 先使用个人模式
        notify_url="https://your-domain.com/api/alipay-notify",
        return_url="https://your-domain.com/payment/success"
    )
