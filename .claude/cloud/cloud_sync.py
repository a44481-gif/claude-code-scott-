#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地-云端数据同步脚本
将云端订单同步到本地 SQLite 数据库备份
"""

import requests
import sqlite3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
CLOUD_API_URL = os.getenv('CLOUD_API_URL', 'https://your-cloud-app.railway.app')
LOCAL_DB_PATH = './data/orders_backup.db'
SYNC_INTERVAL = 300  # 5分钟同步一次


class CloudSync:
    """云端数据同步类"""

    def __init__(self, cloud_url: str, local_db: str):
        self.cloud_url = cloud_url.rstrip('/')
        self.local_db = local_db
        self._init_local_db()

    def _init_local_db(self):
        """初始化本地数据库"""
        os.makedirs(os.path.dirname(self.local_db), exist_ok=True)
        conn = sqlite3.connect(self.local_db)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                customer_name TEXT,
                customer_phone TEXT,
                customer_email TEXT,
                paid_at TEXT,
                created_at TEXT NOT NULL,
                synced_at TEXT,
                source TEXT DEFAULT 'cloud'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_time TEXT NOT NULL,
                orders_synced INTEGER,
                status TEXT
            )
        """)

        conn.commit()
        conn.close()

    def fetch_cloud_orders(self) -> list:
        """从云端获取订单"""
        try:
            resp = requests.get(
                f'{self.cloud_url}/api/get-orders',
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get('orders', [])
            else:
                print(f'获取云端订单失败: {resp.status_code}')
                return []
        except Exception as e:
            print(f'连接云端失败: {str(e)}')
            return []

    def save_to_local(self, orders: list) -> int:
        """保存到本地数据库"""
        conn = sqlite3.connect(self.local_db)
        cursor = conn.cursor()
        synced_count = 0

        for order in orders:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO orders
                    (order_id, product_id, product_name, amount, status,
                     customer_name, customer_phone, customer_email,
                     paid_at, created_at, synced_at, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'cloud')
                """, (
                    order.get('order_id'),
                    order.get('product_id', ''),
                    order.get('product_name', ''),
                    order.get('amount', 0),
                    order.get('status', ''),
                    order.get('customer_name', ''),
                    order.get('customer_phone', ''),
                    order.get('customer_email', ''),
                    order.get('paid_at', ''),
                    order.get('created_at', ''),
                    datetime.now().isoformat()
                ))
                synced_count += 1
            except Exception as e:
                print(f'保存订单失败: {order.get("order_id")} - {str(e)}')

        conn.commit()
        conn.close()
        return synced_count

    def log_sync(self, count: int, status: str):
        """记录同步日志"""
        conn = sqlite3.connect(self.local_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sync_log (sync_time, orders_synced, status)
            VALUES (?, ?, ?)
        """, (datetime.now().isoformat(), count, status))

        conn.commit()
        conn.close()

    def sync(self) -> dict:
        """执行同步"""
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 开始同步...')

        # 获取云端订单
        orders = self.fetch_cloud_orders()

        if orders:
            # 保存到本地
            synced = self.save_to_local(orders)
            self.log_sync(synced, 'success')
            print(f'同步完成: {synced} 条订单')
            return {'success': True, 'synced': synced, 'total': len(orders)}
        else:
            self.log_sync(0, 'no_data')
            print('没有新订单需要同步')
            return {'success': True, 'synced': 0}

    def get_local_stats(self) -> dict:
        """获取本地统计"""
        conn = sqlite3.connect(self.local_db)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM orders')
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'paid'")
        paid = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM orders WHERE status = 'paid'")
        amount = cursor.fetchone()[0]

        cursor.execute('SELECT MAX(synced_at) FROM orders')
        last_sync = cursor.fetchone()[0]

        conn.close()

        return {
            'total_orders': total,
            'paid_orders': paid,
            'total_amount': amount,
            'last_sync': last_sync
        }


def main():
    """主函数"""
    print('=' * 50)
    print('   SCOTT豆包赚钱 - 云端数据同步')
    print('=' * 50)

    sync = CloudSync(CLOUD_API_URL, LOCAL_DB_PATH)

    # 执行同步
    result = sync.sync()

    # 显示本地统计
    stats = sync.get_local_stats()
    print('\n本地备份统计:')
    print(f'  总订单: {stats["total_orders"]}')
    print(f'  已付款: {stats["paid_orders"]}')
    print(f'  总金额: ¥{stats["total_amount"]:.2f}')
    print(f'  最后同步: {stats["last_sync"]}')

    return result


if __name__ == '__main__':
    main()
