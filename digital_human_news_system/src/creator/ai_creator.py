#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI二创模块
AI Content Creator Module
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import random

from ..utils.config_loader import get_config
from ..utils.logger import setup_logger


class AICreator:
    """AI二创内容生成器"""

    def __init__(self):
        self.config = get_config()
        self.logger = setup_logger('ai_creator')
        self.max_videos = self.config.get('ai_creation.max_videos_per_day', 10)
        self.languages = self.config.get('ai_creation.languages', ['zh', 'en'])
        self.template_styles = self.config.get('ai_creation.template_styles', ['warm'])

    def create_content(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        为新闻列表生成二创内容

        Args:
            news_list: 通过筛选的新闻列表

        Returns:
            二创内容列表
        """
        created_content = []
        news_list = news_list[:self.max_videos]  # 限制每日生成数量

        self.logger.info(f"开始生成二创内容，共 {len(news_list)} 条新闻")

        for news in news_list:
            try:
                # 为每种语言生成内容
                for lang in self.languages:
                    content = self._generate_script(news, lang)
                    if content:
                        created_content.append(content)

            except Exception as e:
                self.logger.error(f"生成内容失败: {str(e)}")
                continue

        self._save_created_content(created_content)
        return created_content

    def _generate_script(self, news: Dict[str, Any], language: str) -> Optional[Dict[str, Any]]:
        """
        生成单条二创脚本

        Args:
            news: 原始新闻
            language: 语言代码

        Returns:
            二创内容
        """
        category = news.get('category', 'general')
        summary = news.get('content', '')[:100]

        if language == 'zh':
            return self._generate_chinese_script(news, summary)
        elif language == 'en':
            return self._generate_english_script(news, summary)
        else:
            return None

    def _generate_chinese_script(self, news: Dict[str, Any], summary: str) -> Dict[str, Any]:
        """
        生成中文二创脚本

        Args:
            news: 新闻数据
            summary: 摘要

        Returns:
            中文二创内容
        """
        category = news.get('category', 'general')

        # 分类开场白模板
        opening_templates = {
            'buddhism': [
                "各位师兄师姐好，今天分享一个充满正能量的故事。",
                "在这个喧嚣的世界里，让我们一起来感受一份宁静与温暖。",
                "佛法在世间，不离世间觉。让我们看看这个感人的故事。"
            ],
            'taoism': [
                "道法自然，天人合一。今天分享一个发人深省的故事。",
                "顺应自然，修身养性。让我们一起来聆听这个故事。",
                "天地之大德曰生。让我们感受这份来自天地的温暖。"
            ],
            'pets': [
                "毛孩子们总是能给我们带来无尽的温暖和快乐。",
                "每一个小生命都值得被温柔以待。",
                "动物是人类最好的朋友，让我们一起关爱它们。"
            ],
            'agriculture': [
                "民以食为天，农业是国家的根本。",
                "乡村振兴，离不开每一个辛勤劳作的农民。",
                "绿色农业，健康发展，让我们一起关注三农。"
            ],
            'general': [
                "生活中总有一些温暖的瞬间让我们感动。",
                "今天，让我们一起感受这份正能量。",
                "平凡生活中，也有不平凡的感动。"
            ]
        }

        # 结尾模板
        ending_templates = [
            "希望这个故事能给您带来温暖和力量。",
            "让我们一起传递正能量，让世界更美好。",
            "感谢您的观看，记得点赞关注哦！",
            "愿每一个人都能被温柔以待，世界因你而美好。"
        ]

        # 分类标签
        category_tags = {
            'buddhism': ['#佛教 #正能量 #慈善 #修行 #心灵成长'],
            'taoism': ['#道教 #传统文化 #养生 #道法自然 #修身养性'],
            'pets': ['#宠物 #流浪动物 #动物救助 #爱心 #萌宠'],
            'agriculture': ['#三农 #乡村振兴 #绿色农业 #农民增收'],
            'general': ['#正能量 #温暖 #感人故事 #生活感悟']
        }

        opening = random.choice(opening_templates.get(category, opening_templates['general']))
        ending = random.choice(ending_templates)
        tags = category_tags.get(category, category_tags['general'])

        # 生成标题
        title = self._generate_title(news, language)

        # 生成字幕脚本
        script = f"{opening}\n\n{summary}\n\n{ending}"

        return {
            'id': hashlib.md5(f"{news.get('id', '')}{language}".encode()).hexdigest(),
            'original_id': news.get('id', ''),
            'category': category,
            'language': language,
            'title': title,
            'script': script,
            'tags': tags,
            'video_duration': random.randint(45, 90),  # 45-90秒
            'style': random.choice(self.template_styles),
            'created_at': datetime.now().isoformat()
        }

    def _generate_english_script(self, news: Dict[str, Any], summary: str) -> Dict[str, Any]:
        """
        生成英文二创脚本

        Args:
            news: 新闻数据
            summary: 摘要

        Returns:
            英文二创内容
        """
        category = news.get('category', 'general')

        # 英文开场白
        opening_templates = {
            'buddhism': [
                "Dear friends, today I want to share an inspiring story of compassion.",
                "In this busy world, let's take a moment to feel the warmth and kindness.",
                "Buddhism teaches us to find enlightenment in everyday life."
            ],
            'taoism': [
                "The Tao follows nature. Today, let's explore a thought-provoking story.",
                "Harmony with nature brings peace. Let's listen to this beautiful story.",
                "The journey of a thousand miles begins with a single step."
            ],
            'pets': [
                "Our furry friends always bring us joy and unconditional love.",
                "Every small life deserves love and care.",
                "Animals are humans' best companions. Let's spread love for them."
            ],
            'agriculture': [
                "Agriculture is the foundation of our society.",
                "Rural revitalization brings hope to communities.",
                "Green agriculture leads to sustainable development."
            ],
            'general': [
                "Life is full of warm moments that touch our hearts.",
                "Today, let's be inspired by this positive story.",
                "Even ordinary life holds extraordinary moments."
            ]
        }

        ending_templates = [
            "I hope this story brings warmth and strength to your day.",
            "Let's spread positivity and make the world a better place.",
            "Thank you for watching! Like and subscribe for more inspiring content!",
            "May you be blessed with kindness and love."
        ]

        category_tags = {
            'buddhism': ['#Buddhism #Compassion #PositiveEnergy #SpiritualGrowth'],
            'taoism': ['#Taoism #TraditionalCulture #Wellness #NaturalHarmony'],
            'pets': ['#Pets #AnimalRescue #LoveAnimals #CutePets'],
            'agriculture': ['#Agriculture #RuralRevitalization #SustainableFarming'],
            'general': ['#PositiveEnergy #Heartwarming #InspiringStory']
        }

        opening = random.choice(opening_templates.get(category, opening_templates['general']))
        ending = random.choice(ending_templates)
        tags = category_tags.get(category, category_tags['general'])

        title = self._generate_title(news, language)
        script = f"{opening}\n\n{summary}\n\n{ending}"

        return {
            'id': hashlib.md5(f"{news.get('id', '')}{language}".encode()).hexdigest(),
            'original_id': news.get('id', ''),
            'category': category,
            'language': language,
            'title': title,
            'script': script,
            'tags': tags,
            'video_duration': random.randint(45, 90),
            'style': random.choice(self.template_styles),
            'created_at': datetime.now().isoformat()
        }

    def _generate_title(self, news: Dict[str, Any], language: str) -> str:
        """
        生成视频标题

        Args:
            news: 新闻数据
            language: 语言

        Returns:
            标题
        """
        original_title = news.get('title', '')

        if language == 'zh':
            title_prefixes = ['太暖心了！', '感人至深！', '正能量满满！', '看哭了！', '转发给需要的人！']
            prefix = random.choice(title_prefixes)
            return f"{prefix}{original_title}"

        else:  # English
            title_prefixes = [
                "Heartwarming! ",
                "So Touching! ",
                "Full of Positivity! ",
                "You Need to See This! ",
                "Share with Everyone! "
            ]
            prefix = random.choice(title_prefixes)
            return f"{prefix}{original_title}"

    def _save_created_content(self, content_list: List[Dict[str, Any]]) -> None:
        """
        保存生成的二创内容

        Args:
            content_list: 内容列表
        """
        output_dir = self.config.get('paths.output', 'data/output')
        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.join(
            output_dir,
            f"created_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(content_list, f, ensure_ascii=False, indent=2)

        self.logger.info(f"二创内容已保存: {filename}")
