#!/usr/bin/env python3
"""
💰 短视频收益追踪系统
自动记录和统计各平台收入
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import pandas as pd

# 配置
DATA_DIR = Path("data/income")
DATA_DIR.mkdir(parents=True, exist_ok=True)

class IncomeTracker:
    """收益追踪器"""

    def __init__(self):
        self.income_file = DATA_DIR / "income_records.csv"
        self.init_file()

    def init_file(self):
        """初始化CSV文件"""
        if not self.income_file.exists():
            with open(self.income_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    '日期', '平台', '来源', '金额(CNY)',
                    '备注', '截图路径', '已提现'
                ])

    def add_income(self, platform: str, source: str, amount: float,
                   note: str = "", screenshot: str = ""):
        """
        添加收入记录

        Args:
            platform: 平台（抖音/TikTok/YouTube/品牌合作）
            source: 来源（激励计划/带货/直播/合作）
            amount: 金额（人民币）
            note: 备注
            screenshot: 截图路径
        """
        with open(self.income_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d'),
                platform, source, amount, note, screenshot, '否'
            ])
        print(f"✅ 已添加收入记录：{platform} - {source} - ¥{amount}")

    def get_summary(self, days: int = 30) -> Dict:
        """
        获取收入汇总

        Args:
            days: 统计天数

        Returns:
            汇总数据字典
        """
        df = pd.read_csv(self.income_file)
        df['日期'] = pd.to_datetime(df['日期'])

        # 筛选最近N天
        start_date = datetime.now() - timedelta(days=days)
        df = df[df['日期'] >= start_date]

        # 按平台汇总
        platform_summary = df.groupby('平台')['金额(CNY)'].sum().to_dict()

        # 按来源汇总
        source_summary = df.groupby('来源')['金额(CNY)'].sum().to_dict()

        # 总计
        total = df['金额(CNY)'].sum()

        return {
            '统计周期': f"{start_date.strftime('%Y-%m-%d')} 至 {datetime.now().strftime('%Y-%m-%d')}",
            '总收入': total,
            '平台分布': platform_summary,
            '来源分布': source_summary,
            '记录数': len(df)
        }

    def get_daily_report(self, days: int = 7) -> List[Dict]:
        """获取每日报告"""
        df = pd.read_csv(self.income_file)
        df['日期'] = pd.to_datetime(df['日期'])

        start_date = datetime.now() - timedelta(days=days)
        df = df[df['日期'] >= start_date]

        daily = df.groupby('日期').agg({
            '金额(CNY)': 'sum',
            '平台': 'count'
        }).reset_index()

        daily.columns = ['日期', '总收入', '记录数']
        daily['日期'] = daily['日期'].dt.strftime('%Y-%m-%d')

        return daily.to_dict('records')

    def mark_withdrawn(self, date: str):
        """标记已提现"""
        df = pd.read_csv(self.income_file)
        df.loc[df['日期'] == date, '已提现'] = '是'
        df.to_csv(self.income_file, index=False)
        print(f"✅ 已标记 {date} 的收入为已提现")

def generate_income_report(tracker: IncomeTracker) -> str:
    """生成收入报告HTML"""
    summary = tracker.get_summary(days=30)
    daily = tracker.get_daily_report(days=7)

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>收益报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .card {{ background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 10px 0; }}
        .total {{ font-size: 32px; color: #e91e63; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #8B7355; color: white; }}
        .platform {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        .tag {{ background: #8B7355; color: white; padding: 5px 15px; border-radius: 20px; }}
    </style>
</head>
<body>
    <h1>💰 短视频收益报告</h1>
    <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

    <div class="card">
        <h2>📊 本月汇总</h2>
        <p class="total">¥ {summary['总收入']:,.2f}</p>
        <p>统计周期：{summary['统计周期']}</p>
        <p>收入记录：{summary['记录数']} 条</p>
    </div>

    <div class="card">
        <h2>📱 平台分布</h2>
        <div class="platform">
            {''.join([f'<span class="tag">{k}: ¥{v:,.2f}</span>' for k, v in summary['平台分布'].items()])}
        </div>
    </div>

    <div class="card">
        <h2>💵 来源分布</h2>
        <div class="platform">
            {''.join([f'<span class="tag">{k}: ¥{v:,.2f}</span>' for k, v in summary['来源分布'].items()])}
        </div>
    </div>

    <div class="card">
        <h2>📅 近7日收入</h2>
        <table>
            <tr><th>日期</th><th>收入</th><th>记录数</th></tr>
            {''.join([f'<tr><td>{d["日期"]}</td><td>¥{d["总收入"]:,.2f}</td><td>{d["记录数"]}</td></tr>' for d in daily])}
        </table>
    </div>
</body>
</html>
"""
    return html

def send_income_report(report_html: str):
    """发送收入报告到邮箱"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    with open('config/email_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    smtp = config['smtp']
    sender = config['sender']
    recipient = config['recipient']

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'💰 短视频收益报告 - {datetime.now().strftime("%Y-%m-%d")}'
    msg['From'] = sender['email']
    msg['To'] = recipient['email']

    msg.attach(MIMEText(report_html, 'html'))

    try:
        server = smtplib.SMTP(smtp['server'], smtp['port'], timeout=30)
        server.ehlo()
        server.starttls()
        server.login(sender['email'], sender['password'])
        server.sendmail(sender['email'], [recipient['email']], msg.as_string())
        server.quit()
        print("✅ 收益报告已发送到邮箱！")
    except Exception as e:
        print(f"❌ 发送失败：{e}")

# ==================== 使用示例 ====================

if __name__ == "__main__":
    tracker = IncomeTracker()

    # 添加示例收入记录（实际使用时删除）
    print("\n" + "="*50)
    print("💰 收入追踪系统")
    print("="*50)

    # 查看汇总
    summary = tracker.get_summary(days=30)
    print(f"\n📊 本月收入汇总：¥{summary['总收入']:,.2f}")
    print(f"📝 记录数：{summary['记录数']} 条")

    if summary['平台分布']:
        print("\n📱 平台分布：")
        for platform, amount in summary['平台分布'].items():
            print(f"   {platform}: ¥{amount:,.2f}")

    if summary['来源分布']:
        print("\n💵 来源分布：")
        for source, amount in summary['来源分布'].items():
            print(f"   {source}: ¥{amount:,.2f}")

    # 生成并发送报告
    print("\n📧 生成收益报告...")
    report = generate_income_report(tracker)
    send_income_report(report)

    print("\n" + "="*50)
    print("✅ 完成！")
    print("="*50)
