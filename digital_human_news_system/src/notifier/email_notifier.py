#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
邮件通知模块
Email Notifier Module
"""

import os
import json
import smtplib
from datetime import datetime
from typing import Dict, Any, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..utils.config_loader import get_config
from ..utils.logger import setup_logger


class EmailNotifier:
    """邮件通知发送器"""

    def __init__(self):
        self.config = get_config()
        self.logger = setup_logger('notifier')
        self.email_config = self.config.get_section('email')

    def send_daily_report(self, report_data: Dict[str, Any]) -> bool:
        """
        发送每日执行报告邮件

        Args:
            report_data: 报告数据

        Returns:
            是否发送成功
        """
        try:
            subject = self._generate_subject(report_data)
            html_body = self._generate_html_report(report_data)
            text_body = self._generate_text_report(report_data)
            success = self._send_email(subject, html_body, text_body)

            if success:
                self.logger.info("每日报告邮件发送成功")
            return success
        except Exception as e:
            self.logger.error(f"发送邮件失败: {str(e)}")
            return False

    def _generate_subject(self, report_data: Dict[str, Any]) -> str:
        """生成邮件主题"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        videos_count = report_data.get('videos_created', 0)
        return f"【每日报告】{date_str} AI数字人新闻系统 - 生成{videos_count}个视频"

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """生成HTML格式报告"""
        date_str = datetime.now().strftime('%Y年%m月%d日')
        execution_time = report_data.get('execution_time', 0)
        news_fetched = report_data.get('news_fetched', 0)
        news_passed = report_data.get('news_passed', 0)
        videos_created = report_data.get('videos_created', 0)
        videos_published = report_data.get('videos_published', 0)

        category_stats = report_data.get('category_stats', {})
        category_html = ""
        for cat, count in category_stats.items():
            cat_name = {'buddhism': '佛学正能量', 'taoism': '道教正能量',
                       'pets': '宠物', 'agriculture': '农业', 'general': '通用'}.get(cat, cat)
            category_html += f"<li>{cat_name}: {count} 条</li>"

        douyin_status = report_data.get('douyin_status', {})
        youtube_status = report_data.get('youtube_status', {})
        errors = report_data.get('errors', [])

        error_html = "<p style='color: green;'>✓ 今日执行无错误</p>" if not errors else f"<p style='color: red;'>有 {len(errors)} 个错误</p>"
        summary = report_data.get('summary', '系统正常运行')

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 8px; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
        .stat-box {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; font-size: 0.9em; }}
        .success {{ color: #4CAF50; }}
        .contact {{ text-align: center; color: #666; margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 8px; }}
        .contact h4 {{ color: #333; margin-bottom: 10px; }}
        .contact a {{ color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI数字人新闻系统 - 每日报告</h1>
            <p>{date_str}</p>
        </div>

        <div class="section">
            <h2>📊 执行概览</h2>
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-number">{news_fetched}</div>
                    <div class="stat-label">抓取新闻</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{news_passed}</div>
                    <div class="stat-label">筛选通过</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{videos_created}</div>
                    <div class="stat-label">生成视频</div>
                </div>
            </div>
            <p style="margin-top: 15px;">执行耗时: <strong>{execution_time:.1f}</strong> 秒</p>
        </div>

        <div class="section">
            <h2>📰 分类统计</h2>
            <ul>{category_html}</ul>
        </div>

        <div class="section">
            <h2>🎬 视频发布</h2>
            <p>抖音: 成功 <strong class="success">{douyin_status.get('success', 0)}</strong> 个</p>
            <p>YouTube: 成功 <strong class="success">{youtube_status.get('success', 0)}</strong> 个</p>
            <p style="margin-top: 10px;"><strong>总计发布: {videos_published} 个视频</strong></p>
        </div>

        <div class="section">
            {error_html}
        </div>

        <div class="section" style="background: #e8f5e9;">
            <h2>✨ 今日成果</h2>
            <p>{summary}</p>
        </div>

        <div class="contact">
            <h4>📞 联系我们</h4>
            <p>📧 邮箱: <a href="mailto:scott365888@gmail.com">scott365888@gmail.com</a></p>
            <p>💬 微信: <strong>PTS9800</strong></p>
            <p style="font-size: 0.9em; color: #999;">商务合作 | 内容授权 | 技术支持</p>
        </div>

        <div style="text-align: center; color: #999; margin-top: 20px;">
            <p>本报告由 AI数字人新闻内容生产与全球分发系统 自动生成</p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""

    def _generate_text_report(self, report_data: Dict[str, Any]) -> str:
        """生成纯文本格式报告"""
        date_str = datetime.now().strftime('%Y年%m月%d日')
        return f"""
========================================
AI数字人新闻系统 - 每日执行报告
{date_str}
========================================

【执行概览】
- 抓取新闻: {report_data.get('news_fetched', 0)} 条
- 筛选通过: {report_data.get('news_passed', 0)} 条
- 生成视频: {report_data.get('videos_created', 0)} 个
- 发布视频: {report_data.get('videos_published', 0)} 个
- 执行耗时: {report_data.get('execution_time', 0):.1f} 秒

【今日成果】
{report_data.get('summary', '系统正常运行')}

========================================
📞 联系邮箱: scott365888@gmail.com
📱 微信: PTS9800
========================================
"""

    def _send_email(self, subject: str, html_body: str, text_body: str) -> bool:
        """发送邮件"""
        smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = self.email_config.get('smtp_port', 587)
        sender = self.email_config.get('sender', 'scott365888@gmail.com')
        password = self.email_config.get('password', '')
        receiver = self.email_config.get('receiver', 'scott365888@gmail.com')

        if not password or password == 'YOUR_EMAIL_PASSWORD':
            self.logger.error("邮箱密码未配置，跳过发送")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = receiver
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, [receiver], msg.as_string())

            self.logger.info(f"邮件已发送至: {receiver}")
            return True

        except Exception as e:
            self.logger.error(f"发送邮件失败: {str(e)}")
            return False

    def send_custom_email(self, subject: str, html_body: str, text_body: str = None) -> bool:
        """发送自定义邮件"""
        if text_body is None:
            text_body = html_body.replace('<[^>]+>', '')
        return self._send_email(subject, html_body, text_body)
