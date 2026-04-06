# -*- coding: utf-8 -*-
"""
CoBM电源IC方案专业技术分析报告 PPT发送脚本
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# 邮箱配置
SMTP_SERVER = 'smtp.163.com'
SMTP_PORT = 465
SENDER_EMAIL = 'h13751019800@163.com'
SENDER_AUTH_CODE = 'FZQAXDZUHDWQHUIO'
RECIPIENT_EMAIL = 'h13751019800@163.com'

REPORT_PATH = r'D:/claude mini max 2.7/.claude/CoBM_IC方案专业技术分析报告_20260405.pptx'

def generate_html_body():
    """生成邮件 HTML 正文"""
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #333;">
    <div style="background: linear-gradient(135deg, #1a5276, #2e86c1); color: white; padding: 25px; border-radius: 10px 10px 0 0;">
      <h1 style="margin: 0; font-size: 24px;">CoBM 电源IC方案专业技术分析报告 - PPT</h1>
      <p style="margin: 5px 0 0; opacity: 0.9;">GaN · SiC · Si · 数字控制 · 封装技术 | 2026-04-05</p>
    </div>
    <div style="background: #f9f9f9; padding: 25px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">

    <h2 style="color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 8px;">报告概览</h2>
    <p>本报告已完成PPT版本，共14页，包含以下内容：</p>
    <ol>
      <li><strong>封面</strong> - 标题页</li>
      <li><strong>目录</strong> - 报告结构概览</li>
      <li><strong>半导体材料对比</strong> - Si/GaN/SiC</li>
      <li><strong>GaN厂商对比</strong> - Infineon/Navitas/Power Integrations</li>
      <li><strong>SiC厂商对比</strong> - Wolfspeed/Infineon/onsemi/ROHM</li>
      <li><strong>数字控制器对比</strong> - TI/Infineon/NXP/Microchip</li>
      <li><strong>PFC控制器对比</strong> - CCM/CRM/Totem-Pole</li>
      <li><strong>LLC控制器对比</strong> - 谐振控制器IC</li>
      <li><strong>CoBM封装对比</strong> - 封装技术选型</li>
      <li><strong>功率段选型</strong> - 按功率推荐IC方案</li>
      <li><strong>技术维度对比</strong> - CoBM vs 传统方案</li>
      <li><strong>供应商生态</strong> - 全链路供应商汇总</li>
      <li><strong>投资建议</strong> - Phase 1/2/3路线图</li>
      <li><strong>结论</strong> - 核心结论与建议</li>
    </ol>

    <h2 style="color: #1a5276;">PPT亮点</h2>
    <ul>
      <li>专业的蓝色主题设计</li>
      <li>清晰的数据表格对比</li>
      <li>直观的方案对比图</li>
      <li>完整的投资建议路线图</li>
    </ul>

    <hr style="margin: 25px 0; border: none; border-top: 1px solid #ddd;">
    <p style="font-size: 13px; color: #666;"><strong>附件：</strong><code>CoBM_IC方案专业技术分析报告_20260405.pptx</code></p>
    <p style="font-size: 12px; color: #999;">本报告基于2025-2026年市场调研及行业公开信息 | 分析师：Claude Code AI | 2026-04-05</p>
    </div>
    </body>
    </html>
    """
    return html

def send_email():
    """发送邮件"""
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'CoBM电源IC方案专业技术分析报告-PPT版 2026-04-05'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    # HTML 正文
    html_part = MIMEText(generate_html_body(), 'html', 'utf-8')
    msg.attach(html_part)

    # PPT附件
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, 'rb') as f:
            ppt_content = f.read()

        # 添加 PPT 文件作为附件
        part = MIMEApplication(ppt_content, Name='CoBM_IC方案专业技术分析报告_20260405.pptx')
        part['Content-Disposition'] = 'attachment; filename="CoBM_IC方案专业技术分析报告_20260405.pptx"'
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
    print("CoBM 电源IC方案专业技术分析报告 PPT - 邮件发送")
    print("=" * 60)
    send_email()

if __name__ == '__main__':
    main()
