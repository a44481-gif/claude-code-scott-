"""
Email 寄送模組
使用 SMTP（163.com）發送分析報告
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, date
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailSender:
    """Email 發送器"""

    def __init__(self, config: dict):
        email_cfg = config.get("email", {})
        self.smtp_server = email_cfg.get("smtp_server", "smtp.163.com")
        self.smtp_port = email_cfg.get("smtp_port", 465)
        self.sender = email_cfg.get("sender", "")
        self.password = email_cfg.get("password", "")
        self.recipient = email_cfg.get("recipient", "")
        # 支援逗號分隔的多個收件人
        self.recipients = [r.strip() for r in self.recipient.split(",")]

    def send_report(
        self,
        analysis_text: str,
        raw_data: list | None = None,
        report_date: str | None = None,
    ) -> bool:
        """
        發送分析報告 Email

        Args:
            analysis_text: AI 分析報告正文
            raw_data: 原始數據（可選，會另存附件）
            report_date: 報告日期字串

        Returns:
            bool: 是否發送成功
        """
        if not self.sender or not self.password or not self.recipient:
            logger.error("Email 設定不完整，無法發送")
            return False

        date_str = report_date or date.today().isoformat()

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"【每日PSU市場報告】{date_str}"
        msg["From"] = self.sender
        msg["To"] = self.recipient

        # HTML 格式郵件
        html_body = self._build_html(analysis_text, date_str)
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # 附加原始數據 JSON 檔
        if raw_data:
            self._attach_raw_data(msg, raw_data, date_str)

        # 純文字版本（備用）
        text_part = MIMEText(analysis_text, "plain", "utf-8")
        msg.attach(text_part)

        try:
            # 163.com 使用 SSL
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender, self.password)
                server.sendmail(self.sender, self.recipients, msg.as_string())
            logger.info(f"✅ 報告已成功發送至 {self.recipient}")
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP 認證失敗：請確認 Email 密碼/授權碼是否正確")
            logger.error("提示：163.com 需要使用「授權碼」而非登入密碼")
            return False
        except Exception as e:
            logger.error(f"Email 發送失敗: {e}")
            return False

    def _build_html(self, analysis_text: str, date_str: str) -> str:
        """將分析文字轉為 HTML 格式"""

        # 簡單處理：將 markdown 標題轉為 HTML
        html = analysis_text
        html = html.replace("## ", "<h2>").replace("\n## ", "</h2>\n<h2>")
        html = html.replace("**", "<strong>")
        html = html.replace("**", "</strong>")
        html = html.replace("\n", "<br>\n")

        return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PSU 每日市場報告 {date_str}</title>
<style>
  body {{ font-family: 'Microsoft JhengHei', Arial, sans-serif;
          max-width: 800px; margin: 0 auto; padding: 20px;
          background: #f5f6fa; color: #2c3e50; }}
  .header {{ background: linear-gradient(135deg, #1a73e8, #0d47a1);
             color: white; padding: 24px; border-radius: 12px;
             margin-bottom: 24px; text-align: center; }}
  .header h1 {{ margin: 0; font-size: 22px; }}
  .header p {{ margin: 8px 0 0; opacity: 0.85; font-size: 13px; }}
  .content {{ background: white; padding: 24px; border-radius: 12px;
              box-shadow: 0 2px 8px rgba(0,0,0,0.08); line-height: 1.8; }}
  h2 {{ color: #1a73e8; border-bottom: 2px solid #e8eaed;
        padding-bottom: 8px; margin-top: 24px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
  th {{ background: #e8f0fe; text-align: left; padding: 10px 12px;
       font-size: 13px; color: #1a73e8; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #e8eaed; font-size: 13px; }}
  tr:hover {{ background: #f8f9fa; }}
  .footer {{ text-align: center; margin-top: 20px; font-size: 12px;
              color: #888; }}
  .warn {{ background: #fff3cd; padding: 12px; border-radius: 8px;
           color: #856404; margin-bottom: 16px; font-size: 13px; }}
</style>
</head>
<body>
<div class="header">
  <h1>⚡ PSU 電源供應器 — 每日市場報告</h1>
  <p>{date_str} · 京東 / 天貓 / Amazon</p>
</div>
<div class="content">
  {html}
</div>
<div class="footer">
  由 Claude Code 自動化系統生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')}
</div>
</body>
</html>"""

    def _attach_raw_data(self, msg: MIMEMultipart, raw_data: list, date_str: str):
        """附加原始數據 JSON 檔"""
        import json
        payload = MIMEBase("application", "octet-stream")
        json_str = json.dumps(raw_data, ensure_ascii=False, indent=2)
        encoders.encode_base64(payload)
        filename = f"PSU_raw_data_{date_str}.json"
        payload.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(payload)
