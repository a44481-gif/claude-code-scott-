#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCOTT 豆包赚钱 - 客户自动跟进系统
自动跟进未付款客户、到期服务提醒
"""

import requests
import sqlite3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class CustomerFollowUp:
    """客户自动跟进"""

    def __init__(self, db_path: str = './data/orders.db'):
        self.db_path = db_path
        self.feishu_webhook = os.getenv('FEISHU_WEBHOOK_URL', '')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'scott365888@gmail.com')

    def get_pending_customers(self) -> list:
        """获取待跟进客户（24小时内未付款）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            SELECT order_id, customer_name, customer_phone, customer_email,
                   product_name, amount, created_at
            FROM orders
            WHERE status = 'pending'
            AND created_at >= ?
            ORDER BY created_at DESC
        """, (yesterday,))

        customers = []
        for row in cursor.fetchall():
            customers.append({
                'order_id': row[0],
                'customer_name': row[1],
                'customer_phone': row[2],
                'customer_email': row[3],
                'product_name': row[4],
                'amount': row[5],
                'created_at': row[6]
            })

        conn.close()
        return customers

    def get_awaiting_service(self) -> list:
        """获取等待服务的客户（已付款但未开始服务）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        cursor.execute("""
            SELECT order_id, customer_name, customer_phone,
                   product_name, amount, paid_at
            FROM orders
            WHERE status = 'paid'
            AND paid_at >= ?
            ORDER BY paid_at DESC
        """, (week_ago,))

        customers = []
        for row in cursor.fetchall():
            customers.append({
                'order_id': row[0],
                'customer_name': row[1],
                'customer_phone': row[2],
                'product_name': row[3],
                'amount': row[4],
                'paid_at': row[5]
            })

        conn.close()
        return customers

    def send_followup_reminder(self, customers: list):
        """发送跟进提醒"""
        if not customers:
            print('[提示] 没有需要跟进的客户')
            return

        print(f'\n📋 发现 {len(customers)} 个待跟进客户:')

        # 构建飞书消息
        customer_list = '\n'.join([
            f"• {c['customer_name']} | {c['product_name']} | ¥{c['amount']:.0f}"
            for c in customers
        ])

        message = {
            'msg_type': 'interactive',
            'card': {
                'header': {
                    'title': {
                        'tag': 'plain_text',
                        'content': '📋 客户跟进提醒'
                    },
                    'template': 'orange'
                },
                'elements': [
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': f'**待跟进客户 ({len(customers)}人)**'
                        }
                    },
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': customer_list
                        }
                    },
                    {'tag': 'hr'},
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': '请及时联系客户，确认付款意向'
                        }
                    }
                ]
            }
        }

        if self.feishu_webhook:
            try:
                resp = requests.post(self.feishu_webhook, json=message, timeout=10)
                if resp.status_code == 200:
                    print('[成功] 跟进提醒已发送至飞书')
                else:
                    print(f'[失败] 飞书发送失败')
            except Exception as e:
                print(f'[错误] 飞书发送异常: {str(e)}')

        # 打印详情
        for c in customers:
            print(f"  • {c['customer_name']} | {c['customer_phone']} | {c['product_name']}")

    def send_service_reminder(self, customers: list):
        """发送服务启动提醒"""
        if not customers:
            print('[提示] 没有等待服务的客户')
            return

        print(f'\n🚀 发现 {len(customers)} 个等待服务的客户:')

        for c in customers:
            print(f"  • {c['customer_name']} | {c['product_name']} | 付款时间: {c['paid_at']}")

        # 发送飞书提醒
        message = {
            'msg_type': 'interactive',
            'card': {
                'header': {
                    'title': {
                        'tag': 'plain_text',
                        'content': '🚀 服务启动提醒'
                    },
                    'template': 'green'
                },
                'elements': [
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': f'**待启动服务 ({len(customers)}个)**'
                        }
                    },
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': '\n'.join([
                                f"• {c['customer_name']} - {c['product_name']}"
                                for c in customers
                            ])
                        }
                    },
                    {'tag': 'hr'},
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': '请及时启动服务，发送服务方案'
                        }
                    }
                ]
            }
        }

        if self.feishu_webhook:
            try:
                resp = requests.post(self.feishu_webhook, json=message, timeout=10)
                if resp.status_code == 200:
                    print('[成功] 服务提醒已发送至飞书')
            except Exception as e:
                print(f'[错误] 飞书发送异常: {str(e)}')

    def run(self):
        """执行跟进检查"""
        print('=' * 50)
        print(f'   SCOTT客户跟进检查 - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        print('=' * 50)

        # 检查待跟进客户
        pending = self.get_pending_customers()
        if pending:
            self.send_followup_reminder(pending)
        else:
            print('[OK] 没有待跟进的客户')

        # 检查等待服务客户
        awaiting = self.get_awaiting_service()
        if awaiting:
            self.send_service_reminder(awaiting)
        else:
            print('[OK] 没有等待服务的客户')

        print('\n跟进检查完成!')


if __name__ == '__main__':
    CustomerFollowUp().run()
