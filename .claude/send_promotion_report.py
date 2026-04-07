# -*- coding: utf-8 -*-
"""
CoBM DIY PC电源品牌客户推广策略报告发送脚本
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

REPORT_PATH = r'D:/claude mini max 2.7/.claude/CoBM_DIY_PC_电源推广策略_20260406.pptx'

def generate_html_body():
    """生成邮件 HTML 正文"""
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #333;">
    <div style="background: linear-gradient(135deg, #1a5276, #2e86c1); color: white; padding: 25px; border-radius: 10px 10px 0 0;">
      <h1 style="margin: 0; font-size: 24px;">CoBM DIY PC电源品牌客户推广策略</h1>
      <p style="margin: 5px 0 0; opacity: 0.9;">B2B营销 · 客户开发 · 渠道策略 | 2026-04-06</p>
    </div>
    <div style="background: #f9f9f9; padding: 25px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">

    <h2 style="color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 8px;">报告目录</h2>
    <ol>
      <li><strong>目标客户画像与核心痛点</strong> - 台系/大陆/电竞/ITX品牌分类</li>
      <li><strong>精准客户切入策略</strong> - 曜越T.T/长城/航嘉/ROG差异化打法</li>
      <li><strong>B2B营销工具包</strong> - 技术白皮书/对比表/ROI计算器</li>
      <li><strong>渠道策略与展会计划</strong> - Computex 2026展示策略</li>
      <li><strong>销售赋能与话术模板</strong> - 异议处理/价值主张</li>
      <li><strong>执行计划与里程碑</strong> - Q2-Q3推广甘特图</li>
    </ol>

    <h2 style="color: #1a5276;">一、目标客户优先级</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #1a5276; color: white;">
      <th style="padding: 10px;">客户类型</th>
      <th style="padding: 10px;">代表品牌</th>
      <th style="padding: 10px;">年出货量</th>
      <th style="padding: 10px;">优先级</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">台系电源大厂</td>
      <td style="padding: 8px; border: 1px solid #ddd;">曜越T.T、海韵、全汉</td>
      <td style="padding: 8px; border: 1px solid #ddd;">50-100万+</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: red;"><strong>S级</strong></td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">大陆电源品牌</td>
      <td style="padding: 8px; border: 1px solid #ddd;">长城、航嘉、先马</td>
      <td style="padding: 8px; border: 1px solid #ddd;">100万+</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: orange;"><strong>A级</strong></td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">电竞品牌</td>
      <td style="padding: 8px; border: 1px solid #ddd;">ROG、微星MEG</td>
      <td style="padding: 8px; border: 1px solid #ddd;">20-50万</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: orange;"><strong>A级</strong></td>
    </tr>
    </table>

    <h2 style="color: #e74c3c;">二、核心痛点与CoBM解决方案</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #e74c3c; color: white;">
      <th style="padding: 10px;">痛点类型</th>
      <th style="padding: 10px;">具体表现</th>
      <th style="padding: 10px;">CoBM解决能力</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">成本压力</td>
      <td style="padding: 8px; border: 1px solid #ddd;">利润持续压缩</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>BOM成本降低18-28%</strong></td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">效率竞争</td>
      <td style="padding: 8px; border: 1px solid #ddd;">80PLUS认证成本高</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>白金牌低成本实现</strong></td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">功率密度</td>
      <td style="padding: 8px; border: 1px solid #ddd;">ITX/SFF市场需求</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>功率密度+50-65%</strong></td>
    </tr>
    </table>

    <h2 style="color: #27ae60;">三、ROI预期（按50万台/年计算）</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #27ae60; color: white;">
      <th style="padding: 10px;">指标</th>
      <th style="padding: 10px;">数值</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">年BOM成本节省</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>750万元</strong></td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">认证费用节省</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>50万元</strong></td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">ROI</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>320%</strong></td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">投资回收期</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>3个月</strong></td>
    </tr>
    </table>

    <h2 style="color: #1a5276;">四、展会计划</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #8e44ad; color: white;">
      <th style="padding: 10px;">展会名称</th>
      <th style="padding: 10px;">时间</th>
      <th style="padding: 10px;">目标客户数</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">深圳电子展</td>
      <td style="padding: 8px; border: 1px solid #ddd;">4月/10月</td>
      <td style="padding: 8px; border: 1px solid #ddd;">300+品牌</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">Computex 2026</td>
      <td style="padding: 8px; border: 1px solid #ddd;">6月初</td>
      <td style="padding: 8px; border: 1px solid #ddd;">200+品牌</td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">北京国际软硬件展</td>
      <td style="padding: 8px; border: 1px solid #ddd;">9月</td>
      <td style="padding: 8px; border: 1px solid #ddd;">100+品牌</td>
    </tr>
    </table>

    <hr style="margin: 25px 0; border: none; border-top: 1px solid #ddd;">
    <p style="font-size: 13px; color: #666;"><strong>完整报告附件：</strong><code>CoBM_DIY_PC_电源推广策略_20260406.pptx</code>（12页PPT）</p>
    <p style="font-size: 12px; color: #999;">本报告基于CoBM产品分析 | 分析师：Claude Code AI | 2026-04-06</p>
    </div>
    </body>
    </html>
    """
    return html

def send_email():
    """发送邮件"""
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'CoBM DIY PC电源品牌客户推广策略报告 2026-04-06'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    # HTML 正文
    html_part = MIMEText(generate_html_body(), 'html', 'utf-8')
    msg.attach(html_part)

    # 附件
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, 'rb') as f:
            report_content = f.read()

        part = MIMEApplication(report_content, Name='CoBM_DIY_PC_电源推广策略_20260406.pptx')
        part['Content-Disposition'] = 'attachment; filename="CoBM_DIY_PC_电源推广策略_20260406.pptx"'
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
    print("CoBM DIY PC电源品牌客户推广策略 - 邮件发送")
    print("=" * 60)
    send_email()

if __name__ == '__main__':
    main()
