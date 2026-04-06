# -*- coding: utf-8 -*-
"""
运营日报生成器 - 豆包运营代理人
自动统计每日运营数据并生成报告
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

class DailyReportGenerator:
    """日报生成器"""

    def __init__(self, db_path: str = "orders.db"):
        self.db_path = db_path

    def generate_daily_report(self, date: str = None) -> Dict[str, Any]:
        """
        生成日报

        Args:
            date: 日期，格式 YYYY-MM-DD

        Returns:
            日报数据
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 基础统计
        cursor.execute("""
            SELECT
                COUNT(*) as total_orders,
                SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as paid_orders,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
                SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) as total_amount,
                COUNT(DISTINCT customer_phone) as unique_customers
            FROM orders
            WHERE DATE(created_at) = ?
        """, (date,))

        row = cursor.fetchone()
        total_orders = row[0] or 0
        paid_orders = row[1] or 0
        pending_orders = row[2] or 0
        total_amount = row[3] or 0
        unique_customers = row[4] or 0

        # 产品销售排行
        cursor.execute("""
            SELECT product_name, COUNT(*) as count, SUM(amount) as amount
            FROM orders
            WHERE DATE(created_at) = ? AND status = 'paid'
            GROUP BY product_name
            ORDER BY amount DESC
        """, (date,))

        product_sales = [
            {'product': r[0], 'count': r[1], 'amount': r[2]}
            for r in cursor.fetchall()
        ]

        # 客户地域分布（基于手机号前缀估算）
        cursor.execute("""
            SELECT customer_phone, customer_name
            FROM orders
            WHERE DATE(created_at) = ?
            GROUP BY customer_phone
        """, (date,))

        regions = defaultdict(int)
        for phone, name in cursor.fetchall():
            if phone.startswith('1'):
                second_digit = int(phone[1]) if len(phone) > 1 else 0
                # 简单估算：1开头手机号分布
                if second_digit in [3, 4, 5, 7, 8]:
                    regions['华北/东北'] += 1
                elif second_digit in [6, 9]:
                    regions['华南/西南'] += 1
                else:
                    regions['华东/华中'] += 1

        # 转化漏斗
        conversion_rate = round(paid_orders / total_orders * 100, 2) if total_orders > 0 else 0

        conn.close()

        return {
            'report_date': date,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_orders': total_orders,
                'paid_orders': paid_orders,
                'pending_orders': pending_orders,
                'total_amount': total_amount,
                'unique_customers': unique_customers,
                'conversion_rate': conversion_rate
            },
            'product_sales': product_sales,
            'customer_regions': dict(regions),
            'alerts': self._generate_alerts(total_orders, pending_orders, conversion_rate)
        }

    def _generate_alerts(self, total: int, pending: int, conversion: float) -> List[str]:
        """生成预警信息"""
        alerts = []

        if pending > 5:
            alerts.append(f"⚠️ 有 {pending} 个待支付订单，请跟进")

        if conversion < 30 and total > 5:
            alerts.append(f"⚠️ 转化率偏低 ({conversion}%)，建议优化支付流程")

        if total == 0:
            alerts.append("📊 今日暂无订单，继续努力！")

        return alerts

    def generate_text_report(self, date: str = None) -> str:
        """生成文本格式日报"""
        report = self.generate_daily_report(date)

        lines = [
            "=" * 50,
            "      豆包运营代理人 - 每日运营报告",
            f"      日期: {report['report_date']}",
            "=" * 50,
            "",
            "📊 今日概览",
            "-" * 30,
            f"  总订单数: {report['summary']['total_orders']}",
            f"  已支付: {report['summary']['paid_orders']}",
            f"  待支付: {report['summary']['pending_orders']}",
            f"  收款金额: ¥{report['summary']['total_amount']:.2f}",
            f"  新增客户: {report['summary']['unique_customers']}",
            f"  转化率: {report['summary']['conversion_rate']}%",
            "",
        ]

        if report['product_sales']:
            lines.extend([
                "🏆 产品销售排行",
                "-" * 30,
            ])
            for i, p in enumerate(report['product_sales'], 1):
                lines.append(f"  {i}. {p['product']}: {p['count']}单 (¥{p['amount']:.2f})")
            lines.append("")

        if report['alerts']:
            lines.extend([
                "📢 运营提醒",
                "-" * 30,
            ])
            for alert in report['alerts']:
                lines.append(f"  {alert}")
            lines.append("")

        lines.extend([
            "=" * 50,
            f"  报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 50,
        ])

        return "\n".join(lines)

    def generate_html_report(self, date: str = None) -> str:
        """生成HTML格式日报"""
        report = self.generate_daily_report(date)

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>每日运营报告 - {report['report_date']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
        .card {{ background: white; border-radius: 10px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
        .stat {{ text-align: center; padding: 15px; background: #f9f9f9; border-radius: 8px; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f9f9f9; font-weight: 600; }}
        .alert {{ padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>豆包运营代理人</h1>
        <p>每日运营报告 - {report['report_date']}</p>
    </div>

    <div class="card">
        <h2>📊 今日概览</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{report['summary']['total_orders']}</div>
                <div class="stat-label">总订单数</div>
            </div>
            <div class="stat">
                <div class="stat-value">¥{report['summary']['total_amount']:.0f}</div>
                <div class="stat-label">收款金额</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report['summary']['conversion_rate']}%</div>
                <div class="stat-label">转化率</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report['summary']['paid_orders']}</div>
                <div class="stat-label">已支付</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report['summary']['pending_orders']}</div>
                <div class="stat-label">待支付</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report['summary']['unique_customers']}</div>
                <div class="stat-label">新客户</div>
            </div>
        </div>
    </div>
"""

        if report['product_sales']:
            html += """
    <div class="card">
        <h2>🏆 产品销售排行</h2>
        <table>
            <tr>
                <th>排名</th>
                <th>产品</th>
                <th>订单数</th>
                <th>金额</th>
            </tr>
"""
            for i, p in enumerate(report['product_sales'], 1):
                html += f"""
            <tr>
                <td>{i}</td>
                <td>{p['product']}</td>
                <td>{p['count']}</td>
                <td>¥{p['amount']:.2f}</td>
            </tr>
"""
            html += """
        </table>
    </div>
"""

        if report['alerts']:
            html += """
    <div class="card">
        <h2>📢 运营提醒</h2>
"""
            for alert in report['alerts']:
                html += f"""
        <div class="alert">{alert}</div>
"""
            html += """
    </div>
"""

        html += f"""
    <div class="card" style="text-align: center; color: #999; font-size: 12px;">
        报告生成时间: {report['generated_at']}
    </div>
</body>
</html>
"""
        return html


def main():
    """主函数"""
    generator = DailyReportGenerator()

    # 生成今日日报
    print("正在生成今日运营日报...")
    print()

    # 文本格式
    text_report = generator.generate_text_report()
    print(text_report)

    # 保存HTML报告
    html_report = generator.generate_html_report()
    filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_report)

    print(f"\n📄 HTML报告已保存: {filename}")


if __name__ == '__main__':
    main()
