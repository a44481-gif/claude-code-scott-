# AI 短视频运营 Agent - 邮件发送模块

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
from pathlib import Path

class ReportSender:
    """运营报告邮件发送器"""

    def __init__(self, config_path="config/email_config.json"):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        """加载邮件配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                self.smtp = self.config.get("smtp", {})
                self.sender = self.config.get("sender", {})
                self.recipient = self.config.get("recipient", {})
                self.report = self.config.get("report", {})
        except FileNotFoundError:
            print("⚠️ 邮件配置文件不存在，使用默认配置")
            self.config = {}
            self.smtp = {}
            self.sender = {}
            self.recipient = {"email": "h13751019800@163.com", "name": "运营负责人"}
            self.report = {"subject_prefix": "【AI短视频运营报告】"}

    def build_subject(self):
        """构建邮件主题"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        subject = f"{self.report.get('subject_prefix', '')}{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        return subject

    def send_report(self, html_content):
        """发送报告邮件"""
        subject = self.build_subject()

        # 检查发件人配置
        sender_email = self.sender.get("email", "")
        sender_password = self.sender.get("password", "")

        if not sender_email or sender_email == "your-email@gmail.com":
            print("\n⚠️ 发件人邮箱未配置")
            print("📝 请编辑 config/email_config.json 配置发件人信息")
            print("\n📧 测试邮件预览：")
            print(f"   收件人：{self.recipient.get('email', 'h13751019800@163.com')}")
            print(f"   主题：{subject}")
            print(f"   内容长度：{len(html_content)} 字符")
            return False

        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.sender.get('name', 'AI运营系统')} <{sender_email}>"
        msg["To"] = f"{self.recipient.get('name', '负责人')} <{self.recipient.get('email', 'h13751019800@163.com')}>"

        # 添加纯文本版本（兼容旧邮件客户端）
        text_content = self.html_to_text(html_content)
        msg.attach(MIMEText(text_content, "plain", "utf-8"))

        # 添加 HTML 版本
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        # 尝试发送
        try:
            print(f"\n📧 正在连接邮件服务器...")
            print(f"   服务器：{self.smtp.get('server', 'smtp.gmail.com')}:{self.smtp.get('port', 587)}")

            with smtplib.SMTP(self.smtp.get("server", "smtp.gmail.com"),
                            self.smtp.get("port", 587)) as server:

                if self.smtp.get("use_tls", True):
                    server.starttls()

                print(f"   登录邮箱：{sender_email}")
                server.login(sender_email, sender_password)

                print(f"   发送邮件至：{self.recipient.get('email', 'h13751019800@163.com')}")
                server.send_message(msg)

            print(f"\n✅ 邮件发送成功！")
            print(f"   收件人：{self.recipient.get('email', 'h13751019800@163.com')}")
            print(f"   主题：{subject}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("\n❌ 邮件认证失败！")
            print("📝 请检查：")
            print("   1. 邮箱地址是否正确")
            print("   2. 密码是否为应用专用密码（非登录密码）")
            print("   3. Gmail 需要开启两步验证后生成应用密码")
            print("   📖 Gmail 应用密码申请：https://myaccount.google.com/security")
            return False

        except smtplib.SMTPException as e:
            print(f"\n❌ SMTP 错误：{e}")
            return False

        except Exception as e:
            print(f"\n❌ 发送失败：{e}")
            return False

    def html_to_text(self, html):
        """将 HTML 转换为纯文本"""
        import re
        # 简单转换，移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', html)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&#39;', "'")
        return text

    def send_custom_email(self, to_email, subject, html_content):
        """发送自定义邮件"""
        sender_email = self.sender.get("email", "")
        sender_password = self.sender.get("password", "")

        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.sender.get('name', 'AI运营系统')} <{sender_email}>"
        msg["To"] = to_email

        # 添加纯文本版本
        text_content = self.html_to_text(html_content)
        msg.attach(MIMEText(text_content, "plain", "utf-8"))

        # 添加 HTML 版本
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            print(f"\n📧 正在连接邮件服务器...")
            with smtplib.SMTP(self.smtp.get("server", "smtp.gmail.com"),
                            self.smtp.get("port", 587)) as server:
                if self.smtp.get("use_tls", True):
                    server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"✅ 邮件发送成功！")
            return True

        except Exception as e:
            print(f"❌ 发送失败：{e}")
            return False

    def send_test_email(self):
        """发送测试邮件"""
        from src.analytics.report_generator import ReportGenerator

        print("=" * 50)
        print("📧 邮件发送测试")
        print("=" * 50)

        # 生成测试报告
        generator = ReportGenerator()
        data = generator.collect_weekly_data()
        html = generator.generate_html_report(data)

        # 发送
        return self.send_report(html)


def test_email_config():
    """测试邮件配置"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    sender = ReportSender()

    print("\n📧 当前邮件配置：")
    print(f"   发件人：{sender.sender.get('email', '未配置')}")
    print(f"   收件人：{sender.recipient.get('email', 'h13751019800@163.com')}")
    print(f"   SMTP服务器：{sender.smtp.get('server', 'smtp.gmail.com')}")
    print(f"   SMTP端口：{sender.smtp.get('port', 587)}")

    return sender


if __name__ == "__main__":
    sender = test_email_config()

    print("\n" + "=" * 50)
    print("是否发送测试邮件到 h13751019800@163.com？")
    print("=" * 50)
    print("提示：请先配置 config/email_config.json 中的发件人信息")
    print()

    # 选择发送
    sender.send_test_email()
