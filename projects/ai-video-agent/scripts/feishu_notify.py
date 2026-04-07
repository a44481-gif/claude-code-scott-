#!/usr/bin/env python3
"""
飞书通知脚本
发送每日内容到飞书
"""

import requests
import json
import sys
from datetime import datetime

def send_feishu_message(title: str, content: str, webhook_url: str = None):
    """
    发送飞书消息

    Args:
        title: 消息标题
        content: 消息内容
        webhook_url: 飞书机器人 Webhook 地址
    """
    if not webhook_url:
        # 默认使用环境变量
        webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID"

    # 构造消息
    message = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🤖 {title}"
                },
                "template": "purple"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ]
        }
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        result = response.json()

        if result.get("code") == 0:
            print("✅ 飞书消息发送成功！")
            return True
        else:
            print(f"❌ 发送失败：{result.get('msg')}")
            return False

    except Exception as e:
        print(f"❌ 发送异常：{e}")
        return False

def send_simple_message(text: str, webhook_url: str = None):
    """发送简单文本消息"""
    if not webhook_url:
        webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID"

    message = {
        "msg_type": "text",
        "content": {
            "text": text
        }
    }

    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        result = response.json()
        return result.get("code") == 0
    except Exception as e:
        print(f"❌ 发送异常：{e}")
        return False

if __name__ == "__main__":
    # 测试发送
    if len(sys.argv) > 1:
        title = sys.argv[1]
        content = sys.argv[2] if len(sys.argv) > 2 else "内容已生成"
    else:
        title = "AI 短视频运营报告"
        content = "每日内容已自动生成"

    send_feishu_message(title, content)
