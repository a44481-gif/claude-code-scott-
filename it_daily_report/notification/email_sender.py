"""
Email Sender for IT Hardware Daily Report
Supports SMTP SSL (163.com) with HTML reports and JSON attachments
"""

import os
import sys
import ssl
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Union, Optional

# Fix Windows GBK encoding for print statements
try:
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class EmailSender:
    """Unified email sender with SMTP SSL support"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.smtp_config = self.config.get('smtp', {})
        self.recipients = self.config.get('recipients', {})

    def _load_config(self, config_path: str) -> Dict:
        if config_path and os.path.exists(config_path):
            with open(config_path, encoding='utf-8') as f:
                return json.load(f)
        base = os.path.dirname(os.path.dirname(__file__))
        cfg = os.path.join(base, 'config', 'email_config.json')
        if os.path.exists(cfg):
            with open(cfg, encoding='utf-8') as f:
                return json.load(f)
        return {}

    def validate_config(self) -> bool:
        required = ['server', 'port', 'username', 'password']
        for key in required:
            if not self.smtp_config.get(key):
                print(f"[Email] Missing required config: {key}")
                return False
        return True

    def send(
        self,
        subject: str,
        html_body: str,
        to_email: Optional[Union[str, List[str]]] = None,
        attachments: Optional[List[str]] = None,
        cc: Optional[List[str]] = None,
        text_body: Optional[str] = None
    ) -> Dict:
        """Send email with HTML body and optional attachments"""

        if not self.validate_config():
            return {"success": False, "error": "Invalid email configuration"}

        # Resolve recipients
        primary_recipients = to_email or self.recipients.get('primary', [])
        if isinstance(primary_recipients, str):
            primary_recipients = [primary_recipients]

        all_recipients = list(primary_recipients)
        if cc:
            all_recipients.extend(cc)
        elif self.recipients.get('cc'):
            cc_list = self.recipients['cc']
            all_recipients.extend(cc_list)

        # Build message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.smtp_config.get('sender_name', 'IT Report')} <{self.smtp_config['username']}>"
        msg['To'] = ', '.join(primary_recipients)
        if cc:
            msg['Cc'] = ', '.join(cc)

        # Add text version
        if text_body:
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        else:
            # Generate plain text from HTML
            import re
            plain = re.sub(r'<[^>]+>', '', html_body)
            plain = re.sub(r'\n{3,}', '\n\n', plain)
            msg.attach(MIMEText(plain[:2000], 'plain', 'utf-8'))

        # Add HTML version
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # Add attachments
        if attachments:
            for filepath in attachments:
                if os.path.exists(filepath):
                    self._add_attachment(msg, filepath)
                    print(f"[Email] Attached: {os.path.basename(filepath)}")
                else:
                    print(f"[Email] Warning: Attachment not found: {filepath}")

        # Send via SMTP
        try:
            return self._send_smtp(msg, all_recipients)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_smtp(self, msg: MIMEMultipart, recipients: List[str]) -> Dict:
        """Send via SMTP SSL"""
        server = self.smtp_config['server']
        port = self.smtp_config['port']
        username = self.smtp_config['username']
        password = self.smtp_config['password']
        use_ssl = self.smtp_config.get('use_ssl', True)
        use_tls = self.smtp_config.get('use_tls', False)

        context = ssl.create_default_context()

        print(f"[Email] Connecting to {server}:{port}...")

        if use_ssl:
            with smtplib.SMTP_SSL(server, port, context=context) as smtp:
                smtp.login(username, password)
                smtp.send_message(msg, username, recipients)
        else:
            with smtplib.SMTP(server, port) as smtp:
                if use_tls:
                    smtp.starttls(context=context)
                smtp.login(username, password)
                smtp.send_message(msg, username, recipients)

        print(f"[Email] ✅ Sent successfully to {recipients}")
        return {
            "success": True,
            "message": f"Email sent to {len(recipients)} recipient(s)",
            "recipients": recipients
        }

    def _add_attachment(self, msg: MIMEMultipart, filepath: str):
        """Add file attachment"""
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)

    def send_daily_report(
        self,
        html_report_path: str,
        json_data_path: Optional[str] = None,
        date_str: Optional[str] = None
    ) -> Dict:
        """Send the daily IT hardware report"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        subject_prefix = self.config.get('email_settings', {}).get('subject_prefix', '[IT 日報]')
        subject = f"{subject_prefix} IT硬體每日報告 - {date_str}"

        # Read HTML report
        with open(html_report_path, 'r', encoding='utf-8') as f:
            html_body = f.read()

        # Attachments
        attachments = [html_report_path]
        if json_data_path and os.path.exists(json_data_path):
            attachments.append(json_data_path)

        # Recipients
        recipients = self.recipients.get('primary', [])

        return self.send(
            subject=subject,
            html_body=html_body,
            to_email=recipients,
            attachments=attachments
        )


def send_test():
    """Test email functionality"""
    sender = EmailSender()
    print("[Email] Testing configuration...")

    if not sender.validate_config():
        print("[Email] ❌ Config validation failed")
        return False

    # Simple test
    result = sender.send(
        subject="[IT 日報] Test Email - " + datetime.now().strftime('%Y-%m-%d'),
        html_body="<h1>IT Hardware Daily Report Test</h1><p>This is a test email from the IT Daily Report system.</p>",
        text_body="IT Hardware Daily Report Test - This is a test email."
    )

    print(f"[Email] Result: {result}")
    return result.get('success', False)


if __name__ == '__main__':
    send_test()
