"""
郵件發送服務 - 自動發送MSI電源銷售分析報告
支持HTML格式、附件發送和模板化內容
"""

import logging
import smtplib
import json
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd
import jinja2

logger = logging.getLogger(__name__)


@dataclass
class EmailAttachment:
    """郵件附件數據結構"""
    filename: str
    content: bytes
    content_type: str
    is_inline: bool = False


class EmailSender:
    """郵件發送器"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.template_env = self._setup_templates()
        self.attachments = []
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """加載郵件配置"""
        default_config = {
            'smtp_server': 'smtp.qq.com',
            'smtp_port': 587,
            'use_tls': True,
            'email_sender': 'your_email@qq.com',
            'email_password': 'your_app_password',
            'recipients': ['2231686072@qq.com'],
            'cc_recipients': [],
            'bcc_recipients': [],
            'default_subject': 'MSI電源銷售分析報告',
            'templates': {
                'daily_report': 'templates/daily_report.html',
                'error_alert': 'templates/error_alert.html'
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    logger.info(f"從 {config_path} 加載郵件配置")
            except Exception as e:
                logger.error(f"加載郵件配置失敗: {e}")
        
        return default_config
    
    def _setup_templates(self) -> jinja2.Environment:
        """設置Jinja2模板環境"""
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        
        if not os.path.exists(template_path):
            os.makedirs(template_path, exist_ok=True)
            
            # 創建默認模板
            self._create_default_templates(template_path)
        
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def _create_default_templates(self, template_path: str):
        """創建默認HTML模板"""
        # 每日報告模板
        daily_report_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MSI電源銷售每日報告</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background-color: #0078d7; color: white; padding: 20px; border-radius: 5px; }
        .header h1 { margin: 0; }
        .summary { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .section { margin: 30px 0; }
        .section-title { color: #0078d7; border-bottom: 2px solid #0078d7; padding-bottom: 10px; }
        .metric-card { 
            background: white; 
            border: 1px solid #dee2e6; 
            border-radius: 5px; 
            padding: 15px; 
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value { 
            font-size: 24px; 
            font-weight: bold; 
            color: #0078d7; 
        }
        .metric-label { 
            color: #6c757d; 
            font-size: 14px; 
        }
        .insight-item { 
            padding: 10px; 
            margin: 5px 0; 
            background-color: #e8f4fd; 
            border-left: 4px solid #0078d7;
        }
        .recommendation-item { 
            padding: 10px; 
            margin: 5px 0; 
            background-color: #d4edda; 
            border-left: 4px solid #28a745;
        }
        .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
        .table th { background-color: #f8f9fa; font-weight: bold; }
        .table tr:hover { background-color: #f5f5f5; }
        .footer { 
            margin-top: 40px; 
            padding-top: 20px; 
            border-top: 1px solid #dee2e6; 
            color: #6c757d; 
            font-size: 12px; 
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            font-size: 12px;
            font-weight: bold;
            border-radius: 12px;
            margin-right: 5px;
        }
        .badge-success { background-color: #28a745; color: white; }
        .badge-warning { background-color: #ffc107; color: #212529; }
        .badge-danger { background-color: #dc3545; color: white; }
        .badge-info { background-color: #17a2b8; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MSI電源銷售每日報告</h1>
            <p>{{ report_date }} | 系統版本: v1.0.0</p>
        </div>
        
        <div class="summary">
            <h2>執行摘要</h2>
            <p>{{ executive_summary }}</p>
            <div style="margin-top: 15px;">
                <span class="badge badge-{{ 'success' if overall_confidence > 0.8 else 'warning' if overall_confidence > 0.6 else 'danger' }}">
                    分析置信度: {{ "%.0f"|format(overall_confidence * 100) }}%
                </span>
                <span class="badge badge-info">
                    數據點數: {{ data_points }}
                </span>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📊 關鍵指標</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                {% for metric in critical_metrics %}
                <div class="metric-card">
                    <div class="metric-value">{{ metric.value }}</div>
                    <div class="metric-label">{{ metric.label }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🔍 主要發現</h2>
            {% for insight in key_findings %}
            <div class="insight-item">
                <strong>•</strong> {{ insight }}
            </div>
            {% endfor %}
        </div>
        
        <div class="section">
            <h2 class="section-title">📈 銷售數據概覽</h2>
            {% if top_products %}
            <table class="table">
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>產品型號</th>
                        <th>銷售數量</th>
                        <th>平均價格</th>
                        <th>評分</th>
                    </tr>
                </thead>
                <tbody>
                    {% for product in top_products %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ product.model }}</td>
                        <td>{{ product.sales }}</td>
                        <td>${{ "%.2f"|format(product.price) }}</td>
                        <td>{{ "%.1f"|format(product.rating) if product.rating else 'N/A' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>暫無產品銷售數據</p>
            {% endif %}
        </div>
        
        <div class="section">
            <h2 class="section-title">💡 推薦行動</h2>
            {% for recommendation in recommended_actions %}
            <div class="recommendation-item">
                <strong>▶</strong> {{ recommendation }}
            </div>
            {% endfor %}
        </div>
        
        <div class="section">
            <h2 class="section-title">📋 附件列表</h2>
            <ul>
                {% for attachment in attachments %}
                <li>{{ attachment.filename }} - {{ attachment.description }}</li>
                {% endfor %}
            </ul>
        </div>
        
        <div class="footer">
            <p>本報告由MSI電源銷售數據自動化系統生成</p>
            <p>生成時間: {{ generated_at }}</p>
            <p>如有任何問題或建議，請聯繫系統管理員</p>
            <p><small>此為自動發送的郵件，請勿直接回復</small></p>
        </div>
    </div>
</body>
</html>"""
        
        daily_report_path = os.path.join(template_path, 'daily_report.html')
        with open(daily_report_path, 'w', encoding='utf-8') as f:
            f.write(daily_report_template)
        
        # 錯誤警報模板
        error_alert_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>系統錯誤警報</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .alert { background-color: #dc3545; color: white; padding: 20px; border-radius: 5px; }
        .alert h1 { margin: 0; }
        .content { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .error-details { background-color: white; padding: 15px; border-radius: 5px; border: 1px solid #dee2e6; }
        .footer { margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="alert">
            <h1>🚨 MSI數據收集系統錯誤</h1>
            <p>{{ error_time }}</p>
        </div>
        
        <div class="content">
            <h2>錯誤詳情</h2>
            <div class="error-details">
                <p><strong>錯誤類型:</strong> {{ error_type }}</p>
                <p><strong>錯誤訊息:</strong> {{ error_message }}</p>
                <p><strong>錯誤位置:</strong> {{ error_location }}</p>
                <p><strong>系統狀態:</strong> {{ system_status }}</p>
            </div>
            
            <h2>建議操作</h2>
            <ul>
                <li>檢查系統日誌獲取詳細信息</li>
                <li>驗證數據源連接是否正常</li>
                <li>檢查系統資源使用情況</li>
                <li>如有需要，聯繫技術支持</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>此為自動發送的錯誤警報郵件</p>
            <p>生成時間: {{ generated_at }}</p>
        </div>
    </div>
</body>
</html>"""
        
        error_alert_path = os.path.join(template_path, 'error_alert.html')
        with open(error_alert_path, 'w', encoding='utf-8') as f:
            f.write(error_alert_template)
    
    def send_daily_report(self, report_data: Dict[str, Any], 
                         attachments: List[EmailAttachment] = None) -> bool:
        """發送每日報告郵件"""
        try:
            # 準備郵件內容
            subject = f"MSI電源銷售每日報告 - {datetime.now().strftime('%Y-%m-%d')}"
            
            # 渲染HTML模板
            html_content = self._render_daily_report_template(report_data)
            
            # 準備附件
            if attachments:
                self.attachments = attachments
            
            # 發送郵件
            success = self._send_email(
                subject=subject,
                html_content=html_content,
                text_content=self._html_to_text(html_content),
                attachments=self.attachments
            )
            
            if success:
                logger.info(f"成功發送每日報告郵件到 {len(self.config['recipients'])} 個收件人")
            else:
                logger.error("發送每日報告郵件失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"發送每日報告時發生錯誤: {e}")
            return False
    
    def send_error_alert(self, error_info: Dict[str, Any]) -> bool:
        """發送錯誤警報郵件"""
        try:
            subject = f"🚨 MSI數據收集系統錯誤 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # 渲染錯誤模板
            html_content = self._render_error_alert_template(error_info)
            
            success = self._send_email(
                subject=subject,
                html_content=html_content,
                text_content=self._html_to_text(html_content),
                is_alert=True
            )
            
            if success:
                logger.info(f"成功發送錯誤警報到 {len(self.config['recipients'])} 個收件人")
            else:
                logger.error("發送錯誤警報失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"發送錯誤警報時發生錯誤: {e}")
            return False
    
    def _render_daily_report_template(self, report_data: Dict[str, Any]) -> str:
        """渲染每日報告HTML模板"""
        try:
            template = self.template_env.get_template('daily_report.html')
            
            # 準備模板數據
            template_data = {
                'report_date': datetime.now().strftime('%Y年%m月%d日'),
                'executive_summary': report_data.get('executive_summary', ''),
                'overall_confidence': report_data.get('overall_confidence', 0.0),
                'data_points': report_data.get('data_points', 0),
                'key_findings': report_data.get('key_findings', []),
                'critical_metrics': self._format_metrics(report_data.get('critical_metrics', {})),
                'recommended_actions': report_data.get('recommended_actions', []),
                'top_products': report_data.get('top_products', []),
                'attachments': report_data.get('attachments', []),
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return template.render(**template_data)
            
        except Exception as e:
            logger.error(f"渲染每日報告模板失敗: {e}")
            return self._create_fallback_html(report_data)
    
    def _render_error_alert_template(self, error_info: Dict[str, Any]) -> str:
        """渲染錯誤警報HTML模板"""
        try:
            template = self.template_env.get_template('error_alert.html')
            
            template_data = {
                'error_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error_type': error_info.get('error_type', 'Unknown'),
                'error_message': error_info.get('error_message', 'No error message'),
                'error_location': error_info.get('error_location', 'Unknown'),
                'system_status': error_info.get('system_status', 'Error'),
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return template.render(**template_data)
            
        except Exception as e:
            logger.error(f"渲染錯誤警報模板失敗: {e}")
            return f"系統錯誤: {error_info.get('error_message', 'Unknown error')}"
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化指標數據用於模板"""
        formatted_metrics = []
        
        metric_labels = {
            'sales_growth_rate': '銷售增長率',
            'revenue_growth_rate': '收入增長率',
            'avg_price_per_watt': '每瓦平均價格',
            'avg_rating': '平均評分',
            'in_stock_rate': '庫存率',
            'top_product_sales': '暢銷產品銷量'
        }
        
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                label = metric_labels.get(key, key)
                
                # 格式化值
                if 'rate' in key or 'growth' in key:
                    formatted_value = f"{value*100:.1f}%"
                elif 'price' in key:
                    formatted_value = f"${value:.2f}"
                elif 'rating' in key:
                    formatted_value = f"{value:.1f}/5"
                else:
                    formatted_value = str(value)
                
                formatted_metrics.append({
                    'label': label,
                    'value': formatted_value
                })
        
        return formatted_metrics[:6]  # 只顯示前6個指標
    
    def _send_email(self, subject: str, html_content: str, text_content: str, 
                   attachments: List[EmailAttachment] = None, is_alert: bool = False) -> bool:
        """發送郵件核心方法"""
        try:
            # 創建郵件
            msg = MIMEMultipart('mixed' if attachments else 'alternative')
            msg['From'] = self.config['email_sender']
            msg['To'] = ', '.join(self.config['recipients'])
            
            if self.config.get('cc_recipients'):
                msg['Cc'] = ', '.join(self.config['cc_recipients'])
            
            msg['Subject'] = subject
            
            # 添加文本內容
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            
            # 添加HTML內容
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 添加附件
            if attachments:
                for attachment in attachments:
                    part = MIMEBase(*attachment.content_type.split('/'))
                    part.set_payload(attachment.content)
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'inline' if attachment.is_inline else f'attachment; filename="{attachment.filename}"'
                    )
                    msg.attach(part)
            
            # 連接SMTP服務器並發送
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                if self.config.get('use_tls', True):
                    server.starttls()
                
                server.login(self.config['email_sender'], self.config['email_password'])
                
                # 構建收件人列表
                all_recipients = self.config['recipients'].copy()
                if self.config.get('cc_recipients'):
                    all_recipients.extend(self.config['cc_recipients'])
                if self.config.get('bcc_recipients'):
                    all_recipients.extend(self.config['bcc_recipients'])
                
                server.sendmail(
                    self.config['email_sender'],
                    all_recipients,
                    msg.as_string()
                )
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP認證失敗: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP發送失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"發送郵件時發生未知錯誤: {e}")
            return False
    
    def _html_to_text(self, html_content: str) -> str:
        """將HTML轉換為純文本"""
        try:
            # 簡單的HTML到文本轉換
            import re
            
            # 移除HTML標籤
            text = re.sub(r'<[^>]+>', ' ', html_content)
            
            # 移除多餘空格
            text = re.sub(r'\s+', ' ', text)
            
            # 移除特殊字符
            text = re.sub(r'[^\w\s.,!?-]', '', text)
            
            # 截斷到合理長度
            if len(text) > 1000:
                text = text[:1000] + '...'
            
            return text.strip()
            
        except Exception:
            # 如果轉換失敗，返回簡單文本
            return "這是MSI電源銷售每日報告。請查看HTML版本獲取完整內容。"
    
    def _create_fallback_html(self, report_data: Dict[str, Any]) -> str:
        """創建備用HTML內容"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>MSI電源銷售報告</title>
        </head>
        <body>
            <h1>MSI電源銷售每日報告</h1>
            <p>生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h2>執行摘要</h2>
            <p>{report_data.get('executive_summary', '')}</p>
            
            <h2>主要發現</h2>
            <ul>
        """
        
        for insight in report_data.get('key_findings', []):
            html += f"<li>{insight}</li>"
        
        html += """
            </ul>
            
            <h2>推薦行動</h2>
            <ol>
        """
        
        for action in report_data.get('recommended_actions', []):
            html += f"<li>{action}</li>"
        
        html += """
            </ol>
            
            <p>本報告由MSI電源銷售數據自動化系統生成</p>
        </body>
        </html>
        """
        
        return html
    
    def create_csv_attachment(self, data: pd.DataFrame, filename: str) -> EmailAttachment:
        """創建CSV附件"""
        try:
            csv_content = data.to_csv(index=False, encoding='utf-8-sig')
            return EmailAttachment(
                filename=filename,
                content=csv_content.encode('utf-8-sig'),
                content_type='text/csv',
                is_inline=False
            )
        except Exception as e:
            logger.error(f"創建CSV附件失敗: {e}")
            raise
    
    def create_pdf_attachment(self, content: str, filename: str) -> EmailAttachment:
        """創建PDF附件"""
        try:
            # 使用reportlab創建PDF
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from io import BytesIO
            
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            
            # 設置字體
            c.setFont("Helvetica", 12)
            
            # 添加標題
            c.drawString(50, 750, f"MSI電源銷售報告 - {datetime.now().strftime('%Y-%m-%d')}")
            
            # 添加內容
            y_position = 700
            lines = content.split('\n')
            
            for line in lines[:50]:  # 限制行數
                if y_position < 50:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_position = 750
                
                c.drawString(50, y_position, line[:100])  # 限制每行長度
                y_position -= 20
            
            c.save()
            
            return EmailAttachment(
                filename=filename,
                content=buffer.getvalue(),
                content_type='application/pdf',
                is_inline=False
            )
            
        except Exception as e:
            logger.error(f"創建PDF附件失敗: {e}")
            raise