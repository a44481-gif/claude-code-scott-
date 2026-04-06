"""
飞书邮件发送器
"""
import json
import httpx
from typing import List, Optional
from datetime import datetime
from loguru import logger


class LarkMailSender:
    """飞书邮件发送"""

    def __init__(self, config: dict):
        self.config = config
        self.lark_config = config.get("lark_mail", {})
        self.enabled = self.lark_config.get("enabled", False)

    async def send_email(self, to_email: str, subject: str, body: str,
                        attachments: Optional[List[str]] = None) -> bool:
        """通过飞书邮件API发送"""
        if not self.enabled:
            logger.info("[飞书邮件] 未启用，使用模拟发送")
            return self._mock_send(to_email, subject, body, attachments)

        try:
            # 飞书邮件API
            # 注意: 需要配置飞书应用权限
            api_url = "https://open.feishu.cn/open-apis/mail/v1/messages"

            payload = {
                "email": to_email,
                "subject": subject,
                "content": body,
                "content_type": "html",
            }

            # 实际调用需要access_token
            # 这里先实现框架，后续配置飞书应用后完善
            logger.info(f"[飞书邮件] API调用: {to_email} - {subject}")
            return True

        except Exception as e:
            logger.error(f"[飞书邮件] 发送失败: {e}")
            return False

    def _mock_send(self, to_email: str, subject: str, body: str,
                  attachments: List = None) -> bool:
        """模拟发送"""
        logger.info(f"[飞书邮件-模拟] 收件人: {to_email}")
        logger.info(f"[飞书邮件-模拟] 主题: {subject}")
        return True

    async def send_report(self, to_email: str, report_file: str,
                         date_str: str = None) -> bool:
        """发送报告"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        subject = f"健康食品销售分析报告 - {date_str}"
        body = f"""
        <html>
        <body>
            <h1>健康食品 AI 扩客代理人</h1>
            <p>自动销售分析报告 - {date_str}</p>
            <p>附件包含完整的分析报告，请查收。</p>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, body, attachments=[report_file])
