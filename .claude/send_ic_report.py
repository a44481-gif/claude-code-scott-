# -*- coding: utf-8 -*-
"""
CoBM 电源IC方案专业技术分析报告发送脚本
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
      <h1 style="margin: 0; font-size: 24px;">CoBM 电源IC方案专业技术分析报告</h1>
      <p style="margin: 5px 0 0; opacity: 0.9;">GaN · SiC · Si · 数字控制 · 封装技术 | 2026-04-05</p>
    </div>
    <div style="background: #f9f9f9; padding: 25px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">

    <h2 style="color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 8px;">报告目录</h2>
    <ol>
      <li><strong>电源IC技术分类体系</strong> - 功能架构与半导体材料分类</li>
      <li><strong>GaN/SiC/Si IC方案详细分析</strong> - 主流厂商产品线对比</li>
      <li><strong>数字控制IC方案分析</strong> - TI/Infineon/NXP/Microchip</li>
      <li><strong>PFC与LLC控制器IC</strong> - CCM/Totem-Pole/LLC谐振</li>
      <li><strong>CoBM封装技术分析</strong> - 与传统封装对比</li>
      <li><strong>IC方案选型指南</strong> - 按功率段推荐</li>
      <li><strong>综合对比与供应商生态</strong> - 全链路分析</li>
      <li><strong>结论与投资建议</strong> - Phase 1/2/3规划</li>
    </ol>

    <h2 style="color: #1a5276;">一、半导体材料技术对比</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #1a5276; color: white;">
      <th style="padding: 10px;">材料</th>
      <th style="padding: 10px;">带隙(eV)</th>
      <th style="padding: 10px;">耐压</th>
      <th style="padding: 10px;">效率</th>
      <th style="padding: 10px;">成本</th>
      <th style="padding: 10px;">市场地位</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>Si (硅)</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">1.1</td>
      <td style="padding: 8px; border: 1px solid #ddd;">650V级</td>
      <td style="padding: 8px; border: 1px solid #ddd;">92-95%</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>$0.1-0.5</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">主流 70%</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>GaN (氮化镓)</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">3.4</td>
      <td style="padding: 8px; border: 1px solid #ddd;">650/800V</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>96-99%</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">$0.6-2.5</td>
      <td style="padding: 8px; border: 1px solid #ddd;">快速增长</td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>SiC (碳化硅)</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">3.3</td>
      <td style="padding: 8px; border: 1px solid #ddd;">650-1700V</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>97-99%</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd; color: red;">$1.5-8.0</td>
      <td style="padding: 8px; border: 1px solid #ddd;">高端市场</td>
    </tr>
    </table>

    <h2 style="color: #1a5276;">二、GaN厂商产品线对比</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #27ae60; color: white;">
      <th style="padding: 10px;">厂商</th>
      <th style="padding: 10px;">产品系列</th>
      <th style="padding: 10px;">耐压</th>
      <th style="padding: 10px;">峰值效率</th>
      <th style="padding: 10px;">主要应用</th>
      <th style="padding: 10px;">价格</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>Infineon</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">CoolGaN G5</td>
      <td style="padding: 8px; border: 1px solid #ddd;">600V</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>>98%</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">服务器/汽车</td>
      <td style="padding: 8px; border: 1px solid #ddd;">$1.2-2.5</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>Navitas</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">GaNFast Gen2</td>
      <td style="padding: 8px; border: 1px solid #ddd;">650V</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>99%</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">USB-PD/消费</td>
      <td style="padding: 8px; border: 1px solid #ddd;">$0.8-1.5</td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>Power Integrations</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">InnoSwitch5-Pro</td>
      <td style="padding: 8px; border: 1px solid #ddd;">650V</td>
      <td style="padding: 8px; border: 1px solid #ddd;">97%</td>
      <td style="padding: 8px; border: 1px solid #ddd;">AC-DC/充电</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>$0.6-1.2</strong></td>
    </tr>
    </table>

    <h2 style="color: #1a5276;">三、数字控制器对比</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #8e44ad; color: white;">
      <th style="padding: 10px;">型号</th>
      <th style="padding: 10px;">厂商</th>
      <th style="padding: 10px;">主频</th>
      <th style="padding: 10px;">PWM分辨率</th>
      <th style="padding: 10px;">PMBus</th>
      <th style="padding: 10px;">应用</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">TMS320F28379D</td>
      <td style="padding: 8px; border: 1px solid #ddd;">TI</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>200MHz</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">150ps</td>
      <td style="padding: 8px; border: 1px solid #ddd;">v1.3</td>
      <td style="padding: 8px; border: 1px solid #ddd;">旗舰服务器</td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">UCD3138</td>
      <td style="padding: 8px; border: 1px solid #ddd;">TI</td>
      <td style="padding: 8px; border: 1px solid #ddd;">125MHz</td>
      <td style="padding: 8px; border: 1px solid #ddd;">250ps</td>
      <td style="padding: 8px; border: 1px solid #ddd;">v1.3</td>
      <td style="padding: 8px; border: 1px solid #ddd;">通信电源</td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">XMC4500</td>
      <td style="padding: 8px; border: 1px solid #ddd;">Infineon</td>
      <td style="padding: 8px; border: 1px solid #ddd;">144MHz</td>
      <td style="padding: 8px; border: 1px solid #ddd;">100ps</td>
      <td style="padding: 8px; border: 1px solid #ddd;">可选</td>
      <td style="padding: 8px; border: 1px solid #ddd;">工业</td>
    </tr>
    </table>

    <h2 style="color: #e74c3c;">四、CoBM方案 vs 传统方案 (750W)</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
    <tr style="background: #e74c3c; color: white;">
      <th style="padding: 10px;">指标</th>
      <th style="padding: 10px;">CoBM(Si)</th>
      <th style="padding: 10px;">CoBM(GaN)</th>
      <th style="padding: 10px;">分立Si(传统)</th>
      <th style="padding: 10px;">提升幅度</th>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">BOM成本</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>$38-42</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">$42-48</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: red;">$50-55</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>-20%~-25%</strong></td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">80+认证</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>白金牌</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>白金牌+</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">金牌</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>+2~4%</strong></td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">功率密度</td>
      <td style="padding: 8px; border: 1px solid #ddd;">28-32 W/in3</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>35-40 W/in3</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">18-22 W/in3</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>+50%~-65%</strong></td>
    </tr>
    <tr style="background: #f2f2f2;">
      <td style="padding: 8px; border: 1px solid #ddd;">纹波(12V)</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong><15mV</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong><12mV</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd; color: red;">25-35mV</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>-50%~-60%</strong></td>
    </tr>
    <tr style="background: #fff;">
      <td style="padding: 8px; border: 1px solid #ddd;">边际毛利率</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>28-32%</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">26-30%</td>
      <td style="padding: 8px; border: 1px solid #ddd;">18-22%</td>
      <td style="padding: 8px; border: 1px solid #ddd; color: green;"><strong>+8~10pp</strong></td>
    </tr>
    </table>

    <h2 style="color: #1a5276;">五、投资建议</h2>
    <div style="background: #d5f5e3; border-left: 5px solid #27ae60; padding: 15px; margin: 10px 0;">
    <p><strong>Phase 1 (2026-2027)：</strong>RM550x/650x/750x -> CoBM(Si) -> ROI 126%</p>
    <p><strong>Phase 2 (2027-2028)：</strong>SF750 SFX -> CoBM(GaN) -> 体积-30%</p>
    <p><strong>Phase 3 (2028-2029)：</strong>HX1200旗舰 -> CoBM(SiC) -> 效率99%+</p>
    </div>

    <hr style="margin: 25px 0; border: none; border-top: 1px solid #ddd;">
    <p style="font-size: 13px; color: #666;"><strong>完整报告附件：</strong><code>CoBM_IC方案专业技术分析报告_20260405.md</code></p>
    <p style="font-size: 12px; color: #999;">本报告基于2025-2026年市场调研及行业公开信息 | 分析师：Claude Code AI | 2026-04-05</p>
    </div>
    </body>
    </html>
    """
    return html

def send_email():
    """发送邮件"""
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'CoBM电源IC方案专业技术分析报告(PPT) 2026-04-05'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    # HTML 正文
    html_part = MIMEText(generate_html_body(), 'html', 'utf-8')
    msg.attach(html_part)

    # 附件
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, 'rb') as f:
            report_content = f.read()

        # 添加 PPT 文件作为附件
        part = MIMEApplication(report_content, Name='CoBM_IC方案专业技术分析报告_20260405.pptx')
        part['Content-Disposition'] = 'attachment; filename="CoBM_IC方案专业技术分析报告_20260405.pptx"'
        msg.attach(part)
        print("已附加PPT文件: " + REPORT_PATH)
    else:
        print("报告文件不存在: " + REPORT_PATH)

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
    print("CoBM 电源IC方案专业技术分析报告(PPT) - 邮件发送")
    print("=" * 60)
    send_email()

if __name__ == '__main__':
    main()
