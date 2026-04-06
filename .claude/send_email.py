"""
電源供應器銷售數據報告郵件發送腳本
使用163郵箱SMTP發送HTML報告
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# 郵箱配置
SMTP_SERVER = 'smtp.163.com'
SMTP_PORT = 465
SENDER_EMAIL = 'h13751019800@163.com'
SENDER_AUTH_CODE = 'FZQAXDZUHDWQHUIO'
RECIPIENT_EMAIL = 'h13751019800@163.com'

def send_email_with_report(html_report_path, subject=None):
    """發送帶有HTML報告的郵件"""
    
    if subject is None:
        timestamp = datetime.now().strftime('%Y年%m月%d日')
        subject = f'每日電源供應器銷售數據報告 - {timestamp}'
    
    # 讀取HTML報告
    with open(html_report_path, 'r', encoding='utf-8') as f:
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
每日電源供應器銷售數據報告
報告時間: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

品牌: 華碩(ASUS)、微星(MSI)、技嘉(Gigabyte)、Corsair

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

def main():
    print("=" * 50)
    print("電源供應器銷售數據報告 - 郵件發送")
    print("=" * 50)
    
    # 報告文件路徑
    report_path = r'd:\claude mini max 2.7\.claude\psu_daily_report_20260402.html'
    
    # 發送郵件
    success = send_email_with_report(report_path)
    
    if success:
        print("\n郵件已成功發送至: h13751019800@163.com")
    else:
        print("\n郵件發送失敗，請檢查配置。")

if __name__ == '__main__':
    main()
