"""
163.com SMTP 邮件发送器 - 复用psu_daily_report架构
"""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from loguru import logger


class SMTPSender:
    """163.com SMTP 邮件发送"""

    def __init__(self, config: dict):
        self.config = config
        self.smtp_config = config.get("smtp", {})
        self.host = self.smtp_config.get("host", "smtp.163.com")
        self.port = self.smtp_config.get("port", 465)
        self.use_ssl = self.smtp_config.get("use_ssl", True)
        self.username = self.smtp_config.get("username", "")
        self.password = self.smtp_config.get("password", "")
        self.from_name = self.smtp_config.get("from_name", "AI Agent")

    def send_email(self, to_email: str, subject: str, body: str,
                   attachments: Optional[List[str]] = None,
                   cc: Optional[List[str]] = None) -> bool:
        """发送邮件"""
        if not self.username or not self.password or self.password == "YOUR_163_SMTP_PASSWORD":
            logger.warning("SMTP未配置，使用模拟发送")
            return self._mock_send(to_email, subject, body, attachments)

        try:
            msg = MIMEMultipart()
            msg["From"] = f"{self.from_name} <{self.username}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            if cc:
                msg["Cc"] = ",".join(cc)

            # HTML正文
            msg.attach(MIMEText(body, "html", "utf-8"))

            # 附件
            if attachments:
                for file_path in attachments:
                    self._attach_file(msg, file_path)

            # 发送
            if self.use_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.host, self.port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg)

            logger.info(f"邮件发送成功: {to_email} - {subject}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False

    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """添加附件"""
        file_path = Path(file_path)
        if not file_path.exists():
            logger.warning(f"附件不存在: {file_path}")
            return

        with open(file_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = file_path.name
            part.add_header(
                "Content-Disposition",
                f"attachment; filename*=UTF-8''{filename}"
            )
            msg.attach(part)

    def _mock_send(self, to_email: str, subject: str, body: str, attachments: List = None) -> bool:
        """模拟发送（无配置时）"""
        logger.info(f"[模拟发送] 收件人: {to_email}")
        logger.info(f"[模拟发送] 主题: {subject}")
        logger.info(f"[模拟发送] 附件: {attachments or '无'}")

        # 保存邮件内容到文件
        output_dir = Path(__file__).parent.parent.parent.parent / "data"
        output_dir.mkdir(parents=True, exist_ok=True)
        email_file = output_dir / f"email_pending_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(email_file, "w", encoding="utf-8") as f:
            f.write(f"收件人: {to_email}\n")
            f.write(f"主题: {subject}\n")
            f.write(f"时间: {datetime.now()}\n")
            f.write(f"附件: {attachments}\n")
            f.write(f"\n内容预览:\n{body[:500]}...")

        logger.info(f"[模拟邮件] 已保存: {email_file}")
        return True

    def send_report(self, to_email: str, report_file: str,
                   date_str: str = None) -> bool:
        """发送报告邮件"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        subject = f"健康食品销售分析报告 - {date_str}"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.8; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px;">
                    <h1 style="margin: 0;">健康食品 AI 扩客代理人</h1>
                    <p style="margin: 10px 0 0; opacity: 0.9;">自动销售分析报告</p>
                </div>

                <div style="background: #f9f9f9; padding: 25px; border-radius: 12px; margin-bottom: 20px;">
                    <h2 style="color: #2E7D32; margin-top: 0;">报告周期</h2>
                    <p style="font-size: 16px;">{date_str}</p>
                </div>

                <div style="background: #E8F5E9; padding: 25px; border-radius: 12px; margin-bottom: 20px;">
                    <h2 style="color: #2E7D32; margin-top: 0;">报告内容</h2>
                    <ul style="padding-left: 20px;">
                        <li>台湾市场趋势分析</li>
                        <li>精选产品推荐</li>
                        <li>供应商评估报告</li>
                        <li>定价策略建议</li>
                        <li>渠道规划方案</li>
                        <li>销售执行计划</li>
                    </ul>
                </div>

                <div style="background: #FFF3E0; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                    <h3 style="color: #E65100; margin-top: 0;">注意事项</h3>
                    <p style="margin: 0; color: #666;">本报告由 AI 自动生成，数据仅供参考。实际运营请结合市场实际情况调整。</p>
                </div>

                <div style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">
                    <p>此邮件由 AI 扩客代理人自动发送</p>
                    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, body, attachments=[report_file])

    def batch_send(self, to_emails: List[str], subject: str, body: str,
                  attachments: Optional[List[str]] = None) -> dict:
        """批量发送"""
        results = {}
        for email in to_emails:
            results[email] = self.send_email(email, subject, body, attachments)
        return results
