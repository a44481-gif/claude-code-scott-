#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCOTT 豆包赚钱 - 每日运营报告
自动生成并发送到微信和飞书
"""

import requests
import sqlite3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class DailyReport:
    """每日运营报告"""

    def __init__(self, db_path: str = './data/orders.db'):
        self.db_path = db_path
        self.feishu_webhook = os.getenv('FEISHU_WEBHOOK_URL', '')
        self.serverchan_sendkey = os.getenv('SERVERCHAN_SENDKEY', '')

    def get_daily_stats(self) -> dict:
        """获取每日统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')

        # 今日订单
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(amount), 0)
            FROM orders
            WHERE DATE(created_at) = ?
        """, (today,))
        today_orders, today_amount = cursor.fetchone()

        # 今日收款
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(amount), 0)
            FROM orders
            WHERE DATE(paid_at) = ? AND status = 'paid'
        """, (today,))
        paid_orders, paid_amount = cursor.fetchone()

        # 本周统计
        week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(amount), 0)
            FROM orders
            WHERE DATE(created_at) >= ? AND status = 'paid'
        """, (week_start,))
        week_orders, week_amount = cursor.fetchone()

        # 待处理订单
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
        pending = cursor.fetchone()[0]

        # 新客户数
        cursor.execute("""
            SELECT COUNT(DISTINCT customer_phone)
            FROM orders
            WHERE DATE(created_at) = ?
        """, (today,))
        new_customers = cursor.fetchone()[0]

        conn.close()

        return {
            'today_orders': today_orders or 0,
            'today_amount': today_amount or 0,
            'paid_orders': paid_orders or 0,
            'paid_amount': paid_amount or 0,
            'week_orders': week_orders or 0,
            'week_amount': week_amount or 0,
            'pending': pending,
            'new_customers': new_customers
        }

    def get_recent_orders(self, limit: int = 5) -> list:
        """获取最近订单"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT order_id, customer_name, amount, status, created_at
            FROM orders
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        orders = []
        for row in cursor.fetchall():
            orders.append({
                'order_id': row[0],
                'customer_name': row[1],
                'amount': row[2],
                'status': row[3],
                'created_at': row[4]
            })

        conn.close()
        return orders

    def send_feishu_report(self, stats: dict, orders: list):
        """发送飞书报告"""
        if not self.feishu_webhook:
            print('[跳过] 未配置飞书Webhook')
            return

        # 构建消息
        orders_text = '\n'.join([
            f"• {o['customer_name']} - ¥{o['amount']:.0f} ({o['status']})"
            for o in orders[:3]
        ]) or '暂无新订单'

        message = {
            'msg_type': 'interactive',
            'card': {
                'header': {
                    'title': {
                        'tag': 'plain_text',
                        'content': f"📊 SCOTT运营日报 - {datetime.now().strftime('%m月%d日')}"
                    },
                    'template': 'blue'
                },
                'elements': [
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': '**今日概览**'
                        }
                    },
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': f"📈 新订单: {stats['today_orders']} 单\n💰 今日收款: ¥{stats['paid_amount']:.0f}\n👥 新客户: {stats['new_customers']} 人\n⏳ 待处理: {stats['pending']} 单"
                        }
                    },
                    {'tag': 'hr'},
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': '**本周统计**'
                        }
                    },
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': f"📊 本周订单: {stats['week_orders']} 单\n💰 本周收款: ¥{stats['week_amount']:.0f}"
                        }
                    },
                    {'tag': 'hr'},
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': '**最近订单**'
                        }
                    },
                    {
                        'tag': 'div',
                        'text': {
                            'tag': 'lark_md',
                            'content': orders_text
                        }
                    },
                    {
                        'tag': 'note',
                        'elements': [
                            {
                                'tag': 'plain_text',
                                'content': f"生成时间: {datetime.now().strftime('%H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
        }

        try:
            resp = requests.post(self.feishu_webhook, json=message, timeout=10)
            if resp.status_code == 200:
                print('[成功] 飞书日报已发送')
            else:
                print(f'[失败] 飞书日报发送失败: {resp.text}')
        except Exception as e:
            print(f'[错误] 飞书日报发送异常: {str(e)}')

    def send_wechat_report(self, stats: dict):
        """发送微信报告（Server酱）"""
        if not self.serverchan_sendkey:
            print('[跳过] 未配置Server酱')
            return

        title = f"📊 SCOTT运营日报 {datetime.now().strftime('%m月%d日')}"

        content = f"""
**今日概览**
• 新订单: {stats['today_orders']} 单
• 今日收款: ¥{stats['paid_amount']:.0f}
• 新客户: {stats['new_customers']} 人
• 待处理: {stats['pending']} 单

**本周统计**
• 本周订单: {stats['week_orders']} 单
• 本周收款: ¥{stats['week_amount']:.0f}

**系统状态**: ✅ 运行中
**生成时间**: {datetime.now().strftime('%H:%M:%S')}
"""

        try:
            url = f"https://sctapi.ftqq.com/{self.serverchan_sendkey}.send"
            resp = requests.post(url, data={
                'title': title,
                'desp': content
            }, timeout=10)

            if resp.status_code == 200:
                print('[成功] 微信日报已发送')
            else:
                print(f'[失败] 微信日报发送失败')
        except Exception as e:
            print(f'[错误] 微信日报发送异常: {str(e)}')

    def run(self):
        """执行日报生成和发送"""
        print('=' * 50)
        print(f'   SCOTT运营日报 - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        print('=' * 50)

        # 获取统计数据
        stats = self.get_daily_stats()
        orders = self.get_recent_orders()

        print(f"\n📊 今日统计:")
        print(f"   新订单: {stats['today_orders']}")
        print(f"   今日收款: ¥{stats['paid_amount']:.0f}")
        print(f"   新客户: {stats['new_customers']}")
        print(f"   待处理: {stats['pending']}")
        print(f"\n📈 本周统计:")
        print(f"   本周订单: {stats['week_orders']}")
        print(f"   本周收款: ¥{stats['week_amount']:.0f}")

        # 发送报告
        print('\n发送报告中...')
        self.send_feishu_report(stats, orders)
        self.send_wechat_report(stats)

        print('\n日报生成完成!')


if __name__ == '__main__':
    DailyReport().run()
