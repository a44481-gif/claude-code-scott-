# -*- coding: utf-8 -*-
"""
CoBM 曜越T.T分析报告发送脚本
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# 邮箱配置
SMTP_SERVER = 'smtp.163.com'
SMTP_PORT = 465
SENDER_EMAIL = 'h13751019800@163.com'
SENDER_AUTH_CODE = 'JWxaQXzrCQCWtPu3'
RECIPIENT_EMAIL = 'h13751019800@163.com'

REPORT_PATH = r'D:/claude mini max 2.7/.claude/CoBM_曜越T.T分析报告_20260406.pptx'

def generate_html_body():
    """生成邮件 HTML 正文"""
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #333;">
    <div style="background: linear-gradient(135deg, #1a5276, #2e86c1); color: white; padding: 25px; border-radius: 10px 10px 0 0;">
      <h1 style="margin: 0; font-size: 24px;">CoBM产品IC方案优势分析报告</h1>
      <p style="margin: 5px 0 0; opacity: 0.9;">曜越T.T电竞电源市场切入策略 · 竞品分析 · 销售增长预测 | 2026-04-06</p>
    </div>
    <div style="background: #f9f9f9; padding: 25px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">

    <h2 style="color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 8px;">报告目录</h2>
    <ol>
      <li><strong>CoBM产品IC方案优势分析</strong> - 技术原理与核心优势</li>
      <li><strong>曜越T.T电竞电源产品线调研</strong> - GF系列/XP系列/RGB系列</li>
      <li><strong>CoBM方案切入策略</strong> - 优先级排序与最佳切入型号</li>
      <li><strong>竞品分析</strong> - 华硕ROG/微星/酷冷/安钛克/海韵</li>
      <li><strong>竞争优势对比</strong> - 量化分析</li>
      <li><strong>销售增长预测</strong> - 不同瓦数段增长预期</li>
      <li><strong>策略建议</strong> - 产品/定价/渠道/推广</li>
    </ol>

    <h2 style="color: #1a5276;">一、CoBM技术核心优势</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #1a5276; color: white;">
      <th style="padding: 10px;">维度</th>
      <th style="padding: 10px;">提升表现</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>功率密度</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;">+50%~65%</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>能效</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;">+2%~4% (金牌→白金牌)</td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>BOM成本</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;">-18%~28%</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>纹波抑制</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;">-50%~60%</td>
    </tr>
    </table>

    <h2 style="color: #1a5276;">二、曜越T.T产品线</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #27ae60; color: white;">
      <th style="padding: 10px;">系列</th>
      <th style="padding: 10px;">瓦数覆盖</th>
      <th style="padding: 10px;">80+认证</th>
      <th style="padding: 10px;">参考价(USD)</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">GF3 (旗舰)</td>
      <td style="padding: 8px; border: 1px solid #ddd;">650W-1650W</td>
      <td style="padding: 8px; border: 1px solid #ddd;">Gold</td>
      <td style="padding: 8px; border: 1px solid #ddd;">$110-$440</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">GF2 (高端)</td>
      <td style="padding: 8px; border: 1px solid #ddd;">650W-1200W</td>
      <td style="padding: 8px; border: 1px solid #ddd;">Gold</td>
      <td style="padding: 8px; border: 1px solid #ddd;">$95-$240</td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">XP (白金旗舰)</td>
      <td style="padding: 8px; border: 1px solid #ddd;">850W-1200W</td>
      <td style="padding: 8px; border: 1px solid #ddd;">Platinum</td>
      <td style="padding: 8px; border: 1px solid #ddd;">$170-$310</td>
    </tr>
    </table>

    <h2 style="color: #e74c3c;">三、CoBM切入优先级</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #e74c3c; color: white;">
      <th style="padding: 10px;">优先级</th>
      <th style="padding: 10px;">产品线</th>
      <th style="padding: 10px;">瓦数段</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd; color: red;"><strong>P1</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">Smart BX1</td>
      <td style="padding: 8px; border: 1px solid #ddd;">430-600W</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd; color: red;"><strong>P1</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">GF1系列</td>
      <td style="padding: 8px; border: 1px solid #ddd;">650-1200W</td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd; color: orange;"><strong>P2</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">Smart BX3 Pro SE</td>
      <td style="padding: 8px; border: 1px solid #ddd;">650-850W</td>
    </tr>
    </table>

    <h2 style="color: #1a5276;">四、销售增长预测</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #8e44ad; color: white;">
      <th style="padding: 10px;">瓦数段</th>
      <th style="padding: 10px;">预计销量增长</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">550W-650W</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>+35%~50%</strong></td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">750W-850W</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>+28%~42%</strong></td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">1000W-1200W</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>+20%~30%</strong></td>
    </tr>
    </table>

    <hr style="margin: 25px 0; border: none; border-top: 1px solid #ddd;">
    <p style="font-size: 13px; color: #666;"><strong>完整报告附件：</strong><code>CoBM_曜越T.T分析报告_20260406.pptx</code>（14页PPT）</p>
    <p style="font-size: 12px; color: #999;">本报告基于曜越T.T产品调研及行业公开数据 | 分析师：Claude Code AI | 2026-04-06</p>
    </div>
    </body>
    </html>
    """
    return html

def send_email():
    """发送邮件"""
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'CoBM曜越T.T分析报告 2026-04-06'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    # HTML 正文
    html_part = MIMEText(generate_html_body(), 'html', 'utf-8')
    msg.attach(html_part)

    # 附件
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, 'rb') as f:
            report_content = f.read()

        part = MIMEApplication(report_content, Name='CoBM_曜越T.T分析报告_20260406.pptx')
        part['Content-Disposition'] = 'attachment; filename="CoBM_曜越T.T分析报告_20260406.pptx"'
        msg.attach(part)
        print("已附加PPT文件: " + REPORT_PATH)
    else:
        print("PPT文件不存在: " + REPORT_PATH)
        return False

    try:
        print("连接到 " + SMTP_SERVER + ":" + str(SMTP_PORT) + "...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        print("登录邮箱...")
        server.login(SENDER_EMAIL, SENDER_AUTH_CODE)
        print("发送邮件至 " + RECIPIENT_EMAIL + "...")
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("邮件发送成功！")
        return True
    except Exception as e:
        print("邮件发送失败: " + str(e))
        return False

def main():
    print("=" * 60)
    print("CoBM 曜越T.T分析报告 - 邮件发送")
    print("=" * 60)
    send_email()

if __name__ == '__main__':
    main()
