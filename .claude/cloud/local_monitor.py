#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地监控面板
连接云端API，实时显示数据
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class CloudMonitor:
    """云端监控类"""

    def __init__(self, cloud_url: str = None):
        self.cloud_url = cloud_url or os.getenv('CLOUD_API_URL', 'http://localhost:5000')

    def check_status(self) -> dict:
        """检查云端状态"""
        try:
            resp = requests.get(f'{self.cloud_url}/api/products', timeout=5)
            return {
                'online': resp.status_code == 200,
                'status_code': resp.status_code,
                'url': self.cloud_url
            }
        except Exception as e:
            return {
                'online': False,
                'error': str(e),
                'url': self.cloud_url
            }

    def get_orders(self) -> list:
        """获取订单列表"""
        try:
            resp = requests.get(f'{self.cloud_url}/api/export-orders', timeout=10)
            if resp.status_code == 200:
                return resp.json().get('data', [])
            return []
        except:
            return []

    def get_daily_stats(self) -> dict:
        """获取每日统计"""
        try:
            resp = requests.get(f'{self.cloud_url}/api/daily-stats', timeout=10)
            if resp.status_code == 200:
                return resp.json().get('data', {})
            return {}
        except:
            return {}

    def get_weekly_stats(self) -> dict:
        """获取每周统计"""
        try:
            resp = requests.get(f'{self.cloud_url}/api/weekly-stats', timeout=10)
            if resp.status_code == 200:
                return resp.json().get('data', {})
            return {}
        except:
            return {}

    def display_dashboard(self):
        """显示监控面板"""
        print('\n' + '=' * 60)
        print('    SCOTT豆包赚钱 - 云端监控面板')
        print('=' * 60)

        # 检查状态
        status = self.check_status()
        if status['online']:
            print(f'\n  ✅ 云端服务: 在线')
            print(f'  🌐 地址: {status["url"]}')
        else:
            print(f'\n  ❌ 云端服务: 离线')
            print(f'  🌐 地址: {status["url"]}')
            print(f'  💡 提示: 请检查云端服务是否启动')
            return

        # 每日统计
        print('\n  📊 今日统计')
        print('  ' + '-' * 40)
        daily = self.get_daily_stats()
        if daily:
            print(f'  新订单: {daily.get("total_orders", 0)}')
            print(f'  已付款: {daily.get("paid_orders", 0)}')
            print(f'  待处理: {daily.get("pending_orders", 0)}')
            print(f'  今日收款: ¥{daily.get("total_amount", 0):.2f}')
            print(f'  新客户: {daily.get("new_customers", 0)}')

        # 每周统计
        print('\n  📈 本周统计')
        print('  ' + '-' * 40)
        weekly = self.get_weekly_stats()
        if weekly:
            print(f'  本周订单: {weekly.get("total_orders", 0)}')
            print(f'  本周收款: ¥{weekly.get("total_amount", 0):.2f}')
            print(f'  统计周期: {weekly.get("week_start", "")} ~ {weekly.get("week_end", "")}')

        # 最新订单
        print('\n  📋 最新订单')
        print('  ' + '-' * 40)
        orders = self.get_orders()[:5]
        if orders:
            for i, order in enumerate(orders, 1):
                status_icon = '✅' if order.get('status') == 'paid' else '⏳'
                print(f'  {i}. {status_icon} {order.get("order_id", "")}')
                print(f'     客户: {order.get("customer_name", "")} | {order.get("customer_phone", "")}')
                print(f'     金额: ¥{order.get("amount", 0):.2f} | 产品: {order.get("product_name", "")}')
        else:
            print('  暂无订单')

        print('\n' + '=' * 60)
        print(f'  更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print('=' * 60)


def main():
    import sys

    cloud_url = sys.argv[1] if len(sys.argv) > 1 else None

    monitor = CloudMonitor(cloud_url)
    monitor.display_dashboard()


if __name__ == '__main__':
    main()
