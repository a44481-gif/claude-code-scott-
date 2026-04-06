# AI 短视频运营 Agent - 脚本生成器
# 功能：自动生成视频脚本（禅心师姐 & 爪爪博士）

import json
import random
from datetime import datetime
from pathlib import Path

class ScriptGenerator:
    """视频脚本生成器"""

    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.load_config()
        self.load_templates()

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 配置文件不存在，使用默认配置")
            self.config = {
                "ip_settings": {
                    "primary_ip": {"name": "禅心师姐"},
                    "secondary_ip": {"name": "爪爪博士"}
                }
            }

    def load_templates(self):
        """加载内容模板"""
        self.templates = {
            # ========== 禅心师姐模板 ==========
            "禅心师姐": {
                "早安禅语": {
                    "duration": "45秒",
                    "structure": ["开场问候", "禅语分享", "延伸解读", "行动引导", "结束互动"],
                    "opening_phrases": [
                        "早安。此刻，你的心在哪里？",
                        "新的一天，从心开始。",
                        "清晨的第一缕阳光，送给此刻醒来的你。"
                    ],
                    "zen_phrases": [
                        "昨天再好，也走不回去。明天再难，也要抬脚继续。",
                        "我们真正拥有的，只有此刻。",
                        "放下执念，看见已拥有。停止比较，专注自己。心怀感恩，远离抱怨。"
                    ],
                    "closing_phrases": [
                        "愿你今天，心安，自在。",
                        "喜欢这样的早安，点个关注~",
                        "关注禅心师姐，每天陪你用禅意开启新的一天。"
                    ]
                },
                "知识科普": {
                    "duration": "35秒",
                    "structure": ["开场钩子", "数字揭秘", "要点解读", "收藏引导"],
                    "hooks": [
                        "一个人痛苦的根源，逃不出这3个字。",
                        "师父说：这5件事，做得越少命越好。",
                        "修行100天，我发现了3个人生真相。"
                    ],
                    "topics": ["执", "比", "怨", "放下", "感恩", "正念"],
                    "closing_phrases": [
                        "觉得有用，就收藏起来。",
                        "下次迷茫时，拿出来看看。",
                        "关注禅心师姐，每天分享修行智慧。"
                    ]
                },
                "故事分享": {
                    "duration": "60秒",
                    "structure": ["故事引入", "情节展开", "转折点", "感悟总结", "互动引导"],
                    "story_openers": [
                        "那年，我负债累累。直到去了峨眉山，遇到一位师父...",
                        "敦煌壁画里，藏着一个关于放下的秘密...",
                        "一位道长收徒的条件，看完沉默了..."
                    ],
                    "story_enders": [
                        "那一刻，我泪流满面。不是因为悲伤，是因为释然。",
                        "如今，我依然会迷茫，但我学会了与它们和平共处。",
                        "这3句话，也送给你。你也有过这样的时刻吗？"
                    ]
                },
                "冥想引导": {
                    "duration": "180秒",
                    "structure": ["引导语", "呼吸练习", "身体扫描", "肯定语", "结束语"],
                    "intro_phrases": [
                        "现在，找一个舒服的位置。可以坐着，可以躺着。轻轻地，闭上眼睛。",
                        "欢迎来到今天的冥想时间。让我们一起放下所有烦恼，回归当下。"
                    ],
                    "breathing_phrases": [
                        "深深地吸一口气...缓慢地...全部呼出...",
                        "感受空气进入身体...感受所有的紧绷...慢慢松开..."
                    ],
                    "affirmations": [
                        "你是安全的。",
                        "你值得被爱。",
                        "此刻，你已经很好。"
                    ]
                }
            },

            # ========== 爪爪博士模板 ==========
            "爪爪博士": {
                "行为解读": {
                    "duration": "40秒",
                    "structure": ["开场钩子", "要点讲解", "继续讲解", "总结互动"],
                    "hooks": [
                        "狗狗总舔你？它可不是在撒娇这么简单！",
                        "猫咪这个动作，是在说'我爱你'！",
                        "99%的人都忽略的宠物求救信号！"
                    ],
                    "topics": {
                        "dog": ["舔人", "摇尾巴", "打哈欠", "蹭人", "盯着看"],
                        "cat": ["咕噜声", "蹭腿", "尾巴抖动", "眯眼", "露肚子"]
                    },
                    "closing_phrases": [
                        "下次被舔/做出这个动作，记得分辨是什么意思哦！",
                        "想了解你家毛孩子？关注爪爪博士，一起读懂它们！"
                    ]
                },
                "搞笑集锦": {
                    "duration": "25秒",
                    "structure": ["铺垫", "测试过程", "反转", "结局彩蛋"],
                    "scenarios": [
                        "假装摔倒测试狗狗反应",
                        "给猫戴上喇叭会发生什么",
                        "第一次带狗狗去宠物店",
                        "用黄瓜测试猫咪..."
                    ],
                    "twist_endings": [
                        "它选择了...睡觉。",
                        "然后它给了我一个嫌弃的眼神。",
                        "结果出乎所有人的意料..."
                    ],
                    "closing_phrases": [
                        "你家毛孩子做过什么让你笑喷的事？评论区见！",
                        "关注爪爪博士，看更多毛孩子趣事！"
                    ]
                },
                "情感治愈": {
                    "duration": "45秒",
                    "structure": ["问题引入", "证据展示", "情感升华", "互动引导"],
                    "openers": [
                        "你有没有想过——你的毛孩子，每天都在爱你？",
                        "它们不会说话，但它们用一辈子，在爱着你。"
                    ],
                    "moments": [
                        "它会在你难过时，默默靠近你。",
                        "它会在你回家时，兴奋到发抖。",
                        "它会把自己的玩具叼给你。因为那是他最珍贵的东西。"
                    ],
                    "closings": [
                        "所以，请珍惜。这个选择信任你、陪伴你的小小生命。",
                        "你家的毛孩子，做过什么让你感动的事？来，一起晒晒我们的宝贝！"
                    ]
                },
                "知识科普": {
                    "duration": "40秒",
                    "structure": ["问题引入", "解答", "实操演示", "总结"],
                    "topics": [
                        ("狗狗这个动作，说明超级爱你", ["扑你", "靠着你", "舔你脸", "眼神追随"]),
                        ("猫咪尾巴的语言", ["竖直", "抖动", "炸毛", "夹在腿间"]),
                        ("新手养猫最易犯的错误", ["喂错食物", "忽略驱虫", "不及时绝育"])
                    ],
                    "closing_phrases": [
                        "觉得有用就收藏起来！",
                        "关注爪爪博士，每天学习一个宠物知识！"
                    ]
                }
            }
        }

    def generate_daily_script(self):
        """生成每日脚本"""
        # 随机选择IP和内容类型
        ip_name = random.choice(["禅心师姐", "爪爪博士"])
        content_types = list(self.templates[ip_name].keys())
        content_type = random.choice(content_types)

        script = {
            "id": f"SP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip_name": ip_name,
            "type": content_type,
            "template": self.templates[ip_name][content_type],
            "title": self.generate_title(ip_name, content_type),
            "outline": self.generate_outline(ip_name, content_type),
            "content": self.generate_content(ip_name, content_type),
            "hashtags": self.generate_hashtags(ip_name, content_type),
            "posting_config": self.get_posting_config(ip_name, content_type)
        }

        return script

    def generate_title(self, ip_name, content_type):
        """生成标题"""
        titles = {
            "禅心师姐": {
                "早安禅语": [
                    "早安｜当下，才是最好的答案",
                    "清晨的第一缕禅意，送给你",
                    "新的一天，从心开始"
                ],
                "知识科普": [
                    "痛苦的根源，逃不出这3个字",
                    "师父说：这5件事，做得越少命越好",
                    "修行人都在用的3个智慧"
                ],
                "故事分享": [
                    "峨眉山师父对我说的3句话",
                    "一位道长收徒的真实条件",
                    "师父私下的样子..."
                ],
                "冥想引导": [
                    "睡前10分钟，跟着我一起深度放松",
                    "清晨唤醒冥想",
                    "3分钟快速减压冥想"
                ]
            },
            "爪爪博士": {
                "行为解读": [
                    "狗狗舔你不是在撒娇！是在告诉你这5件事",
                    "猫咪这个动作，说明它超级爱你",
                    "读懂狗狗尾巴的语言"
                ],
                "搞笑集锦": [
                    "带猫咪做了3个智商测试，结果...",
                    "假装摔倒测试狗狗反应，笑喷了",
                    "给猫戴喇叭后它竟然..."
                ],
                "情感治愈": [
                    "原来我的猫一直在用它的方式爱我",
                    "抑郁那段时间，是猫咪救了我",
                    "毛孩子做过的最感动的事"
                ],
                "知识科普": [
                    "99%的人都忽略的宠物求救信号",
                    "这5个动作说明狗狗超级爱你",
                    "新手养猫最易犯的7个错误"
                ]
            }
        }
        return random.choice(titles.get(ip_name, {}).get(content_type, ["精彩内容"]))

    def generate_outline(self, ip_name, content_type):
        """生成大纲"""
        template = self.templates[ip_name][content_type]
        return template.get("structure", [])

    def generate_content(self, ip_name, content_type):
        """生成完整内容"""
        template = self.templates[ip_name][content_type]

        if ip_name == "禅心师姐":
            return self.generate_zen_content(template, content_type)
        else:
            return self.generate_paw_content(template, content_type)

    def generate_zen_content(self, template, content_type):
        """生成禅心师姐内容"""
        content = {}

        if content_type == "早安禅语":
            content["opening"] = random.choice(template["opening_phrases"])
            content["main"] = random.choice(template["zen_phrases"])
            content["closing"] = random.choice(template["closing_phrases"])
        elif content_type == "知识科普":
            content["hook"] = random.choice(template["hooks"])
            content["topic"] = random.choice(template["topics"])
            content["closing"] = random.choice(template["closing_phrases"])
        elif content_type == "故事分享":
            content["opener"] = random.choice(template["story_openers"])
            content["ending"] = random.choice(template["story_enders"])
        elif content_type == "冥想引导":
            content["intro"] = random.choice(template["intro_phrases"])
            content["breathing"] = random.choice(template["breathing_phrases"])
            content["affirmation"] = random.choice(template["affirmations"])

        return content

    def generate_paw_content(self, template, content_type):
        """生成爪爪博士内容"""
        content = {}

        if content_type == "行为解读":
            content["hook"] = random.choice(template["hooks"])
            topic_type = random.choice(["dog", "cat"])
            content["topic"] = random.choice(template["topics"][topic_type])
            content["closing"] = random.choice(template["closing_phrases"])
        elif content_type == "搞笑集锦":
            content["scenario"] = random.choice(template["scenarios"])
            content["twist"] = random.choice(template["twist_endings"])
            content["closing"] = random.choice(template["closing_phrases"])
        elif content_type == "情感治愈":
            content["opener"] = random.choice(template["openers"])
            content["moment"] = random.choice(template["moments"])
            content["closing"] = random.choice(template["closings"])
        elif content_type == "知识科普":
            topic = random.choice(template["topics"])
            content["question"] = topic[0]
            content["points"] = topic[1]
            content["closing"] = random.choice(template["closing_phrases"])

        return content

    def generate_hashtags(self, ip_name, content_type):
        """生成话题标签"""
        base_tags = {
            "禅心师姐": ["#禅心师姐", "#禅语", "#修行", "#正念", "#治愈系"],
            "爪爪博士": ["#爪爪博士", "#宠物", "#萌宠", "#铲屎官必看", "#毛孩子"]
        }

        niche_tags = {
            "禅心师姐": {
                "早安禅语": ["#早安", "#冥想", "#心灵成长", "#每日禅语"],
                "知识科普": ["#人生智慧", "#禅悟", "#自我提升", "#心灵疗愈"],
                "故事分享": ["#佛学", "#道家", "#传统文化", "#修行故事"],
                "冥想引导": ["#冥想", "#放松", "#解压", "#失眠", "#正念"]
            },
            "爪爪博士": {
                "行为解读": ["#狗狗行为", "#猫咪行为", "#宠物心理", "#养宠知识"],
                "搞笑集锦": ["#宠物搞笑", "#萌宠日常", "#宠物趣事", "#猫狗双全"],
                "情感治愈": ["#人宠关系", "#宠物情感", "#治愈", "#铲屎官日记"],
                "知识科普": ["#养宠技巧", "#宠物健康", "#新手养猫", "#养狗攻略"]
            }
        }

        tags = base_tags.get(ip_name, []) + niche_tags.get(ip_name, {}).get(content_type, [])

        # 添加日期标签
        import datetime
        tags.append(f"#{datetime.datetime.now().year}养生日记")

        return tags

    def get_posting_config(self, ip_name, content_type):
        """获取发布配置"""
        configs = {
            "禅心师姐": {
                "早安禅语": {"platforms": ["douyin", "tiktok", "youtube"], "time": "06:00"},
                "知识科普": {"platforms": ["douyin", "tiktok"], "time": "12:00"},
                "故事分享": {"platforms": ["douyin", "tiktok", "youtube"], "time": "21:00"},
                "冥想引导": {"platforms": ["douyin", "youtube", "xiaohongshu"], "time": "22:30"}
            },
            "爪爪博士": {
                "行为解读": {"platforms": ["douyin", "tiktok"], "time": "12:30"},
                "搞笑集锦": {"platforms": ["douyin", "tiktok", "youtube"], "time": "18:00"},
                "情感治愈": {"platforms": ["douyin", "tiktok"], "time": "21:00"},
                "知识科普": {"platforms": ["douyin", "tiktok", "youtube"], "time": "15:00"}
            }
        }
        return configs.get(ip_name, {}).get(content_type, {"platforms": ["douyin"], "time": "12:00"})

    def save_script(self, script):
        """保存脚本到文件"""
        import os
        from datetime import datetime

        scripts_dir = Path("outputs/scripts")
        scripts_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{script['ip_name']}_{script['type']}_{script['id']}.json"
        filepath = scripts_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)

        print(f"📝 脚本已保存: {filepath}")
        return str(filepath)

    def generate_batch(self, count=7):
        """批量生成脚本（一周量）"""
        scripts = []
        for _ in range(count):
            script = self.generate_daily_script()
            scripts.append(script)
            self.save_script(script)
        return scripts


if __name__ == "__main__":
    # 测试脚本生成
    generator = ScriptGenerator()

    print("=" * 50)
    print("🎬 AI 短视频脚本生成器 - 测试")
    print("=" * 50)

    # 生成单个脚本
    script = generator.generate_daily_script()
    print(f"\n📝 生成的脚本:")
    print(f"   ID: {script['id']}")
    print(f"   IP: {script['ip_name']}")
    print(f"   类型: {script['type']}")
    print(f"   标题: {script['title']}")
    print(f"   时长: {script['template']['duration']}")
    print(f"   标签: {' '.join(script['hashtags'][:5])}...")

    print("\n📋 内容预览:")
    for key, value in script['content'].items():
        print(f"   {key}: {value[:50] if isinstance(value, str) else value}...")

    # 批量生成一周脚本
    print("\n" + "=" * 50)
    print(f"📦 批量生成7条脚本...")
    print("=" * 50)

    weekly_scripts = generator.generate_batch(7)
    print(f"\n✅ 成功生成 {len(weekly_scripts)} 条脚本")
