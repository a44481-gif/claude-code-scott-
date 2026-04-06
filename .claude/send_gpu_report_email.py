#!/usr/bin/env python3
"""
發送顯卡電源線燒毀研究報告郵件
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

def send_gpu_report_email():
    """發送顯卡電源線燒毀研究報告郵件"""

    subject = f'顯卡電源線燒毀研究報告 - {datetime.now().strftime("%Y年%m月%d日")}'

    # 讀取HTML報告
    report_path = r'd:\claude mini max 2.7\.claude\gpu_cable_burn_report.html'
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
顯卡電源線燒毀研究報告
報告時間: {datetime.now().strftime('%Y年%m月%d日')}

研究範圍: 2024-2025年 顯示卡電源線燒毀案例分析

主要內容:
1. 事件背景 - RTX 4090 12VHPWR 接口熔化問題
2. 案例統計 - 各品牌型號燒毀案例
3. 原因分析 - 電源連接、供應器、散熱、軟體問題
4. 官方回應 - NVIDIA 保修與更換政策
5. 預防措施 - 日常預防、安裝注意事項
6. 相關資源 - 影片教學、技術文章

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
    print("=" * 50)
    print("顯卡電源線燒毀研究報告 - 郵件發送")
    print("=" * 50)

    success = send_gpu_report_email()

    if success:
        print("\n郵件已成功發送至:", RECIPIENT_EMAIL)
    else:
        print("\n郵件發送失敗，請檢查配置。")
