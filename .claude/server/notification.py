# -*- coding: utf-8 -*-
"""
通知服务模块 - SCOTT豆包賺錢代理人
支持邮件、短信、微信等通知方式
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class EmailConfig:
    """邮件配置"""
    smtp_server: str = "smtp.qq.com"
    smtp_port: int = 465
    sender_email: str = ""
    sender_password: str = ""
    use_ssl: bool = True

@dataclass
class Customer:
    """客户信息"""
    name: str
    phone: str
    email: str = ""
    wechat: str = ""
    source: str = ""  # 来源渠道
    interest: str = ""  # 感兴趣的服务
    created_at: str = ""

class NotificationService:
    """通知服务类"""

    def __init__(self, email_config: EmailConfig = None):
        self.email_config = email_config or EmailConfig()

    # ==================== 邮件通知 ====================

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容

        Returns:
            是否发送成功
        """
        if not self.email_config.sender_email:
            print(f"[邮件模拟] 发送到 {to_email}: {subject}")
            return True

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_config.sender_email
            msg['To'] = to_email

            html = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html)

            if self.email_config.use_ssl:
                server = smtplib.SMTP_SSL(self.email_config.smtp_server, self.email_config.smtp_port)
            else:
                server = smtplib.SMTP(self.email_config.smtp_server, self.email_config.smtp_port)

            server.login(self.email_config.sender_email, self.email_config.sender_password)
            server.sendmail(self.email_config.sender_email, to_email, msg.as_string())
            server.quit()

            print(f"[邮件发送成功] -> {to_email}")
            return True

        except Exception as e:
            print(f"[邮件发送失败] {to_email}: {str(e)}")
            return False

    def send_order_confirmation(self, customer: Customer, order: Dict) -> bool:
        """
        发送订单确认邮件

        Args:
            customer: 客户信息
            order: 订单信息

        Returns:
            是否发送成功
        """
        if not customer.email:
            print(f"[跳过邮件] 客户 {customer.name} 没有邮箱")
            return False

        # 联系方式
        contact_email = 'scott365888@gmail.com'
        contact_wechat = 'PTS9800'

        subject = f"【SCOTT豆包賺錢】订单确认 - {order['order_id']}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .order-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .amount {{ font-size: 32px; color: #667eea; font-weight: bold; }}
                .btn {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>订单确认</h1>
                    <p>感谢您选择SCOTT豆包賺錢代理服务</p>
                </div>
                <div class="content">
                    <p>尊敬的 <strong>{customer.name}</strong>：</p>
                    <p>您的订单已确认，我们将尽快为您服务。</p>

                    <div class="order-box">
                        <p><strong>订单号：</strong>{order['order_id']}</p>
                        <p><strong>服务项目：</strong>{order['product_name']}</p>
                        <p><strong>订单金额：</strong><span class="amount">¥{order['amount']}</span></p>
                        <p><strong>下单时间：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                    </div>

                    <p><strong>下一步流程：</strong></p>
                    <ol>
                        <li>我们的客服将在 <strong>24小时</strong> 内联系您</li>
                        <li>服务合同将在 <strong>24小时</strong> 内发送至您的邮箱</li>
                        <li>服务启动前会有专人对接需求细节</li>
                    </ol>

                    <p>如有疑问，请回复此邮件或拨打客服电话。</p>

                    <p class="footer">
                        SCOTT豆包賺錢代理人<br>
                        专业AI代运营服务<br>
                        © 2024 All Rights Reserved
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(customer.email, subject, html)

    def send_service_contract(self, customer: Customer, order: Dict) -> bool:
        """
        发送服务合同

        Args:
            customer: 客户信息
            order: 订单信息

        Returns:
            是否发送成功
        """
        if not customer.email:
            return False

        subject = f"【SCOTT豆包賺錢】服务合同 - {order['order_id']}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.8; color: #333; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #667eea; text-align: center; }}
                h2 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                .contract-box {{ background: #f9f9f9; padding: 30px; border-radius: 10px; }}
                .signature {{ margin-top: 50px; text-align: right; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI代运营服务合同</h1>

                <div class="contract-box">
                    <h2>一、服务内容</h2>
                    <p>甲方（委托方）：{customer.name}</p>
                    <p>乙方（服务方）：SCOTT豆包賺錢代理人</p>
                    <p>服务项目：{order['product_name']}</p>

                    <h2>二、服务费用</h2>
                    <p>服务费用：人民币 {order['amount']} 元</p>
                    <p>支付方式：支付宝转账</p>
                    <p>订单号：{order['order_id']}</p>

                    <h2>三、服务期限</h2>
                    <p>服务期限：自合同签订之日起 {self._get_service_period(order['product_id'])}</p>

                    <h2>四、双方权利与义务</h2>
                    <p>1. 甲方有权了解服务进度，提出合理修改意见</p>
                    <p>2. 乙方应按时按质完成服务工作</p>
                    <p>3. 双方应对合作过程中知悉的商业秘密保密</p>

                    <h2>五、售后服务</h2>
                    <p>服务期内提供不限次咨询服务</p>
                    <p>工作时间内 24 小时响应</p>

                    <div class="signature">
                        <p>甲方签字：___________</p>
                        <p>乙方签字：___________</p>
                        <p>签订日期：{datetime.now().strftime('%Y年%m月%d日')}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(customer.email, subject, html)

    def _get_service_period(self, product_id: str) -> str:
        """根据产品ID获取服务期限"""
        periods = {
            'ai-operation-basic': '1个月',
            'ai-operation-pro': '1个月',
            'prompt-custom': '一次性服务',
            'script-dev': '一次性服务',
            'digital-human': '一次性服务'
        }
        return periods.get(product_id, '1个月')

    # ==================== 短信通知 ====================

    def send_sms(self, phone: str, message: str) -> bool:
        """
        发送短信（需要接入短信网关，如阿里云短信）

        Args:
            phone: 手机号
            message: 短信内容

        Returns:
            是否发送成功
        """
        # 这里可以接入阿里云短信、腾讯云短信等服务
        print(f"[短信模拟] 发送到 {phone}: {message}")
        return True

    def send_order_notification_sms(self, phone: str, order_id: str) -> bool:
        """发送订单通知短信"""
        message = f"【SCOTT豆包賺錢】尊敬的客户，您的订单{order_id}已确认，客服将在24小时内联系您。如有疑问请回复此短信。"
        return self.send_sms(phone, message)

    # ==================== 微信通知 ====================

    def send_wechat_notification(self, open_id: str, template_id: str, data: Dict) -> bool:
        """
        发送微信模板消息

        Args:
            open_id: 用户OpenID
            template_id: 模板ID
            data: 模板数据

        Returns:
            是否发送成功
        """
        # 需要接入微信支付或微信开放平台
        print(f"[微信模拟] 发送给 {open_id}: 模板消息 {template_id}")
        return True


# ==================== 客户管理服务 ====================

class CustomerService:
    """客户管理服务"""

    def __init__(self, db_path: str = "customers.db"):
        self.db_path = db_path
        self.notification_service = NotificationService()
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT,
                wechat TEXT,
                source TEXT,
                interest TEXT,
                status TEXT DEFAULT 'new',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def add_customer(self, name: str, phone: str, email: str = "",
                     source: str = "", interest: str = "") -> Dict:
        """添加客户"""
        import sqlite3
        from datetime import datetime

        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO customers (name, phone, email, source, interest, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, phone, email, source, interest, now, now))

            customer_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return {
                'success': True,
                'customer_id': customer_id,
                'message': '客户添加成功'
            }

        except sqlite3.IntegrityError:
            conn.close()
            # 更新已有客户
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE customers SET updated_at = ? WHERE phone = ?
            """, (now, phone))
            conn.commit()
            conn.close()

            return {
                'success': True,
                'message': '客户已存在，已更新信息'
            }

    def get_customer_by_phone(self, phone: str) -> Optional[Dict]:
        """根据手机号查询客户"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'name': row[1],
                'phone': row[2],
                'email': row[3],
                'wechat': row[4],
                'source': row[5],
                'interest': row[6],
                'status': row[7],
                'created_at': row[8],
                'updated_at': row[9]
            }
        return None

    def update_customer_status(self, phone: str, status: str) -> bool:
        """更新客户状态"""
        import sqlite3
        from datetime import datetime

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE customers SET status = ?, updated_at = ? WHERE phone = ?
        """, (status, datetime.now().isoformat(), phone))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success


# ==================== 自动化运营服务 ====================

import requests
import os

class AutomationService:
    """自动化运营服务"""

    def __init__(self):
        self.notification_service = NotificationService()
        self.customer_service = CustomerService()
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', '')
        self.feishu_webhook_url = os.getenv('FEISHU_WEBHOOK_URL', '')
        self.enable_n8n = os.getenv('ENABLE_N8N_AUTOMATION', 'false').lower() == 'true'

    def on_payment_received(self, order: Dict):
        """
        支付成功后的自动化流程

        Args:
            order: 订单信息
        """
        print(f"[自动化流程] 订单 {order['order_id']} 支付成功，开始自动化流程")

        # 1. 创建/更新客户记录
        customer_data = {
            'name': order['customer_name'],
            'phone': order['customer_phone'],
            'email': order['customer_email'],
            'interest': order['product_name']
        }
        self.customer_service.add_customer(**customer_data)

        # 2. 发送确认邮件
        customer = Customer(
            name=order['customer_name'],
            phone=order['customer_phone'],
            email=order['customer_email']
        )
        self.notification_service.send_order_confirmation(customer, order)

        # 3. 发送短信通知
        self.notification_service.send_order_notification_sms(
            order['customer_phone'],
            order['order_id']
        )

        # 4. 发送服务合同
        self.notification_service.send_service_contract(customer, order)

        # 5. 触发 n8n 自动化（如果启用）
        if self.enable_n8n and self.n8n_webhook_url:
            self._trigger_n8n_workflow(order)

        # 6. 发送飞书通知（如果配置了）
        if self.feishu_webhook_url:
            self._send_feishu_notification(order)

        print(f"[自动化流程] 订单 {order['order_id']} 流程完成")

    def _trigger_n8n_workflow(self, order: Dict):
        """触发 n8n 工作流"""
        try:
            payload = {
                'event': 'payment_completed',
                'order': {
                    'order_id': order['order_id'],
                    'product_name': order['product_name'],
                    'amount': order['amount'],
                    'paid_at': datetime.now().isoformat()
                },
                'customer': {
                    'name': order['customer_name'],
                    'phone': order['customer_phone'],
                    'email': order['customer_email']
                }
            }

            response = requests.post(self.n8n_webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"[n8n触发成功] 订单 {order['order_id']}")
            else:
                print(f"[n8n触发失败] 状态码: {response.status_code}")

        except Exception as e:
            print(f"[n8n触发异常] {str(e)}")

    def _send_feishu_notification(self, order: Dict):
        """发送飞书通知"""
        try:
            message = {
                'msg_type': 'interactive',
                'card': {
                    'header': {
                        'title': {
                            'tag': 'plain_text',
                            'content': '🎉 新订单收款通知'
                        },
                        'template': 'green'
                    },
                    'elements': [
                        {
                            'tag': 'div',
                            'text': {
                                'tag': 'lark_md',
                                'content': f"**订单号**: {order['order_id']}"
                            }
                        },
                        {
                            'tag': 'div',
                            'text': {
                                'tag': 'lark_md',
                                'content': f"**客户**: {order['customer_name']}"
                            }
                        },
                        {
                            'tag': 'div',
                            'text': {
                                'tag': 'lark_md',
                                'content': f"**金额**: ¥{order['amount']}"
                            }
                        },
                        {
                            'tag': 'div',
                            'text': {
                                'tag': 'lark_md',
                                'content': f"**产品**: {order['product_name']}"
                            }
                        },
                        {
                            'tag': 'hr'
                        },
                        {
                            'tag': 'div',
                            'text': {
                                'tag': 'lark_md',
                                'content': '请及时跟进服务交付'
                            }
                        }
                    ]
                }
            }

            response = requests.post(self.feishu_webhook_url, json=message, timeout=10)
            if response.status_code == 200:
                print(f"[飞书通知成功] 订单 {order['order_id']}")

        except Exception as e:
            print(f"[飞书通知失败] {str(e)}")

    def on_lead_captured(self, lead_data: Dict):
        """
        捕获潜在客户后的自动化流程

        Args:
            lead_data: 潜在客户数据
        """
        print(f"[自动化流程] 捕获潜在客户: {lead_data.get('name')}")

        # 1. 创建客户记录
        self.customer_service.add_customer(
            name=lead_data.get('name', ''),
            phone=lead_data.get('phone', ''),
            email=lead_data.get('email', ''),
            source=lead_data.get('source', ''),
            interest=lead_data.get('interest', '')
        )

        # 2. 发送欢迎邮件
        customer = Customer(
            name=lead_data.get('name', ''),
            phone=lead_data.get('phone', ''),
            email=lead_data.get('email', '')
        )

        welcome_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>亲爱的 {lead_data.get('name')}：</h2>
            <p>感谢您对SCOTT豆包賺錢代理服务的关注！</p>
            <p>我们的客服团队将在 <strong>24小时</strong> 内与您联系，为您提供专业的咨询服务。</p>
            <p>如果您有任何问题，也可以直接回复这封邮件。</p>
            <hr>
            <p><strong>我们的服务：</strong></p>
            <ul>
                <li>AI代运营（月费制）</li>
                <li>AI提示词定制</li>
                <li>AI脚本开发</li>
                <li>AI数字人视频</li>
                <li>自动化工作流搭建</li>
            </ul>
        </body>
        </html>
        """

        self.notification_service.send_email(
            customer.email,
            "【SCOTT豆包賺錢】感谢您的关注！",
            welcome_html
        )


# ==================== 导出服务类 ====================

def get_notification_service() -> NotificationService:
    """获取通知服务实例"""
    return NotificationService()

def get_customer_service() -> CustomerService:
    """获取客户管理服务实例"""
    return CustomerService()

def get_automation_service() -> AutomationService:
    """获取自动化服务实例"""
    return AutomationService()
