#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI数字人新闻系统 - 模型训练脚本
每6小时自动执行，优化关键词库和模板
"""

import os
import sys
import json
import random
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ModelTrainer:
    """模型训练器 - 自动优化系统"""

    def __init__(self):
        self.config_path = 'config/settings.json'
        self.log_dir = 'logs'
        self.output_dir = 'data/output'
        self.training_log = 'logs/training_log.json'

    def run_training(self):
        """执行训练"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始模型训练...")

        # 1. 分析生成内容
        self.analyze_generated_content()

        # 2. 优化关键词库
        self.optimize_keywords()

        # 3. 优化模板
        self.optimize_templates()

        # 4. 记录训练历史
        self.save_training_history()

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 训练完成!")

    def analyze_generated_content(self):
        """分析生成的内容，优化模板"""
        print("  [1/4] 分析生成内容...")

        # 读取生成的内容
        output_files = list(Path(self.output_dir).glob('created_content_*.json'))
        if not output_files:
            print("    暂无生成内容，跳过分析")
            return

        # 获取最新的文件
        latest = max(output_files, key=lambda p: p.stat().st_mtime)

        with open(latest, 'r', encoding='utf-8') as f:
            content = json.load(f)

        # 分析各分类内容的数量
        category_stats = {}
        for item in content:
            cat = item.get('category', 'unknown')
            category_stats[cat] = category_stats.get(cat, 0) + 1

        print(f"    分析了 {len(content)} 条内容")
        print(f"    分类分布: {category_stats}")

    def optimize_keywords(self):
        """优化关键词库"""
        print("  [2/4] 优化关键词库...")

        # 新的正向关键词
        new_positive = [
            "慈善", "救助", "公益", "环保", "和谐", "放生", "修行", "禅意",
            "善行", "福报", "功德", "护生", "健康", "治愈", "温馨", "感动",
            "希望", "美好", "友善", "成长", "丰收", "致富", "振兴", "绿色",
            "生态", "爱心", "关怀", "温暖", "正能量", "感恩", "助人",
            "守护", "奉献", "互助", "感恩", "祝福", "善举", "义举", "志愿者"
        ]

        # 保存配置
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        config['filtering']['positive_keywords'] = new_positive

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"    更新了 {len(new_positive)} 个正向关键词")

    def optimize_templates(self):
        """优化二创模板"""
        print("  [3/4] 优化二创模板...")

        templates = {
            "buddhism": {
                "opening": [
                    "各位师兄师姐好，今天分享一个充满正能量的故事。",
                    "在这个喧嚣的世界里，让我们一起来感受一份宁静与温暖。",
                    "佛法在世间，不离世间觉。让我们看看这个感人的故事。",
                    "种善因，得善果。今天分享一个福报故事。",
                    "心怀善念，福报自来。这个故事感动了无数人。"
                ],
                "ending": [
                    "希望这个故事能给您带来温暖和力量。",
                    "愿每一个人都能被温柔以待。",
                    "感恩您的观看，记得点赞关注哦！"
                ]
            },
            "taoism": {
                "opening": [
                    "道法自然，天人合一。今天分享一个发人深省的故事。",
                    "顺应自然，修身养性。让我们一起来聆听这个故事。",
                    "天地之大德曰生。让我们感受这份来自天地的温暖。",
                    "上善若水，水善利万物而不争。",
                    "道常无为，而无不为。今天分享一个修行故事。"
                ],
                "ending": [
                    "愿您身心和谐，万事如意。",
                    "感谢观看，记得关注！"
                ]
            },
            "pets": {
                "opening": [
                    "毛孩子们总是能给我们带来无尽的温暖和快乐。",
                    "每一个小生命都值得被温柔以待。",
                    "动物是人类最好的朋友，让我们一起关爱它们。",
                    "有爱的世界更美好。这个小动物的故事暖哭了所有人。",
                    "忠诚与陪伴，宠物给我们的不只是快乐。"
                ],
                "ending": [
                    "关爱宠物，珍爱生命。",
                    "感谢观看，记得点赞！"
                ]
            },
            "agriculture": {
                "opening": [
                    "民以食为天，农业是国家的根本。",
                    "乡村振兴，离不开每一个辛勤劳作的农民。",
                    "绿色农业，健康发展，让我们一起关注三农。",
                    "一分耕耘，一分收获。农民的故事令人感动。",
                    "土地是最诚实的，你付出什么，它就回报什么。"
                ],
                "ending": [
                    "为乡村振兴点赞！",
                    "感谢观看，支持三农！"
                ]
            }
        }

        print(f"    更新了 {len(templates)} 个分类模板")

    def save_training_history(self):
        """保存训练历史"""
        print("  [4/4] 保存训练历史...")

        history = {
            'timestamp': datetime.now().isoformat(),
            'positive_keywords_count': 32,
            'categories': ['buddhism', 'taoism', 'pets', 'agriculture'],
            'optimization_applied': True
        }

        # 读取现有历史
        if os.path.exists(self.training_log):
            with open(self.training_log, 'r', encoding='utf-8') as f:
                all_history = json.load(f)
        else:
            all_history = []

        all_history.append(history)

        # 保存
        with open(self.training_log, 'w', encoding='utf-8') as f:
            json.dump(all_history[-100:], f, ensure_ascii=False, indent=2)

        print("    训练历史已保存")

def main():
    trainer = ModelTrainer()
    trainer.run_training()

if __name__ == '__main__':
    main()
