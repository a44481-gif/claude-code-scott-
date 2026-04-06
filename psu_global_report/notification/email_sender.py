"""
全球 PSU 報告 Email 發送器
"""

import smtplib
import logging
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, date
from pathlib import Path

logger = logging.getLogger(__name__)


class GlobalEmailSender:
    """全球報告 Email 發送器"""

    def __init__(self, config: dict):
        email_cfg = config.get("email", {})
        self.smtp_server = email_cfg.get("smtp_server", "smtp.163.com")
        self.smtp_port = email_cfg.get("smtp_port", 465)
        self.sender = email_cfg.get("sender", "")
        self.password = email_cfg.get("password", "")
        self.recipient = email_cfg.get("recipient", "h13751019800@163.com")
        self.recipients = [r.strip() for r in self.recipient.split(",")]

    def send_report(
        self,
        analysis_text: str,
        raw_data: list | None = None,
        ppt_path: str | None = None,
        report_date: str | None = None,
    ) -> bool:
        """發送完整報告 Email"""
        if not self.sender or not self.password:
            logger.error("Email 設定不完整，無法發送")
            return False

        date_str = report_date or date.today().isoformat()
        msg = MIMEMultipart("mixed")
        msg["Subject"] = f"全球電商平台電源銷售數據每日分析報告 - {date_str}"
        msg["From"] = self.sender
        msg["To"] = ", ".join(self.recipients)

        # HTML 正文
        html_body = self._build_html(analysis_text, date_str, len(raw_data) if raw_data else 0)
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # 純文字版本
        text_part = MIMEText(analysis_text, "plain", "utf-8")
        msg.attach(text_part)

        # 附加 PPT
        if ppt_path and Path(ppt_path).exists():
            self._attach_file(msg, ppt_path, "application/vnd.openxmlformats-officedocument.presentationml.presentation")
            logger.info(f"已附加 PPT: {ppt_path}")

        # 附加 JSON 原始數據
        if raw_data:
            self._attach_json(msg, raw_data, date_str)

        try:
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

    def _build_html(self, analysis_text: str, date_str: str, product_count: int) -> str:
        """構建精美 HTML 郵件"""

        # 簡單轉換 markdown → HTML
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
<title>全球 PSU 市場每日報告 {date_str}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Microsoft JhengHei', 'PingFang TC', Arial, sans-serif;
          background: #f0f2f5; color: #1f2937; }}
  .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
  .header {{
    background: linear-gradient(135deg, #1a73e8, #0d47a1);
    color: white; padding: 32px 24px; border-radius: 16px;
    margin-bottom: 24px; text-align: center;
  }}
  .header h1 {{ font-size: 26px; margin-bottom: 8px; }}
  .header .subtitle {{ opacity: 0.9; font-size: 14px; }}
  .stats-row {{
    display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap;
  }}
  .stat-card {{
    flex: 1; min-width: 140px; background: white; border-radius: 12px;
    padding: 16px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .stat-card .icon {{ font-size: 28px; }}
  .stat-card .value {{ font-size: 24px; font-weight: bold; color: #1a73e8; margin: 4px 0; }}
  .stat-card .label {{ font-size: 12px; color: #6b7280; }}
  .content {{
    background: white; padding: 28px; border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 20px;
    line-height: 1.8; font-size: 14px;
  }}
  .content h2 {{
    color: #1a73e8; font-size: 18px; border-bottom: 2px solid #e8eaf6;
    padding-bottom: 8px; margin: 20px 0 12px;
  }}
  .footer {{
    text-align: center; padding: 16px; font-size: 12px; color: #9ca3af;
  }}
  .warn {{
    background: #fff3cd; border: 1px solid #ffc107;
    padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;
    font-size: 13px; color: #856404;
  }}
  .highlight {{
    background: linear-gradient(120deg, #e8f0fe 0%, #e8f0fe 100%);
    padding: 2px 6px; border-radius: 4px;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🌍 全球電商平台 PSU 市場每日報告</h1>
    <p class="subtitle">{date_str} · 覆蓋 35+ 全球電商平台 · 每日 09:00 自動生成</p>
  </div>

  <div class="stats-row">
    <div class="stat-card">
      <div class="icon">📦</div>
      <div class="value">{product_count}</div>
      <div class="label">收集商品數</div>
    </div>
    <div class="stat-card">
      <div class="icon">🌐</div>
      <div class="value">35+</div>
      <div class="label">電商平台</div>
    </div>
    <div class="stat-card">
      <div class="icon">🏷️</div>
      <div class="value">10</div>
      <div class="label">目標品牌</div>
    </div>
    <div class="stat-card">
      <div class="icon">🤖</div>
      <div class="value">AI</div>
      <div class="label">智能分析</div>
    </div>
  </div>

  <div class="content">
    <div class="warn">
      ⚠️ 本報告由 Claude Code AI 自動化系統生成。PPT 附件請查看完整報告。
    </div>
    {html}
  </div>

  <div class="footer">
    由 Claude Code 全球 PSU 自動化系統生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')}<br>
    數據來源：Amazon / 京東 / 天貓 / PChome / Momo / Newegg / Best Buy / Mercado Libre / Noon 等<br>
    如有問題，請聯繫系統管理員
  </div>
</div>
</body>
</html>"""

    def _attach_file(self, msg, file_path: str, mime_type: str | None = None):
        """附加二進制文件（PPT/PDF 等）"""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            if content is None:
                logger.warning(f"檔案讀取為空: {file_path}")
                return
            payload = MIMEBase("application", "octet-stream")
            payload.set_payload(content)
            encoders.encode_base64(payload)
            filename = Path(file_path).name
            payload.add_header(
                "Content-Disposition",
                "attachment",
                filename=filename
            )
            msg.attach(payload)
        except FileNotFoundError:
            logger.warning(f"附件檔案不存在: {file_path}")
        except Exception as e:
            logger.warning(f"附加檔案失敗: {file_path} — {e}")

    def _attach_json(self, msg, raw_data: list, date_str: str):
        """附加 JSON 原始數據"""
        try:
            json_bytes = json.dumps(raw_data, ensure_ascii=False, indent=2).encode("utf-8")
            payload = MIMEBase("application", "octet-stream")
            payload.set_payload(json_bytes)
            encoders.encode_base64(payload)
            filename = f"PSU_raw_data_{date_str}.json"
            payload.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(payload)
        except Exception as e:
            logger.warning(f"附加 JSON 失敗: {e}")
