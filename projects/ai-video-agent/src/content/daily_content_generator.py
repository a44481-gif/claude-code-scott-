#!/usr/bin/env python3
"""
📧 每日内容推送系统
每天自动生成内容并发送到邮箱
"""

import json
from datetime import datetime
import random
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.email.report_sender import ReportSender

# ==================== 内容素材库 ====================

# 宠物赛道 - 爆款文案素材
PET_CONTENT = {
    "猫咪": [
        {
            "title": "猫咪爱你的{}个表现",
            "points": ["蹭你", "露肚子", "慢慢眨眼", "踩奶", "给你送礼物"],
            "type": "知识科普"
        },
        {
            "title": "猫咪生气是因为{}",
            "points": ["你不让上床", "你不给罐头", "你摸了别的猫", "你不陪它玩", "它就是无聊"],
            "type": "趣味互动"
        },
        {
            "title": "新手养猫最易犯的{}个错",
            "points": ["买太小的奶猫", "随意换粮", "不打疫苗", "不封窗", "强行遛猫"],
            "type": "实用干货"
        },
        {
            "title": "猫咪VS狗狗，{}对比",
            "points": ["智商", "忠诚度", "独立性", "粘人度", "拆家能力"],
            "type": "趣味对比"
        },
        {
            "title": "猫咪的{}种神秘行为",
            "points": ["盯着空气看", "突然疯跑", "半夜叫", "揉捏被子", "喜欢纸箱"],
            "type": "知识科普"
        },
    ],
    "狗狗": [
        {
            "title": "狗狗等主人的{}个小时",
            "points": ["看门", "睡觉", "等门开", "迎接", "转圈"],
            "type": "情感故事"
        },
        {
            "title": "狗狗的{}个肢体语言",
            "points": ["摇尾巴", "舔脸", "扑人", "转圈", "叹气"],
            "type": "知识科普"
        },
        {
            "title": "假装睡着测试狗狗反应",
            "points": ["东张西望", "闻你", "舔脸", "叫", "躺下陪着你"],
            "type": "趣味测试"
        },
        {
            "title": "狗狗vs猫咪，{}不同",
            "points": ["表达爱意", "吃饭方式", "等你回家", "睡觉习惯", "拆家能力"],
            "type": "趣味对比"
        },
    ],
    "情感": [
        {
            "title": "离别前的最后{}天",
            "points": ["陪伴", "回忆", "不舍", "告别", "珍惜"],
            "type": "情感共鸣"
        },
        {
            "title": "宠物说给主人的5句话",
            "points": ["谢谢你", "陪我", "不要走", "我爱你", "我会等你"],
            "type": "情感共鸣"
        },
        {
            "title": "养宠物后才知道的5件事",
            "points": ["凌晨被踩醒", "衣服全是毛", "它比你忙", "荷包空了", "更快乐了"],
            "type": "情感共鸣"
        },
    ]
}

# 话题标签库
HASHTAGS = {
    "基础": ["摇尾巴", "萌宠", "宠物", "可爱", "治愈"],
    "猫咪": ["喵星人", "猫奴", "猫咪", "吸猫", "猫猫", "猫主子"],
    "狗狗": ["汪星人", "狗奴", "狗狗", "铲屎官", "萌狗"],
    "知识": ["养宠知识", "科学养宠", "宠物健康", "宠物行为", "宠物心理"],
    "情感": ["感动", "泪目", "宠物故事", "宠物情感", "暖心"],
    "互动": ["评论区", "评论区见", "你家的呢", "中了几个", "你是吗"]
}

# 爆款开场白
HOOKS = [
    "我的天哪！",
    "这也太",
    "你绝对不知道",
    "看完我",
    "必须告诉大家",
    "我发现了！",
]

def generate_daily_content():
    """生成每日内容"""
    # 随机选择类别
    category = random.choice(["猫咪", "狗狗", "情感"])
    content = random.choice(PET_CONTENT[category])
    point = random.choice(content["points"])
    num = random.randint(3, 5)

    # 生成标题
    title = content["title"].format(point) if "{}" in content["title"] else content["title"]
    title = title.format(num) if "{}" in title else title

    # 生成开场白
    hook = random.choice(HOOKS)

    # 生成正文
    body_parts = []
    for i in range(num):
        if content["type"] == "知识科普":
            body_parts.append(f"{i+1}. {content['points'][i % len(content['points'])]}")
        elif content["type"] == "趣味测试":
            body_parts.append(f"看看它会不会{content['points'][i % len(content['points'])]}...")
        else:
            body_parts.append(f"{content['points'][i % len(content['points'])]}")

    # 生成结尾引导
    endings = [
        "中了几个？评论区告诉我！",
        "你家宠物是这样的吗？评论聊聊！",
        "你更认同哪个？评论区说说！",
        "这种情况你家宠物有吗？等你的评论！",
    ]
    ending = random.choice(endings)

    # 生成话题标签
    topics = []
    topics.extend(HASHTAGS["基础"])
    topics.extend(HASHTAGS.get(category, []))
    topics.extend(HASHTAGS.get(content["type"], []))
    topics.append(random.choice(HASHTAGS["互动"]))

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": category,
        "content_type": content["type"],
        "title": title,
        "hook": hook,
        "body": body_parts,
        "ending": ending,
        "hashtags": topics[:10],  # 限制10个标签
    }

