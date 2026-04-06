#!/usr/bin/env python3
"""
每日自动发送内容邮件
设置Windows计划任务，每天早上9点自动执行
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("="*60)
    print("每日内容推送")
    print("="*60)
    print()

    # 导入并运行
    from src.content.daily_content_generator import send_daily_content_email
    send_daily_content_email()

    print()
    print("="*60)
    print("完成！")
    print("="*60)

if __name__ == "__main__":
    main()
