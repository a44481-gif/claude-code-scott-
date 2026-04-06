# 邮箱配置向导
# 帮用户配置邮件发送功能

import json
import os
from pathlib import Path

def setup_email_config():
    """交互式邮箱配置"""

    print("=" * 60)
    print("📧 网易邮箱配置向导")
    print("=" * 60)
    print()
    print("请按提示输入信息，完成后报告将自动发送至：h13751019800@163.com")
    print()

    # 获取用户输入
    email = input("📮 请输入你的网易邮箱地址（如：yourname@163.com）: ").strip()
    if not email:
        print("❌ 邮箱地址不能为空")
        return False

    # 获取授权码
    print()
    print("🔑 授权码获取方法：")
    print("   1. 登录网页版邮箱: https://mail.163.com")
    print("   2. 点击【设置】→【POP3/SMTP/IMAP】")
    print("   3. 开启【SMTP服务】")
    print("   4. 点击【授权码管理】生成授权码")
    print("   5. 复制授权码（注意：是16位授权码，不是登录密码）")
    print()

    auth_code = input("🔑 请输入授权码: ").strip()
    if not auth_code:
        print("❌ 授权码不能为空")
        return False

    # 验证授权码格式（163邮箱授权码是16位）
    if len(auth_code) < 10:
        print("⚠️ 授权码格式可能不正确，请确认")
        confirm = input("是否继续？(y/n): ").strip().lower()
        if confirm != 'y':
            return False

    # 发送测试邮件
    print()
    print("📤 正在测试发送...")

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from datetime import datetime, timedelta

        # 网易邮箱配置
        smtp_server = "smtp.163.com"
        smtp_port = 465  # SSL

        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"【AI短视频运营报告】测试邮件 - {datetime.now().strftime('%Y-%m-%d')}"
        msg["From"] = f"AI运营系统 <{email}>"
        msg["To"] = "h13751019800@163.com"

        # 简单HTML内容
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">📊 AI 短视频运营报告 - 测试邮件</h2>
            <p>这是一封测试邮件，用于验证邮箱配置是否正确。</p>
            <p>配置时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                如果你收到这封邮件，说明配置成功！<br>
                后续每周会自动收到运营报告。
            </p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html", "utf-8"))

        # 发送邮件
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email, auth_code)
            server.send_message(msg)

        print("✅ 测试邮件发送成功！")
        print(f"   已发送至: h13751019800@163.com")

        # 保存配置
        config = {
            "smtp": {
                "server": smtp_server,
                "port": smtp_port,
                "use_ssl": True,
                "use_tls": False
            },
            "sender": {
                "email": email,
                "password": auth_code,
                "name": "AI 短视频运营系统"
            },
            "recipient": {
                "email": "h13751019800@163.com",
                "name": "运营负责人"
            },
            "report": {
                "subject_prefix": "【AI短视频运营报告】",
                "template": "templates/weekly_report.html",
                "include_charts": True
            },
            "schedule": {
                "enabled": True,
                "send_on": ["monday"],
                "send_time": "09:00"
            }
        }

        # 保存到文件
        config_path = Path("config/email_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print()
        print("✅ 配置已保存至: config/email_config.json")

        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ 认证失败！")
        print("   请检查：")
        print("   1. 邮箱地址是否正确")
        print("   2. 授权码是否正确（不是登录密码）")
        print("   3. 163邮箱需要开启SMTP服务并获取授权码")
        return False

    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False


if __name__ == "__main__":
    import sys

    # 设置UTF-8编码
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

    success = setup_email_config()

    if success:
        print()
        print("=" * 60)
        print("🎉 邮箱配置完成！")
        print("=" * 60)
        print()
        print("下一步：")
        print("   1. 运行 python main.py --weekly 发送完整周报")
        print("   2. 或运行 python main.py 启动自动运行")
    else:
        print()
        print("❌ 配置失败，请重试或检查错误信息")
