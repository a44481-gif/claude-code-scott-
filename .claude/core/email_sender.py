"""
Email Sender - SMTP with Jinja2 HTML templates.
Merged from msi_psu_automation EmailSender + health_food_agent SMTP patterns.
"""
import smtplib
import json
import os
from datetime import datetime
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class EmailAttachment:
    """邮件附件"""
    filename: str
    content: bytes
    content_type: str
    is_inline: bool = False


class EmailSender:
    """邮件发送器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.attachments: List[EmailAttachment] = []

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """从 JSON 文件加载配置"""
        if not os.path.exists(config_path):
            logger.warning(f"邮件配置文件不存在: {config_path}，使用默认配置")
            return self._default_config()

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        logger.info(f"已加载邮件配置: {config_path}")
        return cfg

    def _default_config(self) -> Dict[str, Any]:
        return {
            "smtp_server": "smtp.qq.com",
            "smtp_port": 587,
            "use_tls": True,
            "email_sender": "your_email@qq.com",
            "email_password": "your_app_password",
            "recipients": [],
            "cc_recipients": [],
            "default_subject": "AI Agent 报告",
        }

    # ── Send Email ───────────────────────────────────────────────

    def send(
        self,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        recipients: Optional[List[str]] = None,
        cc_recipients: Optional[List[str]] = None,
        attachments: Optional[List[EmailAttachment]] = None,
    ) -> bool:
        """发送邮件"""
        cfg = self.config
        recipients = recipients or cfg.get("recipients", [])
        if not recipients:
            logger.error("没有收件人配置")
            return False

        msg = MIMEMultipart("mixed")
        msg["From"] = cfg.get("email_sender", "")
        msg["To"] = ", ".join(recipients)
        if cc_recipients or cfg.get("cc_recipients"):
            cc = cc_recipients or cfg.get("cc_recipients", [])
            msg["Cc"] = ", ".join(cc)

        msg["Subject"] = subject
        msg.attach(MIMEText(text_content or "", "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        # Add attachments
        all_attachments = attachments or self.attachments
        for att in all_attachments:
            part = MIMEBase(*att.content_type.split("/"))
            part.set_payload(att.content)
            encoders.encode_base64(part)
            disposition = "inline" if att.is_inline else f"attachment; filename=\"{att.filename}\""
            part.add_header("Content-Disposition", disposition)
            msg.attach(part)

        try:
            with smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"]) as server:
                if cfg.get("use_tls", True):
                    server.starttls()
                server.login(cfg["email_sender"], cfg["email_password"])
                all_recipients = recipients + (cc_recipients or []) + cfg.get("bcc_recipients", [])
                server.sendmail(cfg["email_sender"], all_recipients, msg.as_string())
            logger.info(f"邮件已发送至 {len(recipients)} 个收件人: {subject}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP 认证失败: {e}")
            return False
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP 认证失败: {e}")
            return False
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False

    # ── HTML Report Builder ───────────────────────────────────────

    def build_html_report(
        self,
        title: str,
        summary: str,
        sections: List[Dict[str, Any]],
        footer: str = "",
    ) -> str:
        """构建 HTML 报告"""
        sections_html = ""
        for section in sections:
            sections_html += f"""
            <div class="section">
                <h2>{section.get('title', '')}</h2>
                {section.get('content', '')}
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', 'PingFang TC', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; }}
        .header h1 {{ margin: 0 0 10px; font-size: 24px; }}
        .header .date {{ opacity: 0.9; font-size: 14px; }}
        .summary {{ background: #f8f9fa; padding: 20px 30px; border-bottom: 1px solid #eee; }}
        .section {{ padding: 25px 30px; border-bottom: 1px solid #eee; }}
        .section:last-child {{ border-bottom: none; }}
        .section h2 {{ color: #667eea; margin: 0 0 15px; font-size: 18px; border-left: 4px solid #667eea; padding-left: 12px; }}
        .item {{ padding: 12px; margin: 8px 0; background: #f8f9fa; border-radius: 6px; border-left: 3px solid #764ba2; }}
        .item strong {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background: #667eea; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px 10px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f5f5f5; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 5px; }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        .footer {{ padding: 20px 30px; color: #888; font-size: 12px; border-top: 1px solid #eee; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="date">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        <div class="summary">
            <strong>执行摘要:</strong> {summary}
        </div>
        {sections_html}
        <div class="footer">
            <p>此邮件由 AI Business Intelligence Platform 自动生成</p>
            {footer}
        </div>
    </div>
</body>
</html>"""

    # ── Simple Alert ─────────────────────────────────────────────

    def build_alert_email(self, title: str, message: str, level: str = "info") -> str:
        """构建告警邮件"""
        colors = {
            "success": "#28a745",
            "warning": "#ffc107",
            "danger": "#dc3545",
            "info": "#17a2b8",
        }
        color = colors.get(level, "#17a2b8")

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .alert {{ border-left: 6px solid {color}; padding: 15px 20px; background: #f8f9fa; border-radius: 4px; }}
        h2 {{ margin: 0 0 10px; color: #333; }}
        p {{ margin: 0; color: #555; }}
    </style>
</head>
<body>
    <div class="alert">
        <h2>{title}</h2>
        <p>{message}</p>
        <p style="margin-top:15px; font-size:12px; color:#888;">时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>"""
