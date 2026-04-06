#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动配置抖音推流地址
"""

import os
import sys
import json
import re

def update_douyin_config():
    """更新抖音推流配置"""

    config_path = 'config/live_config.json'

    print("=" * 50)
    print("  抖音推流地址自动配置")
    print("=" * 50)
    print()
    print("请从抖音创作服务平台复制推流地址")
    print("格式: rtmp://push.toutiao.com/live/xxxx-xxxx")
    print()

    # 如果命令行有参数，使用参数
    if len(sys.argv) > 1:
        stream_url = sys.argv[1]
    else:
        stream_url = input("请粘贴推流地址: ").strip()

    if not stream_url:
        print("错误: 推流地址不能为空")
        return False

    # 解析推流地址
    if 'rtmp://' in stream_url:
        # 完整地址
        match = re.match(r'(rtmp://[^/]+/live)/(.+)', stream_url)
        if match:
            stream_server = match.group(1)
            stream_key = match.group(2)
        else:
            print("警告: 无法解析地址格式，使用默认值")
            stream_server = "rtmp://push.toutiao.com/live"
            stream_key = stream_url
    else:
        # 只有key
        stream_server = "rtmp://push.toutiao.com/live"
        stream_key = stream_url

    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 更新配置
    config['live']['platforms']['douyin']['stream_server'] = stream_server
    config['live']['platforms']['douyin']['stream_key'] = stream_key
    config['live']['platforms']['douyin']['enabled'] = True

    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 50)
    print("  配置完成!")
    print("=" * 50)
    print()
    print(f"推流服务器: {stream_server}")
    print(f"推流密钥: {stream_key}")
    print()
    print("下一步:")
    print("1. 打开OBS Studio")
    print("2. 设置 -> 推流")
    print("3. 服务: 自定义")
    print(f"4. 服务器: {stream_server}")
    print(f"5. 推流密钥: {stream_key}")
    print()

    return True

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    update_douyin_config()
