#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直播視頻批量生成腳本
生成一批預渲染視頻用於直播
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.news.news_fetcher import NewsFetcher
from src.filter.content_filter import ContentFilter
from src.creator.ai_creator import AICreator
from src.human.digital_human import DigitalHumanGenerator


def generate_live_videos(count=5):
    """
    生成直播用視頻

    Args:
        count: 生成數量
    """
    print("=" * 50)
    print("  直播視頻批量生成")
    print("=" * 50)
    print()

    # 1. 抓取新聞
    print("[1/4] 抓取新聞...")
    fetcher = NewsFetcher()
    news = fetcher.deduplicate(fetcher.fetch_all_sources())
    print(f"    抓取 {len(news)} 條新聞")

    # 2. 篩選
    print("[2/4] 內容篩選...")
    filter_module = ContentFilter()
    passed = filter_module.process(news)['passed']
    print(f"    通過 {len(passed)} 條")

    if not passed:
        print("    無通過內容，使用模擬數據")
        passed = news[:count] if news else []

    # 3. AI二創
    print("[3/4] AI二創...")
    creator = AICreator()
    content = creator.create_content(passed[:count])
    print(f"    生成 {len(content)} 條腳本")

    # 4. 生成視頻
    print("[4/4] 生成視頻...")
    generator = DigitalHumanGenerator()
    videos = generator.generate_videos(content)
    print(f"    生成 {len(videos)} 個視頻")

    # 保存視頻列表
    video_list_path = 'data/output/live_videos.json'
    os.makedirs('data/output', exist_ok=True)

    video_list = [{
        'title': v.get('title'),
        'path': v.get('video_path'),
        'duration': v.get('video_duration'),
        'category': v.get('category'),
        'language': v.get('language')
    } for v in videos]

    with open(video_list_path, 'w', encoding='utf-8') as f:
        json.dump(video_list, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 50)
    print(f"  完成！生成 {len(videos)} 個直播視頻")
    print(f"  列表保存: {video_list_path}")
    print("=" * 50)

    return videos


def generate_live_playlist():
    """生成直播播放列表"""
    print("\n生成直播播放列表...")

    playlist = {
        'created': datetime.now().isoformat(),
        'segments': [
            {
                'id': 1,
                'type': 'greeting',
                'title': '開場問候',
                'duration': 120,
                'category': 'general'
            },
            {
                'id': 2,
                'type': 'story',
                'title': '正能量故事1',
                'duration': 600,
                'category': 'buddhism'
            },
            {
                'id': 3,
                'type': 'story',
                'title': '正能量故事2',
                'duration': 600,
                'category': 'pets'
            },
            {
                'id': 4,
                'type': 'interaction',
                'title': '觀眾互動',
                'duration': 180,
                'category': 'general'
            },
            {
                'id': 5,
                'type': 'story',
                'title': '正能量故事3',
                'duration': 600,
                'category': 'agriculture'
            },
            {
                'id': 6,
                'type': 'story',
                'title': '正能量故事4',
                'duration': 600,
                'category': 'taoism'
            },
            {
                'id': 7,
                'type': 'ending',
                'title': '結尾感謝',
                'duration': 120,
                'category': 'general'
            }
        ],
        'total_duration': 2820  # 47分鐘
    }

    playlist_path = 'data/output/live_playlist.json'
    with open(playlist_path, 'w', encoding='utf-8') as f:
        json.dump(playlist, f, ensure_ascii=False, indent=2)

    print(f"播放列表保存: {playlist_path}")
    return playlist


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='直播視頻生成')
    parser.add_argument('-c', '--count', type=int, default=5, help='生成數量')
    args = parser.parse_args()

    generate_live_videos(args.count)
    generate_live_playlist()