def format_content_for_douyin(content):
    """格式化内容为抖音文案"""
    # 开场
    hook = content["hook"].format("")[:-1] if content["hook"].endswith("{}") else content["hook"]

    # 组装文案
    caption = f"{hook}！\n\n"
    caption += f"{content['title']}\n\n"
    caption += "👇👇👇\n\n"

    for point in content["body"]:
        caption += f"{point}\n"

    caption += f"\n{content['ending']}\n\n"
    caption += "@摇尾巴\n\n"

    # 添加话题
    for tag in content["hashtags"]:
        caption += f"#{tag} "

    return caption

def generate_html_email(content, caption):
    """生成HTML邮件内容"""
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .card {{ background: #f9f9f9; padding: 20px; border-radius: 10px; margin: 15px 0; }}
        .title {{ font-size: 24px; color: #333; margin-bottom: 15px; }}
        .caption {{ background: white; padding: 15px; border-radius: 8px; white-space: pre-wrap; line-height: 1.8; }}
        .hashtags {{ color: #667eea; font-size: 14px; margin-top: 10px; }}
        .footer {{ text-align: center; color: #999; margin-top: 20px; font-size: 12px; }}
        .time {{ background: #ff6b6b; color: white; display: inline-block; padding: 5px 15px; border-radius: 20px; }}
        .copy-btn {{ background: #4ecdc4; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐾 每日内容推送</h1>
        <p>摇尾巴 · 宠物赛道</p>
        <span class="time">📅 {content['date']}</span>
    </div>

    <div class="card">
        <h2 class="title">📝 今日内容</h2>
        <p><strong>类型：</strong>{content['content_type']} · {content['category']}</p>
        <p><strong>标题：</strong>{content['title']}</p>
    </div>

    <div class="card">
        <h2 class="title">📱 抖音文案（直接复制）</h2>
        <button class="copy-btn" onclick="copyCaption()">📋 一键复制文案</button>
        <div class="caption" id="caption">{caption}</div>
        <div class="hashtags">
            <strong>话题标签：</strong><br>
            {" ".join(["#" + tag for tag in content['hashtags']])}
        </div>
    </div>

    <div class="card">
        <h2 class="title">⏰ 发布建议</h2>
        <p>🕐 <strong>最佳时间：</strong>12:00 或 18:00</p>
        <p>📍 <strong>发布位置：</strong>抖音APP → 首页「+」</p>
        <p>🏷️ <strong>话题：</strong>直接复制上方标签</p>
    </div>

    <div class="footer">
        <p>由 AI 短视频运营系统自动生成</p>
        <p>收件人：h13751019800@163.com</p>
    </div>

    <script>
        function copyCaption() {{
            const text = document.getElementById('caption').innerText;
            navigator.clipboard.writeText(text).then(() => {{
                alert('已复制！去抖音发布吧！');
            }});
        }}
    </script>
</body>
</html>
"""
    return html

def send_daily_content_email():
    """发送每日内容邮件"""
    print("="*60)
    print("📧 生成每日内容推送...")
    print("="*60)

    # 生成内容
    content = generate_daily_content()
    caption = format_content_for_douyin(content)

    # 生成HTML
    html = generate_html_email(content, caption)

    # 发送邮件
    sender = ReportSender()

    # 读取配置获取收件人
    with open('config/email_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    result = sender.send_custom_email(
        to_email=config['recipient']['email'],
        subject=f"📋 每日内容推送 - {content['date']} | 摇尾巴",
        html_content=html
    )

    if result:
        print()
        print("="*60)
        print("✅ 每日内容已发送到邮箱！")
        print("="*60)
        print()
        print(f"📅 日期：{content['date']}")
        print(f"📝 类型：{content['content_type']} · {content['category']}")
        print(f"📌 标题：{content['title']}")
        print()
        print("📧 请查收邮件，复制文案去抖音发布！")
    else:
        print()
        print("="*60)
        print("❌ 发送失败，请检查邮件配置")
        print("="*60)

    return content, caption

if __name__ == "__main__":
    content, caption = send_daily_content_email()
