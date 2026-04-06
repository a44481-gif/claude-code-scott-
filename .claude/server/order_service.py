# -*- coding: utf-8 -*-
"""
订单服务模块 - 豆包运营代理人
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from enum import Enum

class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "pending"       # 待支付
    PAID = "paid"            # 已支付
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed"   # 已完成
    CANCELLED = "cancelled"  # 已取消
    REFUNDED = "refunded"     # 已退款

class PayMethod(Enum):
    """支付方式"""
    ALIPAY = "alipay"
    WECHAT = "wechat"
    BANK = "bank"

@dataclass
class Order:
    """订单数据模型"""
    order_id: str = ""
    product_id: str = ""
    product_name: str = ""
    amount: float = 0.0
    status: str = "pending"
    pay_method: str = "alipay"
    customer_name: str = ""
    customer_phone: str = ""
    customer_email: str = ""
    customer_remark: str = ""
    trade_no: str = ""           # 支付宝交易号
    paid_at: str = ""            # 支付时间
    created_at: str = ""
    updated_at: str = ""
    extra_data: str = ""         # 额外数据JSON

class OrderService:
    """订单服务类"""

    def __init__(self, db_path: str = "orders.db"):
        self.db_path = db_path
        # Enable thread-safe connections
        self._local = __import__('threading').local()
        self._init_database()

    def _get_conn(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path, timeout=30)

    def _init_database(self):
        """初始化数据库"""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                pay_method TEXT NOT NULL DEFAULT 'alipay',
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                customer_email TEXT,
                customer_remark TEXT,
                trade_no TEXT,
                paid_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                extra_data TEXT
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_phone ON orders(customer_phone)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at)
        """)

        conn.commit()

    def _row_to_order(self, row: tuple) -> Order:
        """数据库行转换为Order对象"""
        return Order(
            order_id=row[0],
            product_id=row[1],
            product_name=row[2],
            amount=row[3],
            status=row[4],
            pay_method=row[5],
            customer_name=row[6],
            customer_phone=row[7],
            customer_email=row[8] or "",
            customer_remark=row[9] or "",
            trade_no=row[10] or "",
            paid_at=row[11] or "",
            created_at=row[12],
            updated_at=row[13],
            extra_data=row[14] or ""
        )

    def create_order(
        self,
        product_id: str,
        product_name: str,
        amount: float,
        customer_name: str,
        customer_phone: str,
        customer_email: str = "",
        customer_remark: str = "",
        pay_method: str = "alipay"
    ) -> Order:
        """
        创建新订单

        Args:
            product_id: 产品ID
            product_name: 产品名称
            amount: 金额
            customer_name: 客户姓名
            customer_phone: 客户电话
            customer_email: 客户邮箱
            customer_remark: 客户备注
            pay_method: 支付方式

        Returns:
            创建的订单对象
        """
        now = datetime.now()
        order_id = f"DD{now.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

        order = Order(
            order_id=order_id,
            product_id=product_id,
            product_name=product_name,
            amount=amount,
            status=OrderStatus.PENDING.value,
            pay_method=pay_method,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            customer_remark=customer_remark,
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )

        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO orders (
                order_id, product_id, product_name, amount, status, pay_method,
                customer_name, customer_phone, customer_email, customer_remark,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order.order_id,
            order.product_id,
            order.product_name,
            order.amount,
            order.status,
            order.pay_method,
            order.customer_name,
            order.customer_phone,
            order.customer_email,
            order.customer_remark,
            order.created_at,
            order.updated_at
        ))

        conn.commit()

        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """获取订单"""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()

        return self._row_to_order(row) if row else None

    def update_order_status(
        self,
        order_id: str,
        status: str,
        trade_no: str = "",
        paid_at: str = ""
    ) -> bool:
        """
        更新订单状态

        Args:
            order_id: 订单号
            status: 新状态
            trade_no: 交易号
            paid_at: 支付时间

        Returns:
            是否成功
        """
        now = datetime.now().isoformat()
        conn = self._get_conn()
        cursor = conn.cursor()

        if trade_no:
            cursor.execute("""
                UPDATE orders
                SET status = ?, trade_no = ?, paid_at = ?, updated_at = ?
                WHERE order_id = ?
            """, (status, trade_no, paid_at or now, now, order_id))
        else:
            cursor.execute("""
                UPDATE orders
                SET status = ?, updated_at = ?
                WHERE order_id = ?
            """, (status, now, order_id))

        success = cursor.rowcount > 0
        conn.commit()

        return success

    def get_orders_by_phone(self, phone: str) -> List[Order]:
        """根据手机号查询订单"""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM orders
            WHERE customer_phone = ?
            ORDER BY created_at DESC
        """, (phone,))

        rows = cursor.fetchall()

        return [self._row_to_order(row) for row in rows]

    def get_orders_by_status(self, status: str, limit: int = 100) -> List[Order]:
        """根据状态查询订单"""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM orders
            WHERE status = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (status, limit))

        rows = cursor.fetchall()

        return [self._row_to_order(row) for row in rows]

    def get_daily_stats(self, date: str = None) -> Dict[str, Any]:
        """
        获取每日统计

        Args:
            date: 日期，格式 YYYY-MM-DD，默认为今天

        Returns:
            统计数据
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        conn = self._get_conn()
        cursor = conn.cursor()

        # 当日订单数
        cursor.execute("""
            SELECT COUNT(*) FROM orders
            WHERE DATE(created_at) = ?
        """, (date,))
        total_orders = cursor.fetchone()[0]

        # 当日已支付订单数
        cursor.execute("""
            SELECT COUNT(*) FROM orders
            WHERE DATE(created_at) = ? AND status = 'paid'
        """, (date,))
        paid_orders = cursor.fetchone()[0]

        # 当日收款金额
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM orders
            WHERE DATE(created_at) = ? AND status = 'paid'
        """, (date,))
        total_amount = cursor.fetchone()[0]

        # 当日新客户数 (手机号去重)
        cursor.execute("""
            SELECT COUNT(DISTINCT customer_phone) FROM orders
            WHERE DATE(created_at) = ?
        """, (date,))
        new_customers = cursor.fetchone()[0]


        return {
            'date': date,
            'total_orders': total_orders,
            'paid_orders': paid_orders,
            'pending_orders': total_orders - paid_orders,
            'total_amount': total_amount,
            'new_customers': new_customers,
            'conversion_rate': round(paid_orders / total_orders * 100, 2) if total_orders > 0 else 0
        }

    def get_weekly_stats(self) -> Dict[str, Any]:
        """获取本周统计"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start_str = week_start.strftime('%Y-%m-%d')

        conn = self._get_conn()
        cursor = conn.cursor()

        # 本周订单数
        cursor.execute("""
            SELECT COUNT(*) FROM orders
            WHERE DATE(created_at) >= ?
        """, (week_start_str,))
        total_orders = cursor.fetchone()[0]

        # 本周收款金额
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM orders
            WHERE DATE(created_at) >= ? AND status = 'paid'
        """, (week_start_str,))
        total_amount = cursor.fetchone()[0]

        # 每日明细
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count, COALESCE(SUM(amount), 0) as amount
            FROM orders
            WHERE DATE(created_at) >= ? AND status = 'paid'
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (week_start_str,))

        daily_data = [
            {'date': row[0], 'count': row[1], 'amount': row[2]}
            for row in cursor.fetchall()
        ]


        return {
            'week_start': week_start_str,
            'week_end': today.strftime('%Y-%m-%d'),
            'total_orders': total_orders,
            'total_amount': total_amount,
            'daily_data': daily_data
        }

    def export_orders(
        self,
        start_date: str = None,
        end_date: str = None,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """
        导出订单数据

        Args:
            start_date: 开始日期
            end_date: 结束日期
            status: 订单状态

        Returns:
            订单列表
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        query = "SELECT * FROM orders WHERE 1=1"
        params = []

        if start_date:
            query += " AND DATE(created_at) >= ?"
            params.append(start_date)

        if end_date:
            query += " AND DATE(created_at) <= ?"
            params.append(end_date)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        orders = []
        for row in rows:
            order = self._row_to_order(row)
            orders.append({
                'order_id': order.order_id,
                'product_name': order.product_name,
                'amount': order.amount,
                'status': order.status,
                'customer_name': order.customer_name,
                'customer_phone': order.customer_phone,
                'customer_email': order.customer_email,
                'trade_no': order.trade_no,
                'paid_at': order.paid_at,
                'created_at': order.created_at
            })

        return orders


# 产品配置
PRODUCTS = {
    'ai-operation-basic': {
        'name': 'AI代运营基础版',
        'price': 999,
        'period': '月付',
        'description': '每月20条AI内容生成、基础数据分析'
    },
    'ai-operation-pro': {
        'name': 'AI代运营进阶版',
        'price': 2999,
        'period': '月付',
        'description': '每日内容生成不限量、竞品分析、SEO优化'
    },
    'prompt-custom': {
        'name': 'AI提示词定制',
        'price': 599,
        'period': '次',
        'description': '按需定制提示词、3次免费修改'
    },
    'script-dev': {
        'name': 'AI脚本开发',
        'price': 1999,
        'period': '次',
        'description': '按场景定制脚本、多版本备选'
    },
    'digital-human': {
        'name': 'AI数字人视频',
        'price': 399,
        'period': '条',
        'description': '模板数字人、配音合成、24h内交付'
    },
    'custom': {
        'name': '自定义金额',
        'price': 0,
        'period': '次',
        'description': '自定义服务金额'
    }
}
