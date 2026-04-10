# -*- coding: utf-8 -*-
"""
品牌開發郵件發送系統
Brand Outreach Email Sender

使用 Gmail SMTP 發送品牌開發郵件
"""

import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Gmail SMTP 配置
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587  # TLS
SENDER_EMAIL = 'scott365888@gmail.com'
# 注意：需要使用 Gmail 應用程式密碼，不是登錄密碼
# Gmail → 安全性 → 兩步驗證 → 應用程式密碼


def get_app_password():
    """獲取應用程式密碼"""
    # 方式1: 從配置文件讀取
    import os
    app_password = os.environ.get('GMAIL_APP_PASSWORD')
    if app_password:
        return app_password

    # 方式2: 從文件讀取
    password_file = 'gmail_app_password.txt'
    try:
        with open(password_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def create_email_a(brand_name: str, case_count: int = 0, specific_issues: str = "") -> tuple:
    """創建郵件模板A - 初次接觸"""
    subject = f"全球顯卡電源接口燒毀研究報告 - 您的品牌涉及{case_count}個案例"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.8; max-width: 800px; margin: 0 auto;">

    <h2 style="color: #2c3e50;">尊敬的{brand_name}採購/產品團隊您好，</h2>

    <p>我是Scott，專注於顯卡電源供電安全的技術顧問。</p>

    <p>我正在進行一項覆蓋全球的研究項目，分析2024年至2026年3月間全球各大品牌的顯卡電源接口燒毀案例。研究數據庫已收錄<strong>41個真實案例</strong>，涵蓋Reddit、Tom's Hardware、知乎、Bilibili等12個主要平台。</p>

    <h3 style="color: #e74c3c;">關於您的品牌：</h3>

    <p>根據我們的研究數據，您的品牌在以下案例中出現：</p>
    <ul>
        <li>案例數量：{case_count}個</li>
        <li>主要問題：{specific_issues if specific_issues else "12VHPWR接口熔化"}</li>
    </ul>

    <h3 style="color: #27ae60;">我們的解決方案：</h3>

    <p>我們開發了一套完整的顯卡供電安全解決方案，包含：</p>
    <ol>
        <li><strong>CoBM集成電源技術</strong> - 紋波降低60%，效率提升2-4%</li>
        <li><strong>原廠規格線材</strong> - 避免第三方線材導致的35%故障</li>
        <li><strong>智能接口保護</strong> - 預防接口未完全插入導致的24%故障</li>
    </ol>

    <h3 style="color: #3498db;">我們提供的價值：</h3>

    <table style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f8f9fa;">
            <th style="padding: 10px; border: 1px solid #ddd;">對電源品牌的價值</th>
            <th style="padding: 10px; border: 1px solid #ddd;">對顯卡品牌的價值</th>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">差異化競爭優勢</td>
            <td style="padding: 10px; border: 1px solid #ddd;">降低RMA率</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">提升產品可靠性</td>
            <td style="padding: 10px; border: 1px solid #ddd;">客戶滿意度提升</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">12年質保支持</td>
            <td style="padding: 10px; border: 1px solid #ddd;">品牌形象升級</td>
        </tr>
    </table>

    <p>期待有機會與您進一步交流，分享我們的研究成果和解決方案。</p>

    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h4 style="margin-top: 0;">聯絡方式：</h4>
        <p style="margin: 5px 0;"><strong>Email:</strong> scott365888@gmail.com</p>
        <p style="margin: 5px 0;"><strong>微信:</strong> PTS9800</p>
    </div>

    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

    <p>Scott<br>顯卡電源安全顧問</p>

    <p style="color: #7f8c8d; font-size: 12px;">本郵件由 AI 助理自動發送 | {datetime.now().strftime('%Y-%m-%d')}</p>

    </body>
    </html>
    """

    text = f"""
尊敬的{brand_name}採購/產品團隊您好，

我是Scott，專注於顯卡電源供電安全的技術顧問。

我正在進行一項覆蓋全球的研究項目，分析2024年至2026年3月間全球各大品牌的顯卡電源接口燒毀案例。研究數據庫已收錄41個真實案例。

關於您的品牌：
- 案例數量：{case_count}個
- 主要問題：{specific_issues if specific_issues else "12VHPWR接口熔化"}

我們的解決方案：
1. CoBM集成電源技術 - 紋波降低60%，效率提升2-4%
2. 原廠規格線材 - 避免第三方線材導致的35%故障
3. 智能接口保護 - 預防接口未完全插入導致的24%故障

聯絡方式：
- Email: scott365888@gmail.com
- 微信: PTS9800

Scott
顯卡電源安全顧問
    """

    return subject, text, html


def create_email_b(brand_name: str) -> tuple:
    """創建郵件模板B - 技術合作提案"""
    subject = "顯卡12VHPWR接口燒毀 - 技術解決方案提案"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.8; max-width: 800px; margin: 0 auto;">

    <h2 style="color: #2c3e50;">尊敬的{brand_name}技術總監/產品經理您好，</h2>

    <h3 style="color: #e74c3c;">一、研究背景</h3>

    <p>2024年至2026年3月間，全球顯卡市場因12VHPWR接口問題導致大量燒毀事故。根據我們的研究：</p>

    <table style="border-collapse: collapse; width: 100%; margin: 15px 0;">
        <tr style="background-color: #e74c3c; color: white;">
            <th style="padding: 10px; border: 1px solid #ddd;">故障原因</th>
            <th style="padding: 10px; border: 1px solid #ddd;">佔比</th>
        </tr>
        <tr><td style="padding: 10px; border: 1px solid #ddd;">第三方轉接線質量問題</td><td style="padding: 10px; border: 1px solid #ddd;">35%</td></tr>
        <tr><td style="padding: 10px; border: 1px solid #ddd;">接口未完全插入</td><td style="padding: 10px; border: 1px solid #ddd;">24%</td></tr>
        <tr><td style="padding: 10px; border: 1px solid #ddd;">電源功率不足</td><td style="padding: 10px; border: 1px solid #ddd;">18%</td></tr>
        <tr><td style="padding: 10px; border: 1px solid #ddd;">線纜彎折過急</td><td style="padding: 10px; border: 1px solid #ddd;">15%</td></tr>
        <tr><td style="padding: 10px; border: 1px solid #ddd;">製造缺陷</td><td style="padding: 10px; border: 1px solid #ddd;">8%</td></tr>
    </table>

    <h3 style="color: #27ae60;">二、我們的技術解決方案</h3>

    <p>我們的解決方案針對<strong>57%可預防的故障</strong>：</p>

    <h4>方案1：CoBM集成電源</h4>
    <ul>
        <li>紋波: 25-35mV → <15mV（降低60%）</li>
        <li>效率: 89-92% → 92-94%（提升2-4%）</li>
        <li>MTBF: 100k → 120k+小時</li>
    </ul>

    <h4>方案2：原廠線材標準化</h4>
    <ul>
        <li>強制使用原廠12VHPWR線材</li>
        <li>避免第三方轉接線（35%故障源）</li>
        <li>統一的接口認證標準</li>
    </ul>

    <h4>方案3：智能接口保護</h4>
    <ul>
        <li>視覺化安裝指導</li>
        <li>卡扣鎖緊確認機制</li>
        <li>溫度監控預警</li>
    </ul>

    <h3 style="color: #3498db;">三、預期效果</h3>

    <table style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #3498db; color: white;">
            <th style="padding: 10px; border: 1px solid #ddd;">指標</th>
            <th style="padding: 10px; border: 1px solid #ddd;">改善前</th>
            <th style="padding: 10px; border: 1px solid #ddd;">改善後</th>
        </tr>
        <tr><td style="padding: 10px; border: 1px solid #ddd;">接口燒毀率</td><td>100%基準</td><td>-57%</td></tr>
        <tr><td style="padding: 10px; border: 1px solid #ddd;">RMA率</td><td>基準</td><td>-40%</td></tr>
        <tr><td style="padding: 10px; border: 1px solid #ddd;">客戶滿意度</td><td>基準</td><td>+25%</td></tr>
    </table>

    <h3 style="color: #9b59b6;">四、合作模式</h3>
    <ol>
        <li><strong>技術授權:</strong> 提供CoBM方案技術授權</li>
        <li><strong>聯合開發:</strong> 共同開發定制化解決方案</li>
        <li><strong>品牌認證:</strong> 聯合品牌認證CoBM升級套裝</li>
    </ol>

    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h4 style="margin-top: 0;">聯絡方式：</h4>
        <p style="margin: 5px 0;"><strong>Email:</strong> scott365888@gmail.com</p>
        <p style="margin: 5px 0;"><strong>微信:</strong> PTS9800</p>
    </div>

    <p>期待與您深入探討合作細節。</p>

    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <p>Scott<br>顯卡電源安全顧問</p>

    </body>
    </html>
    """

    text = f"""
尊敬的{brand_name}技術總監/產品經理您好，

一、研究背景

2024年至2026年3月間，全球顯卡市場因12VHPWR接口問題導致大量燒毀事故。

故障原因分佈：
- 第三方轉接線質量問題: 35%
- 接口未完全插入: 24%
- 電源功率不足: 18%
- 線纜彎折過急: 15%
- 製造缺陷: 8%

二、我們的技術解決方案

我們的解決方案針對57%可預防的故障：

方案1：CoBM集成電源
- 紋波降低60%
- 效率提升2-4%
- MTBF提升20%

方案2：原廠線材標準化
方案3：智能接口保護

三、合作模式
1. 技術授權
2. 聯合開發
3. 品牌認證

聯絡方式：
- Email: scott365888@gmail.com
- 微信: PTS9800

Scott
顯卡電源安全顧問
    """

    return subject, text, html


def send_email(to_email: str, subject: str, text_body: str, html_body: str = None) -> bool:
    """
    發送郵件

    Args:
        to_email: 收件人郵箱
        subject: 郵件主題
        text_body: 純文字內容
        html_body: HTML內容（可選）

    Returns:
        bool: 發送是否成功
    """
    app_password = get_app_password()

    if not app_password:
        print("❌ 錯誤: 請先設置 Gmail 應用程式密碼")
        print("   1. 登錄 Gmail → 安全性 → 兩步驗證 → 應用程式密碼")
        print("   2. 生成密碼後，保存到 gmail_app_password.txt 文件")
        print("   或設置環境變量: export GMAIL_APP_PASSWORD='你的密碼'")
        return False

    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    # 添加純文字版本
    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))

    # 添加HTML版本（如果提供）
    if html_body:
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        print(f"📧 連接到 {SMTP_HOST}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()  # 啟用TLS加密
        print("🔐 登錄郵箱...")
        server.login(SENDER_EMAIL, app_password)
        print(f"📤 發送郵件至 {to_email}...")
        server.send_message(msg)
        server.quit()
        print(f"✅ 郵件發送成功!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("❌ 認證失敗: 應用程式密碼可能已過期或不正確")
        return False
    except Exception as e:
        print(f"❌ 發送失敗: {e}")
        return False


def send_to_brand(brand: str, email: str, template: str = 'A', **kwargs) -> bool:
    """發送郵件給指定品牌"""
    if template == 'A':
        case_count = kwargs.get('case_count', 0)
        issues = kwargs.get('issues', '')
        subject, text, html = create_email_a(brand, case_count, issues)
    elif template == 'B':
        subject, text, html = create_email_b(brand)
    else:
        print(f"❌ 未知模板: {template}")
        return False

    return send_email(email, subject, text, html)


def main():
    """主程序"""
    print("=" * 60)
    print("品牌開發郵件發送系統")
    print("=" * 60)

    # 測試郵箱連接
    print("\n📧 測試郵箱配置...")
    app_password = get_app_password()
    if not app_password:
        print("⚠️ 未設置應用程式密碼，請先配置")
        print("   1. Gmail → 安全性 → 兩步驗證 → 應用程式密碼")
        print("   2. 保存密碼到 gmail_app_password.txt")
        return

    # 測試發送
    print("\n📤 測試發送郵件...")
    test_email = 'scott365888@gmail.com'  # 發送給自己測試

    subject, text, html = create_email_a("測試品牌", 5, "12VHPWR接口熔化")
    success = send_email(test_email, subject, text, html)

    if success:
        print(f"\n✅ 測試郵件已發送至 {test_email}")
        print("   請檢查郵箱確認發送正常")
    else:
        print("\n❌ 測試發送失敗，請檢查配置")


if __name__ == '__main__':
    main()
