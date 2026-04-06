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
from email.mime.base import MIMEBase
from email import encoders

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
            report_data: 报告数据，包含:
                - news_fetched: 抓取的新闻数量
                - news_passed: 通过筛选的新闻数量
                - videos_created: 生成的视频数量
                - videos_published: 发布的视频数量
                - douyin_status: 抖音发布状态
                - youtube_status: YouTube发布状态
                - errors: 错误列表
                - execution_time: 执行耗时

        Returns:
            是否发送成功
        """
        try:
            # 准备邮件内容
            subject = self._generate_subject(report_data)
            html_body = self._generate_html_report(report_data)
            text_body = self._generate_text_report(report_data)

            # 发送邮件
            success = self._send_email(subject, html_body, text_body)

            if success:
                self.logger.info("每日报告邮件发送成功")
            else:
                self.logger.error("每日报告邮件发送失败")

            return success

        except Exception as e:
            self.logger.error(f"发送邮件失败: {str(e)}")
            return False

    def _generate_subject(self, report_data: Dict[str, Any]) -> str:
        """
        生成邮件主题

        Args:
            report_data: 报告数据

        Returns:
            邮件主题
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        videos_count = report_data.get('videos_created', 0)
        published_count = report_data.get('videos_published', 0)

        return f"【每日报告】{date_str} AI数字人新闻系统 - 生成{videos_count}个视频，成功发布{published_count}个"

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """
        生成HTML格式报告

        Args:
            report_data: 报告数据

        Returns:
            HTML报告内容
        """
        date_str = datetime.now().strftime('%Y年%m月%d日')
        execution_time = report_data.get('execution_time', 0)

        # 分类统计
        category_stats = report_data.get('category_stats', {})
        category_html = ""
        for cat, count in category_stats.items():
            cat_name = {
                'buddhism': '佛学正能量',
                'taoism': '道教正能量',
                'pets': '宠物',
                'agriculture': '农业',
                'general': '通用'
            }.get(cat, cat)
            category_html += f"<li>{cat_name}: {count} 条</li>"

        # 发布状态
        douyin_status = report_data.get('douyin_status', {})
        youtube_status = report_data.get('youtube_status', {})

        # 错误信息
        errors = report_data.get('errors', [])
        error_html = ""
        if errors:
            error_html = "<h3 style='color: red;'>执行错误</h3><ul>"
            for error in errors[:5]:  # 最多显示5个错误
                error_html += f"<li>{error}</li>"
            error_html += "</ul>"
        else:
            error_html = "<p style='color: green;'>✓ 今日执行无错误</p>"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
                .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 8px; }}
                .stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
                .stat-box {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
                .stat-label {{ color: #666; font-size: 0.9em; }}
                .success {{ color: #4CAF50; }}
                .warning {{ color: #FFC107; }}
                .platform {{ display: flex; justify-content: space-between; margin: 10px 0; }}
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
                            <div class="stat-number">{report_data.get('news_fetched', 0)}</div>
                            <div class="stat-label">抓取新闻</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{report_data.get('news_passed', 0)}</div>
                            <div class="stat-label">筛选通过</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{report_data.get('videos_created', 0)}</div>
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
                    <h2>🎬 视频发布状态</h2>
                    <h3>抖音 (Douyin)</h3>
                    <div class="platform">
                        <span>成功发布: <strong class="success">{douyin_status.get('success', 0)}</strong> 个</span>
                        <span>失败: <strong>{douyin_status.get('failed', 0)}</strong> 个</span>
                    </div>

                    <h3>YouTube</h3>
                    <div class="platform">
                        <span>成功发布: <strong class="success">{youtube_status.get('success', 0)}</strong> 个</span>
                        <span>失败: <strong>{youtube_status.get('failed', 0)}</strong> 个</span>
                    </div>

                    <p style="margin-top: 15px; font-size: 1.2em;">
                        <strong>总计发布: {report_data.get('videos_published', 0)} 个视频</strong>
                    </p>
                </div>

                <div class="section">
                    {error_html}
                </div>

                <div class="section" style="background: #e8f5e9;">
                    <h2>✨ 今日成果</h2>
                    <p>{report_data.get('summary', '系统正常运行，成功完成新闻抓取、内容创作和视频发布任务。')}</p>
                </div>

                <div style="text-align: center; color: #999; margin-top: 30px;">
                    <p>本报告由 AI数字人新闻内容生产与全球分发系统 自动生成</p>
                    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _generate_text_report(self, report_data: Dict[str, Any]) -> str:
        """
        生成纯文本格式报告

        Args:
            report_data: 报告数据

        Returns:
            文本报告内容
        """
        date_str = datetime.now().strftime('%Y年%m月%d日')

        text = f"""
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

【分类统计】
"""

        category_stats = report_data.get('category_stats', {})
        for cat, count in category_stats.items():
            cat_name = {
                'buddhism': '佛学正能量',
                'taoism': '道教正能量',
                'pets': '宠物',
                'agriculture': '农业',
                'general': '通用'
            }.get(cat, cat)
            text += f"- {cat_name}: {count} 条\n"

        text += f"""
【发布平台状态】
- 抖音: 成功 {report_data.get('douyin_status', {{}}).get('success', 0)} 个
- YouTube: 成功 {report_data.get('youtube_status', {{}}).get('success', 0)} 个

【执行错误】
"""

        errors = report_data.get('errors', [])
        if errors:
            for error in errors[:5]:
                text += f"- {error}\n"
        else:
            text += "无\n"

        text += f"""
【成果总结】
{report_data.get('summary', '系统正常运行')}

========================================
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================================
"""

        return text

    def _send_email(
        self,
        subject: str,
        html_body: str,
        text_body: str
    ) -> bool:
        """
        发送邮件

        Args:
            subject: 邮件主题
            html_body: HTML格式正文
            text_body: 纯文本正文

        Returns:
            是否发送成功
        """
        smtp_server = self.email_config.get('smtp_server', 'smtp.163.com')
        smtp_port = self.email_config.get('smtp_port', 465)
        sender = self.email_config.get('sender', '')
        password = self.email_config.get('password', '')
        receiver = self.email_config.get('receiver', '')

        # 检查配置
        if not sender or not receiver:
            self.logger.error("邮件配置不完整，跳过发送")
            return False

        if password == 'YOUR_EMAIL_PASSWORD' or not password:
            self.logger.error("邮箱密码未配置，跳过发送")
            return False

        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = receiver

            # 添加正文
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            html_part = MIMEText(html_body, 'html', 'utf-8')

            msg.attach(text_part)
            msg.attach(html_part)

            # 发送邮件
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender, password)
                server.sendmail(sender, [receiver], msg.as_string())

            self.logger.info(f"邮件已发送至: {receiver}")
            return True

        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP发送失败: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"发送邮件失败: {str(e)}")
            return False

    def send_error_alert(self, error_message: str, context: str = "") -> bool:
        """
        发送错误告警邮件

        Args:
            error_message: 错误信息
            context: 错误上下文

        Returns:
            是否发送成功
        """
        subject = f"【告警】AI数字人新闻系统错误 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        html_body = f"""
        <html>
        <body>
            <h2 style="color: red;">⚠️ 系统错误告警</h2>
            <p><strong>错误时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>错误信息:</strong></p>
            <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{error_message}</pre>
            <p><strong>上下文:</strong></p>
            <pre style="background: #fff3cd; padding: 10px; border-radius: 5px;">{context}</pre>
            <p>请及时检查系统状态。</p>
        </body>
        </html>
        """

        text_body = f"""
        系统错误告警

        错误时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        错误信息: {error_message}
        上下文: {context}

        请及时检查系统状态。
        """

        return self._send_email(subject, html_body, text_body)
