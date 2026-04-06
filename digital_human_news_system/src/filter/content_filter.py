#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
内容筛选与处理模块
Content Filter Module
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple

from ..utils.config_loader import get_config
from ..utils.logger import setup_logger


class ContentFilter:
    """内容过滤器 - 负责筛选、去重、情感分析"""

    def __init__(self):
        self.config = get_config()
        self.logger = setup_logger('content_filter')
        self.positive_keywords = self.config.get(
            'filtering.positive_keywords', []
        )
        self.negative_keywords = self.config.get(
            'filtering.negative_keywords', []
        )
        self.min_length = self.config.get('filtering.min_content_length', 50)
        self.max_length = self.config.get('filtering.max_content_length', 2000)

    def process(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        处理新闻列表

        Args:
            news_list: 原始新闻列表

        Returns:
            处理结果，包含各类统计数据
        """
        results = {
            'total_input': len(news_list),
            'passed': [],
            'filtered': [],
            'statistics': {}
        }

        for news in news_list:
            # 检查是否通过筛选
            passed, reason = self._check_news(news)

            if passed:
                results['passed'].append(news)
            else:
                news['filter_reason'] = reason
                results['filtered'].append(news)

        # 统计各分类通过率
        results['statistics'] = self._generate_statistics(results)
        self._save_processed_data(results)

        return results

    def _check_news(self, news: Dict[str, Any]) -> Tuple[bool, str]:
        """
        检查单条新闻是否通过筛选

        Args:
            news: 新闻数据

        Returns:
            (是否通过, 原因)
        """
        title = news.get('title', '')
        content = news.get('content', '')
        full_text = title + content

        # 1. 长度检查
        if len(content) < self.min_length:
            return False, f"内容过短 ({len(content)} < {self.min_length})"
        if len(content) > self.max_length:
            return False, f"内容过长 ({len(content)} > {self.max_length})"

        # 2. 负面关键词过滤
        for neg_word in self.negative_keywords:
            if neg_word in full_text:
                return False, f"包含负面词汇: {neg_word}"

        # 3. 正面关键词匹配 (至少包含一个)
        has_positive = any(pos_word in full_text for pos_word in self.positive_keywords)

        # 如果没有正面词汇，检查是否为正向内容
        if not has_positive:
            # 额外的正向内容判断逻辑
            if not self._is_positive_content(full_text):
                return False, "不属于正向内容范畴"

        return True, "通过"

    def _is_positive_content(self, text: str) -> bool:
        """
        判断内容是否为正向

        Args:
            text: 文本内容

        Returns:
            是否为正向内容
        """
        # 正向指标词
        positive_indicators = [
            '帮助', '关爱', '温暖', '希望', '美好', '幸福',
            '和谐', '友善', '成长', '发展', '进步', '成功',
            '健康', '爱心', '善举', '奉献', '责任', '担当'
        ]

        # 计算正向词出现次数
        positive_count = sum(1 for word in positive_indicators if word in text)

        # 至少包含2个正向词
        return positive_count >= 2

    def classify_category(self, news: Dict[str, Any]) -> str:
        """
        对新闻进行赛道分类

        Args:
            news: 新闻数据

        Returns:
            分类名称
        """
        title = news.get('title', '')
        content = news.get('content', '')
        full_text = title + content

        category_keywords = {
            'buddhism': ['佛', '禅', '寺', '僧', '经', '法', '放生', '修行', '福报', '功德'],
            'taoism': ['道', '道教', '道观', '道士', '仙', '太极', '养生', '阴阳', '五行'],
            'pets': ['宠物', '猫', '狗', '动物', '救助', '收养', '导盲犬', '流浪'],
            'agriculture': ['农业', '农村', '农民', '种植', '养殖', '丰收', '乡村', '振兴']
        }

        scores = {}
        for category, keywords in category_keywords.items():
            scores[category] = sum(1 for kw in keywords if kw in full_text)

        # 返回得分最高的分类
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return news.get('category', 'general')

    def summarize(self, news: Dict[str, Any], max_length: int = 100) -> str:
        """
        生成新闻摘要

        Args:
            news: 新闻数据
            max_length: 最大长度

        Returns:
            摘要文本
        """
        content = news.get('content', '')

        # 简单摘要策略：取前N个字符
        if len(content) <= max_length:
            return content

        # 在句号或逗号处截断
        for i in range(max_length, len(content)):
            if content[i] in '。！？':
                return content[:i+1]

        return content[:max_length] + '...'

    def _generate_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成统计数据

        Args:
            results: 处理结果

        Returns:
            统计信息
        """
        passed = results['passed']

        # 按分类统计
        category_stats = {}
        for news in passed:
            cat = news.get('category', 'unknown')
            category_stats[cat] = category_stats.get(cat, 0) + 1

        return {
            'total_input': results['total_input'],
            'total_passed': len(passed),
            'total_filtered': len(results['filtered']),
            'pass_rate': f"{len(passed)/results['total_input']*100:.1f}%" if results['total_input'] > 0 else "0%",
            'category_distribution': category_stats,
            'process_time': datetime.now().isoformat()
        }

    def _save_processed_data(self, results: Dict[str, Any]) -> None:
        """
        保存处理后的数据

        Args:
            results: 处理结果
        """
        processed_dir = self.config.get('paths.processed_data', 'data/processed')
        os.makedirs(processed_dir, exist_ok=True)

        filename = os.path.join(
            processed_dir,
            f"processed_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        self.logger.info(f"处理后数据已保存: {filename}")
