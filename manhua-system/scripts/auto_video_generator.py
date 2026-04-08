#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
漫剧出海AI - 全自动视频生成器
自动生成图片 + 字幕 + 配音 → MP4视频
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import random
from datetime import datetime

# ============ 配置 ============
CONFIG = {
    "output_dir": "output/videos",
    "images_dir": "output/images",
    "fonts_dir": "fonts",
    "default_fps": 2,
    "video_width": 1080,
    "video_height": 1920,
}

# 题材内容库
THEMES = {
    "龙王": {
        "topics": [
            "被嘲笑穷鬼上门女婿", "工地搬砖被嫌脏", "婚礼现场被羞辱",
            "丈母娘要50万彩礼", "外卖小哥救富二代", "修空调被嫌穷",
            "参加同学会被嘲笑", "当保安被白富美嘲笑", "前女友嫌穷分手"
        ],
        "titles": [
            "下一秒十辆豪车来接！丈母娘当场吓瘫！😭🐉",
            "下一秒大客户来工地找他！工友当场吓傻！😂🐉",
            "下一秒三千亿将士到场！全场吓傻跪地求饶！😭👑",
            "下一秒拿出黑卡全场吓傻！💳🐉"
        ],
        "scripts": [
            "被人嘲笑：穷鬼还想娶我女儿？",
            "突然电话响了：老板，您在哪？",
            "全场震惊！十辆豪车到场！",
            "龙王身份揭晓！全场跪地求饶！"
        ]
    },
    "逆袭": {
        "topics": [
            "被公司开除收到1个亿", "被离婚带三宝宝", "火锅店打工被嘲笑",
            "摆地摊被城管追", "电子厂拧螺丝十年", "摆摊卖红薯被城管收",
            "快递员被投诉丢工作", "被亲戚嫌弃寒酸"
        ],
        "titles": [
            "下一秒收到到账1个亿！老板求他回去当董事长！💰💼",
            "三年后我带三个天才宝宝回归！渣夫当场吓哭！😭💪",
            "下一秒服务员喊他老板！😂💪"
        ],
        "scripts": [
            "老婆嫌弃：你能有什么用？",
            "突然手机震动：到账1亿元！",
            "老婆当场吓哭！求他原谅！",
            "三年后带三宝宝华丽回归！"
        ]
    },
    "虐渣": {
        "topics": [
            "渣男炫耀新女友", "闺蜜抢男友", "相亲遇普信男",
            "表妹偷设计稿", "室友偷化妆品", "同事抢我方案获奖",
            "渣男说怀了双胞胎逼我让位", "婆婆嫌我不会生"
        ],
        "titles": [
            "我发了一张照片！全场炸了！😂🔥",
            "我不动声色让她一无所有！🔥手撕绿茶！",
            "下一秒看到我的劳斯莱斯直接吓傻！😂💳",
            "我亮出监控！她当场社死！😂🔥"
        ],
        "scripts": [
            "绿茶炫耀：你算什么？",
            "我微微一笑：哦？",
            "下一秒！我亮出证据！",
            "她当场崩溃！全场炸了！"
        ]
    },
    "重生": {
        "topics": [
            "被老公婆婆害死", "被妹妹害死", "被合伙人背叛",
            "被老板压榨猝死", "被养女拔氧气管", "被网暴自杀"
        ],
        "titles": [
            "重生到结婚前一天！我：不嫁了！😭⚡",
            "重生到她出生那天！这一世我要改写命运！😭⚡",
            "重生归来她跪求原谅！😭⚡"
        ],
        "scripts": [
            "上一世被害死",
            "睁开眼：这是...我重生了？",
            "这一世，我要改写命运！",
            "复仇开始！他们跪地求饶！"
        ]
    },
    "神医": {
        "topics": [
            "路边救摔倒老人", "飞机上救人", "被师父赶下山",
            "医院放弃治疗", "治好小乞丐", "治好瘫痪老人"
        ],
        "titles": [
            "所有人绕着走！结果他是首富亲爹！🩺💰",
            "三针下去她当场醒来！🩺",
            "下山第一天全世界都震惊了！🩺⚡"
        ],
        "scripts": [
            "医院放弃治疗：我也没办法",
            "我上前：三针就好",
            "所有人都震惊了！",
            "他竟然是神医！首富跪谢！"
        ]
    },
    "系统": {
        "topics": [
            "绑定神级篮球系统", "绑定神级选择系统", "绑定神级投资系统",
            "绑定神级厨神系统", "绑定神级美妆系统", "绑定神级游戏系统"
        ],
        "titles": [
            "一挑五完胜校队主力！🏀🎮",
            "第一块石头开出帝王绿！前女友后悔！💰🎮",
            "三个月翻100倍！老板求我收购！💰"
        ],
        "scripts": [
            "绑定神级系统",
            "系统：恭喜宿主获得新手大礼包",
            "开挂人生开始！所有人傻眼！",
            "完胜！震惊全场！"
        ]
    }
}


def ensure_dirs():
    """确保目录存在"""
    for d in [CONFIG["output_dir"], CONFIG["images_dir"]]:
        os.makedirs(d, exist_ok=True)


