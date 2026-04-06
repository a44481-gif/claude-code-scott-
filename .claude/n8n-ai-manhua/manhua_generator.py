#!/usr/bin/env python3
"""
漫剧出海AI变现内容生成器
直接使用 Claude Code 或 Anthropic API 生成内容
"""

import json
import random
from datetime import datetime

# 6种题材类型
THEMES = ['龙王', '逆袭', '虐渣', '重生', '神医', '系统']

def generate_theme_prompt(theme_type):
    """生成对应题材的完整提示词"""
    return f"""你是专业的漫剧出海AI变现运营师，专注生成{theme_type}题材爆款内容，所有内容以转化收钱为核心，严格输出JSON格式，禁止多余解释。

题材类型：{theme_type}

请生成一套完整的{theme_type}题材漫剧内容：
1. theme: 高变现{theme_type}漫剧主题（霸气、有噱头）
2. 6_panel_script: 6格分镜台词
   - 第1格：强冲突钩子，3秒抓住用户
   - 第2-5格：制造爽点、悬念、矛盾
   - 第6格：断更留悬念，引导付费看全集
3. title: TikTok强钩子付费标题（提升点击率）
4. caption: 高转化发布文案（含付费引导、催更关注）
5. tags: 10个精准变现热门标签
6. cta_text: 跳转付费链接话术
7. post_time: 最佳变现发布时间（北京时间+美西时间）

输出格式（仅JSON，不要任何其他内容）：
{{
  "theme": "{theme_type}-xxx",
  "6_panel_script": "格1: xxx\\n格2: xxx\\n格3: xxx\\n格4: xxx\\n格5: xxx\\n格6: xxx",
  "title": "付费钩子标题",
  "caption": "发布文案",
  "tags": "#标签1 #标签2...",
  "cta_text": "CTA话术",
  "post_time": "最佳发布时间"
}}"""

def generate_batch(theme_type, count=5):
    """批量生成指定题材内容"""
    print(f"\n{'='*60}")
    print(f"🎬 生成 {count} 套 {theme_type} 题材内容")
    print('='*60)

    results = []
    for i in range(count):
        print(f"\n📌 第 {i+1} 套内容:")
        print("-" * 40)
        print(f"[提示词已生成，请复制到 Claude Code 执行]")
        print(f"\n{generate_theme_prompt(theme_type)}")
        results.append({
            "index": i+1,
            "theme": theme_type,
            "prompt": generate_theme_prompt(theme_type)
        })
    return results

def main():
    print("🎬 漫剧出海AI变现内容生成器")
    print("=" * 60)

    while True:
        print("\n📋 功能菜单:")
        print("1. 生成 龙王 题材")
        print("2. 生成 逆袭 题材")
        print("3. 生成 虐渣 题材")
        print("4. 生成 重生 题材")
        print("5. 生成 神医 题材")
        print("6. 生成 系统 题材")
        print("7. 生成全部6种题材各5套")
        print("8. 随机生成1套")
        print("0. 退出")

        choice = input("\n请选择 (0-8): ").strip()

        if choice == '0':
            print("再见！")
            break
        elif choice == '1':
            generate_batch('龙王')
        elif choice == '2':
            generate_batch('逆袭')
        elif choice == '3':
            generate_batch('虐渣')
        elif choice == '4':
            generate_batch('重生')
        elif choice == '5':
            generate_batch('神医')
        elif choice == '6':
            generate_batch('系统')
        elif choice == '7':
            for theme in THEMES:
                generate_batch(theme, 5)
        elif choice == '8':
            theme = random.choice(THEMES)
            generate_batch(theme, 1)
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()
