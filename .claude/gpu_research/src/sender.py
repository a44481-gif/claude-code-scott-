# -*- coding: utf-8 -*-
"""
郵件發送器
Email Sender Module

支持 SMTP 郵箱發送
"""

import smtplib
import time
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from .config import config

# Windows 控制台 UTF-8 支持
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class EmailSender:
    """
    郵件發送器
    """

    def __init__(self):
        self.smtp_host = config.email.smtp_host
        self.smtp_port = config.email.smtp_port
        self.sender_email = config.email.sender_email
        self.auth_code = config.email.sender_auth_code
        self.use_ssl = config.email.use_ssl
        self.max_retries = 3
        self.retry_delay = 5

    def send_email(self, subject: str, content: str,
                   recipients: List[str],
                   content_type: str = 'html',
                   attachments: List[str] = None) -> bool:
        """
        發送郵件

        Args:
            subject: 郵件主題
            content: 郵件內容
            recipients: 收件人列表
            content_type: 內容類型 ('html' 或 'plain')
            attachments: 附件路徑列表

        Returns:
            bool: 發送是否成功
        """
        if not self.auth_code:
            print("❌ 錯誤: 郵箱授權碼未設置")
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = ', '.join(recipients)

        # 添加內容
        if content_type == 'html':
            html_part = MIMEText(content, 'html', 'utf-8')
            msg.attach(html_part)

            # 同時添加純文字版本
            text_content = self._strip_html(content)
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
        else:
            text_part = MIMEText(content, 'plain', 'utf-8')
            msg.attach(text_part)

        # 添加附件
        if attachments:
            for filepath in attachments:
                self._add_attachment(msg, filepath)

        # 發送郵件（帶重試機制）
        for attempt in range(self.max_retries):
            try:
                return self._send_with_smtp(msg, recipients)
            except Exception as e:
                print(f"⚠️ 發送失敗 (嘗試 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    print("❌ 達到最大重試次數，發送失敗")
                    return False

        return False

    def _send_with_smtp(self, msg: MIMEMultipart, recipients: List[str]) -> bool:
        """使用 SMTP 發送郵件"""
        if self.use_ssl:
            server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
        else:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()

        try:
            server.login(self.sender_email, self.auth_code)
            server.sendmail(self.sender_email, recipients, msg.as_string())
            print(f"✅ 郵件已成功發送至: {', '.join(recipients)}")
            return True
        finally:
            server.quit()

    def _add_attachment(self, msg: MIMEMultipart, filepath: str):
        """添加附件"""
        try:
            with open(filepath, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = filepath.split('/')[-1].split('\\')[-1]
                part.add_header('Content-Disposition', f'attachment; filename= {filename}')
                msg.attach(part)
        except Exception as e:
            print(f"⚠️ 添加附件失敗: {filepath} - {e}")

    def _strip_html(self, html: str) -> str:
        """去除 HTML 標籤，生成純文字版本"""
        import re
        # 簡單的 HTML 去除
        text = re.sub(r'<br\s*/?>', '\n', html)
        text = re.sub(r'<p[^>]*>', '\n', text)
        text = re.sub(r'</p>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        return text.strip()

    def send_report(self, report_html: str,
                    recipients: List[str] = None,
                    subject: str = None) -> bool:
        """
        發送研究報告

        Args:
            report_html: HTML 報告內容
            recipients: 收件人列表
            subject: 郵件主題

        Returns:
            bool: 發送是否成功
        """
        if recipients is None:
            recipients = [self.sender_email]

        if subject is None:
            from datetime import datetime
            subject = f"顯卡電源線燒毀 - 全球平台研究報告 {datetime.now().strftime('%Y年%m月%d日')}"

        return self.send_email(
            subject=subject,
            content=report_html,
            recipients=recipients,
            content_type='html'
        )

    def test_connection(self) -> bool:
        """
        測試 SMTP 連接

        Returns:
            bool: 連接是否成功
        """
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                server.starttls()

            server.login(self.sender_email, self.auth_code)
            server.quit()
            print("✅ SMTP 連接測試成功")
            return True
        except Exception as e:
            print(f"❌ SMTP 連接測試失敗: {e}")
            return False


def send_test_email():
    """發送測試郵件"""
    sender = EmailSender()
    sender.send_email(
        subject="測試郵件 - GPU 研究工具",
        content="<h1>測試郵件</h1><p>這是一封測試郵件。</p>",
        recipients=['h13751019800@163.com']
    )


if __name__ == '__main__':
    send_test_email()
