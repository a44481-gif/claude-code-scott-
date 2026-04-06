#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
新闻抓取模块
News Fetcher Module
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    requests = None

from ..utils.config_loader import get_config
from ..utils.logger import setup_logger


class NewsFetcher:
    """新闻抓取器"""

    def __init__(self):
        self.config = get_config()
        self.logger = setup_logger('news_fetcher')
        self.session = None
        self.seen_hashes = set()  # 用于去重

        if requests:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

    def fetch_all_sources(self) -> List[Dict[str, Any]]:
        """
        抓取所有新闻源

        Returns:
            抓取的新闻列表
        """
        all_news = []
        sources = self.config.get('news_sources', {})

        for category, urls in sources.items():
            self.logger.info(f"正在抓取分类: {category}")
            for url in urls:
                try:
                    news_list = self.fetch_source(url, category)
                    all_news.extend(news_list)
                    self.logger.info(f"从 {url} 抓取到 {len(news_list)} 条新闻")
                except Exception as e:
                    self.logger.error(f"抓取 {url} 失败: {str(e)}")

        # 保存原始数据
        self._save_raw_data(all_news)
        return all_news

    def fetch_source(self, url: str, category: str) -> List[Dict[str, Any]]:
        """
        抓取单个新闻源

        Args:
            url: 新闻源URL
            category: 分类

        Returns:
            新闻列表
        """
        if not self.session:
            # 如果没有requests库，返回模拟数据用于测试
            return self._generate_mock_news(category, 5)

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'

            # 解析HTML获取新闻 (简化版，实际需要BeautifulSoup)
            news_list = self._parse_html(response.text, url, category)

            return news_list

        except Exception as e:
            self.logger.warning(f"抓取失败，使用模拟数据: {str(e)}")
            return self._generate_mock_news(category, 5)

    def _parse_html(self, html: str, base_url: str, category: str) -> List[Dict[str, Any]]:
        """
        解析HTML提取新闻 (需要BeautifulSoup，这里是简化版)

        Args:
            html: HTML内容
            base_url: 基础URL
            category: 分类

        Returns:
            解析的新闻列表
        """
        # 简化实现：实际项目中应使用BeautifulSoup
        # 这里返回模拟数据，实际需要根据具体网站结构解析
        return self._generate_mock_news(category, 3)

    def _generate_mock_news(self, category: str, count: int) -> List[Dict[str, Any]]:
        """
        生成模拟新闻数据 (用于测试)

        Args:
            category: 分类
            count: 生成数量

        Returns:
            模拟新闻列表
        """
        mock_templates = {
            'buddhism': [
                {'title': '寺庙开展慈善救助活动，帮助困难群众', 'content': '近日，某寺庙组织慈善救助活动，为困难群众送去生活物资和慰问金，传递社会正能量。'},
                {'title': '禅修体验营开课，帮助城市人群减压', 'content': '禅修体验营在山寺开课，吸引众多城市人群参与，通过禅修帮助人们舒缓压力，找回内心平静。'},
                {'title': '佛教慈善基金会捐资助学', 'content': '佛教慈善基金会向贫困地区学校捐赠教学设备，帮助更多孩子接受教育。'},
            ],
            'taoism': [
                {'title': '道观举办公益讲座，传承道教文化', 'content': '道观举办道教文化公益讲座，吸引众多文化爱好者参与，传承中华优秀传统文化。'},
                {'title': '道教协会开展敬老慰问活动', 'content': '道教协会组织志愿者前往养老院开展慰问活动，为老人们送去温暖和祝福。'},
                {'title': '武当山道士传授养生功法', 'content': '武当山道士向游客和信众传授传统养生功法，倡导健康生活方式。'},
            ],
            'pets': [
                {'title': '流浪动物救助中心收容流浪宠物', 'content': '爱心人士建立的流浪动物救助中心本月收容了50只流浪猫狗，为它们寻找温暖的家。'},
                {'title': '宠物义诊活动进社区', 'content': '宠物医院开展义诊活动，为社区居民的宠物提供免费体检和健康咨询。'},
                {'title': '导盲犬培训基地培养助盲犬', 'content': '导盲犬培训基地成功培养一批助盲犬，帮助视障人士更好地融入社会。'},
            ],
            'agriculture': [
                {'title': '乡村振兴项目带动农民增收', 'content': '某地实施乡村振兴项目，通过发展特色农业，带动当地农民年均增收30%。'},
                {'title': '农业专家指导农户科学种养', 'content': '农业技术专家深入田间地头，指导农户科学种养，提高农作物产量和品质。'},
                {'title': '绿色有机蔬菜走进城市餐桌', 'content': '偏远山区的绿色有机蔬菜通过电商平台销往全国各地，既丰富了城市餐桌，又带动了山区农户致富。'},
            ],
            'general': [
                {'title': '志愿者开展社区服务活动', 'content': '社区志愿者开展各类服务活动，为居民提供便利，传递爱心与温暖。'},
                {'title': '环保组织发起绿色出行倡议', 'content': '环保组织发起绿色出行倡议，呼吁更多人选择公共交通或骑行，共同保护环境。'},
            ],
        }

        templates = mock_templates.get(category, mock_templates['general'])
        news_list = []

        for i in range(count):
            template = templates[i % len(templates)]
            news_id = hashlib.md5(f"{category}{i}{datetime.now()}".encode()).hexdigest()

            news = {
                'id': news_id,
                'title': template['title'],
                'content': template['content'],
                'category': category,
                'source_url': f'https://example.com/news/{news_id}',
                'fetch_time': datetime.now().isoformat(),
                'language': 'zh'
            }
            news_list.append(news)

        return news_list

    def _save_raw_data(self, news_list: List[Dict[str, Any]]) -> None:
        """
        保存原始新闻数据

        Args:
            news_list: 新闻列表
        """
        raw_dir = self.config.get('paths.raw_data', 'data/raw')
        os.makedirs(raw_dir, exist_ok=True)

        filename = os.path.join(
            raw_dir,
            f"raw_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)

        self.logger.info(f"原始数据已保存: {filename}")

    def deduplicate(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        新闻去重

        Args:
            news_list: 原始新闻列表

        Returns:
            去重后的新闻列表
        """
        deduplicated = []
        seen_content = set()

        for news in news_list:
            # 使用内容哈希进行去重
            content_hash = hashlib.md5(
                (news.get('title', '') + news.get('content', '')).encode()
            ).hexdigest()

            if content_hash not in seen_content:
                seen_content.add(content_hash)
                deduplicated.append(news)

        removed_count = len(news_list) - len(deduplicated)
        if removed_count > 0:
            self.logger.info(f"去重完成，移除了 {removed_count} 条重复新闻")

        return deduplicated