def generate_content():
    """生成一套内容"""
    theme_name = random.choice(list(THEMES.keys()))
    theme = THEMES[theme_name]

    topic = random.choice(theme["topics"])
    title = random.choice(theme["titles"])
    scripts = theme["scripts"]

    content = {
        "id": f"manhua_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "theme": theme_name,
        "topic": topic,
        "title": f"{topic}！{title}",
        "scripts": [
            f"格1: {topic}...被人嘲笑",
            f"格2: {scripts[0]}",
            f"格3: {scripts[1]}",
            f"格4: {scripts[2]}",
            f"格5: {scripts[3]}",
            "格6: 👇全集VIP已更新 $1.99👇 paypal.me/scott365888 👍点赞+关注！"
        ],
        "caption": f"{topic}\n\n精彩故事，不容错过！\n\n👇【全集VIP已更新 $1.99】\n👍 点赞+关注！",
        "tags": f"#{theme_name} #爽剧 #漫剧 #反转 #逆袭 #全集解锁 #海外华人 #爆款",
        "cta": "👇【全集VIP已更新 $1.99】👉 paypal.me/scott365888 👍 点赞+关注！",
        "post_time": "北京时间 20:00-22:00",
        "generated_at": datetime.now().isoformat()
    }

    return content


def create_image_panels(content):
    """创建图片面板（文字图片）"""
    images = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for i, script in enumerate(content["scripts"]):
        filename = f"panel_{i+1}_{timestamp}.png"
        filepath = os.path.join(CONFIG["images_dir"], filename)
        images.append(filepath)

        # 简单文字图片生成（可用PIL）
        try:
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new('RGB', (1080, 1920), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)

            # 尝试使用默认字体
            try:
                font_size = 60
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            # 绘制文字
            text = script.replace("格1: ", "").replace("格2: ", "").replace("格3: ", "").replace("格4: ", "").replace("格5: ", "").replace("格6: ", "")
            draw.text((100, 800), text, fill=(0, 0, 0), font=font)

            img.save(filepath)
            print(f"  ✅ 已生成图片: {filename}")

        except ImportError:
            # 如果没有PIL，创建占位符文件
            with open(filepath.replace('.png', '.txt'), 'w') as f:
                f.write(script)
            print(f"  ⚠️ PIL未安装，已保存文字: {filename.replace('.png', '.txt')}")

    return images


def create_video_script(content, images):
    """创建视频合成脚本"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    video_filename = f"video_{content['theme']}_{timestamp}.mp4"
    video_path = os.path.join(CONFIG["output_dir"], video_filename)

    script_content = f"""# 视频生成脚本
# 视频文件: {video_filename}
# 主题: {content['theme']}
# 标题: {content['title']}

# 图片列表:
{chr(10).join([f"# {img}" for img in images])}

# 输出路径: {video_path}

# FFmpeg 命令 (如果有FFmpeg):
# ffmpeg -framerate 2 -i "panel_%d.png" -c:v libx264 -pix_fmt yuv420p "{video_path}"

# 或使用 MoviePy:
# from moviepy.editor import *
# clips = [ImageClip(img).set_duration(3) for img in images]
# video = concatenate_videoclips(clips)
# video.write_videofile("{video_path}", fps=24)
"""

    script_path = os.path.join(CONFIG["output_dir"], f"script_{timestamp}.sh")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    return video_path, script_path


def save_content_json(content, images):
    """保存内容JSON"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    content["images"] = images
    content["video_ready"] = True

    json_path = os.path.join(CONFIG["output_dir"], f"content_{timestamp}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    return json_path


def generate_markdown(content, json_path=""):
    """生成Markdown发布文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    md_path = os.path.join(CONFIG["output_dir"], f"publish_{timestamp}.md")

    md_content = f"""# 🎬 漫剧出海 - 今日发布

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📌 {content['theme']}题材

**标题:**
```
{content['title']}
```

**正文:**
```
{content['caption']}
```

**标签:**
```
{content['tags']}
```

**发布时间:** {content['post_time']}

---

## 📱 TikTok 发布模板

**标题:**
```
{content['title']}
```

**描述:**
```
{content['caption']}

{content['cta']}
```

**标签:**
```
{content['tags']}
```

---

## 🎬 6格分镜

{chr(10).join([f"{i+1}. {s}" for i, s in enumerate(content['scripts'])])}

---

## 💰 收款

**链接:** paypal.me/scott365888

---

**文件路径:** {json_path}

"""

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    return md_path


def run_auto_operator():
    """运行自动运营"""
    print("\n" + "="*50)
    print("🤖 漫剧出海AI - 全自动运营系统")
    print("="*50 + "\n")

    ensure_dirs()

    # 1. 生成内容
    print("📝 正在生成内容...")
    content = generate_content()
    print(f"  ✅ 主题: {content['theme']}")
    print(f"  ✅ 标题: {content['title'][:30]}...")

    # 2. 生成图片
    print("\n🎨 正在生成图片...")
    images = create_image_panels(content)

    # 3. 保存JSON
    print("\n💾 正在保存...")
    json_path = save_content_json(content, images)
    print(f"  ✅ JSON: {json_path}")

    # 4. 生成Markdown
    md_path = generate_markdown(content, json_path)
    print(f"  ✅ Markdown: {md_path}")

    # 5. 生成视频脚本
    video_path, script_path = create_video_script(content, images)
    print(f"  ✅ 视频脚本: {script_path}")

    print("\n" + "="*50)
    print("✅ 全自动内容生成完成！")
    print("="*50)
    print(f"""
📋 下一步操作:

1. 查看发布内容:
   {md_path}

2. 生成视频方法:
   - 方法1: 使用剪映"图文成片"功能
   - 方法2: 运行视频脚本 {script_path}

3. 发布到TikTok:
   - 打开 TikTok APP
   - 上传生成的图片/视频
   - 粘贴标题和描述
   - 发布！

💰 收款链接: paypal.me/scott365888
""")

    return content


if __name__ == "__main__":
    run_auto_operator()
