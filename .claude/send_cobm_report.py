# -*- coding: utf-8 -*-
"""
CoBM 技术分析报告发送脚本
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

REPORT_PATH = r'D:/claude mini max 2.7/.claude/CoBM_技术分析报告_20260405.md'

def read_report():
    """读取报告文件"""
    with open(REPORT_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def generate_html_body():
    """生成邮件 HTML 正文"""
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #333;">
    <div style="background: linear-gradient(135deg, #1a5276, #2980b9); color: white; padding: 25px; border-radius: 10px 10px 0 0;">
      <h1 style="margin: 0; font-size: 24px;">CoBM 技术分析报告（完整版）</h1>
      <p style="margin: 5px 0 0; opacity: 0.9;">海盗船市场切入策略 · 财务模型 · 技术规格对比 | 2026-04-05</p>
    </div>
    <div style="background: #f9f9f9; padding: 25px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">

    <h2 style="color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 8px;">报告概览</h2>
    <p>本报告已完成全面更新，新增<strong>财务模型（ROI分析）</strong>与<strong>产品技术规格对比表</strong>两大部分。</p>

    <h2 style="color: #1a5276;">一、CoBM 技术核心优势（摘要）</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #1a5276; color: white;">
      <th style="padding: 10px; text-align: left;">维度</th>
      <th style="padding: 10px; text-align: left;">核心优势</th>
      <th style="padding: 10px; text-align: left;">量化表现</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>性能</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">高功率密度 + 低纹波</td>
      <td style="padding: 8px; border: 1px solid #ddd;">功率密度 +65%，纹波 -60%</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>能效</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">金牌→白金牌升级</td>
      <td style="padding: 8px; border: 1px solid #ddd;">效率 +2~4%</td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>成本</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">BOM+制造综合成本</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>降低 18%~28%</strong></td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>可靠性</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">焊点失效率降低</td>
      <td style="padding: 8px; border: 1px solid #ddd;">-80%+，MTBF 120,000h+</td>
    </tr>
    </table>

    <h2 style="color: #1a5276;">二、财务模型核心结论</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #27ae60; color: white;">
      <th style="padding: 10px;">财务指标</th>
      <th style="padding: 10px;">保守情景</th>
      <th style="padding: 10px;">基准情景</th>
      <th style="padding: 10px;">乐观情景</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">总投资成本</td>
      <td style="padding: 8px; border: 1px solid #ddd;">$169.4 万</td>
      <td style="padding: 8px; border: 1px solid #ddd;">$139.4 万</td>
      <td style="padding: 8px; border: 1px solid #ddd;">$109.5 万</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">三年净利润</td>
      <td style="padding: 8px; border: 1px solid #ddd;">+$55.6 万</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>+$175.6 万</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;">+$340.5 万</td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">三年 ROI</td>
      <td style="padding: 8px; border: 1px solid #ddd;">+33%</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>+126%</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;">+311%</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">投资回收期</td>
      <td style="padding: 8px; border: 1px solid #ddd;">18~24 个月</td>
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>14~18 个月</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">10~14 个月</td>
    </tr>
    </table>

    <h2 style="color: #1a5276;">三、最佳切入点</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #8e44ad; color: white;">
      <th style="padding: 10px;">优先级</th>
      <th style="padding: 10px;">型号</th>
      <th style="padding: 10px;">瓦数</th>
      <th style="padding: 10px;">选型理由</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">★★★★★</td>
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>RM550x CoBM</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">550W</td>
      <td style="padding: 8px; border: 1px solid #ddd;">入门高端 RTX 4060 Ti 黄金搭配</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">★★★★★</td>
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>RM650x CoBM</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">650W</td>
      <td style="padding: 8px; border: 1px solid #ddd;">出货量最大、性价比敏感区间</td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">★★★★★</td>
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>RM750x CoBM</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">750W</td>
      <td style="padding: 8px; border: 1px solid #ddd;">主攻 RTX 4070/4080 主流平台</td>
    </tr>
    </table>

    <h2 style="color: #e74c3c;">四、立即行动（本周）</h2>
    <div style="background: #fef9e7; border-left: 5px solid #f39c12; padding: 15px; margin: 10px 0;">
    <p><strong>P0 — 本周内：</strong>锁定 2 家 CoBM 封装厂商，启动 NRE 谈判</p>
    <p><strong>P1 — 2026 Q2：</strong>搭建 650W CoBM 原理样机</p>
    <p><strong>P2 — 2026 Q3：</strong>启动 80PLUS 白金认证预测试</p>
    <p><strong>P3 — 2026 Q4：</strong>确定上市联动 RTX 5070 发布计划</p>
    </div>

    <h2 style="color: #1a5276;">五、销售增长预测（基准情景）</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #1a5276; color: white;">
      <th style="padding: 10px;">情景</th>
      <th style="padding: 10px;">年度销量增量</th>
      <th style="padding: 10px;">新增营收</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">乐观</td>
      <td style="padding: 8px; border: 1px solid #ddd;">+35%~45%</td>
      <td style="padding: 8px; border: 1px solid #ddd;">+$1.8 亿~$2.4 亿</td>
    </tr>
    <tr style="background: #d5f5e3;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>基准（推荐）</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>+20%~28%</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>+$1.0 亿~$1.4 亿</strong></td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">保守</td>
      <td style="padding: 8px; border: 1px solid #ddd;">+10%~15%</td>
      <td style="padding: 8px; border: 1px solid #ddd;">+$0.5 亿~$0.8 亿</td>
    </tr>
    </table>

    <hr style="margin: 25px 0; border: none; border-top: 1px solid #ddd;">
    <p style="font-size: 13px; color: #666;"><strong>完整报告附件：</strong><code>CoBM_技术分析报告_20260405.md</code>（约 1500+ 行，含完整财务模型、产品规格对比表）</p>
    <p style="font-size: 12px; color: #999;">本报告数据基于 2025 年市场调研及行业经验估算，投资决策前请结合内部数据验证。 | 分析师：Claude Code AI | 2026-04-05</p>
    </div>
    </body>
    </html>
    """
    return html

def send_email():
    """发送邮件"""
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'CoBM技术分析报告（完整版）2026-04-05'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    # HTML 正文
    html_part = MIMEText(generate_html_body(), 'html', 'utf-8')
    msg.attach(html_part)

    # 附件
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, 'r', encoding='utf-8') as f:
            report_content = f.read()

        # 添加 MD 文件作为附件
        part = MIMEApplication(report_content.encode('utf-8'), Name='CoBM_技术分析报告_20260405.md')
        part['Content-Disposition'] = 'attachment; filename="CoBM_技术分析报告_20260405.md"'
        msg.attach(part)
        print(f"已附加报告文件: {REPORT_PATH}")
    else:
        print(f"报告文件不存在: {REPORT_PATH}")

    try:
        print(f"连接到 {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        print("登录邮箱...")
        server.login(SENDER_EMAIL, SENDER_AUTH_CODE)
        print(f"发送邮件至 {RECIPIENT_EMAIL}...")
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("邮件发送成功！")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

def main():
    print("=" * 60)
    print("CoBM 技术分析报告 - 邮件发送")
    print("=" * 60)
    send_email()

if __name__ == '__main__':
    main()
