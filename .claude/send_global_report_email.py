#!/usr/bin/env python3
"""
發送顯卡電源線燒毀 - 全球平台研究報告郵件
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# 郵箱配置
SMTP_SERVER = 'smtp.163.com'
SMTP_PORT = 465
SENDER_EMAIL = 'h13751019800@163.com'
SENDER_AUTH_CODE = 'FZQAXDZUHDWQHUIO'
RECIPIENT_EMAIL = 'h13751019800@163.com'

def send_global_report_email():
    """發送全球平台研究報告郵件"""

    subject = f'顯卡電源線燒毀 - 全球平台研究報告 {datetime.now().strftime("%Y年%m月%d日")}'

    # 讀取HTML報告
    report_path = r'd:\claude mini max 2.7\.claude\gpu_cable_burn_global_report.html'
    with open(report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 創建郵件對象
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    # 添加HTML內容
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)

    # 添加純文字版本（備用）
    text_content = f"""
顯卡電源線燒毀 - 全球平台研究報告
報告時間: {datetime.now().strftime('%Y年%m月%d日')}

研究範圍: 全球各大平台英文/中文/日文/歐洲案例

========================================
主要內容
========================================

一、全球案例統計概覽
- 英文平台（北美/全球）: 約 60-80 起
- 中文平台（中國/台灣）: 約 40-50 起
- 日文平台（日本）: 約 10-15 起
- 歐洲平台（德/法/英）: 約 15-20 起

二、英文平台案例與討論
- Reddit (r/nvidia / r/hardware)
- Tom's Hardware / Gamers Nexus
- VideoCardz / TechPowerUp
- Overclock.net / Guru3D

三、中文平台案例與討論
- 知乎 (Zhihu)
- Bilibili (嗶哩嗶哩)
- NGA 玩家社區 / 百度貼吧
- ChipHell / PCEVA / ZOL

四、日文平台案例與討論
- 価格.com (Kakaku.com)
- AKIBA PC Hotline!
- 日本Twitter/X / 5ch

五、歐洲平台案例與討論
- Hardwareluxx (德國)
- Scan (英國) / LDLC (法國)
- Guru3D (荷蘭) / Quelltext (德國)

六、全球案例詳細列表
七、全球平台共識 - 預防建議

========================================
報告已以HTML格式呈現，請使用郵箱客戶端查看完整報告。

---
本郵件由 AI 自動發送
    """
    text_part = MIMEText(text_content, 'plain', 'utf-8')
    msg.attach(text_part)

    try:
        # 連接SMTP服務器
        print(f"連接到 {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

        # 登錄
        print("登錄郵箱...")
        server.login(SENDER_EMAIL, SENDER_AUTH_CODE)

        # 發送郵件
        print(f"發送郵件至 {RECIPIENT_EMAIL}...")
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

        # 關閉連接
        server.quit()

        print("郵件發送成功！")
        return True

    except Exception as e:
        print(f"郵件發送失敗: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("顯卡電源線燒毀 - 全球平台研究報告 郵件發送")
    print("=" * 60)

    success = send_global_report_email()

    if success:
        print("\n郵件已成功發送至:", RECIPIENT_EMAIL)
    else:
        print("\n郵件發送失敗，請檢查配置。")
