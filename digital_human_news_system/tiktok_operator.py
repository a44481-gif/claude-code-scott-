#!/usr/bin env python
# -*- coding: utf-8 -*-
"""
抖音內容自動化運營腳本
每日生成並準備發布內容
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TikTokContentOperator:
    """抖音內容運營器"""

    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.project_dir, 'data', 'output', 'tiktok')
        self.content_file = os.path.join(self.output_dir, 'daily_content.json')
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_daily_content(self, count=5):
        """生成每日內容"""
        print("=" * 50)
        print("  抖音內容自動生成")
        print("=" * 50)
        print()

        # 導入模組
        from src.news.news_fetcher import NewsFetcher
        from src.filter.content_filter import ContentFilter
        from src.creator.ai_creator import AICreator

        print("[1/4] 抓取新聞...")
        fetcher = NewsFetcher()
        news = fetcher.deduplicate(fetcher.fetch_all_sources())
        print(f"    抓取 {len(news)} 條新聞")

        print("[2/4] 內容篩選...")
        filter_module = ContentFilter()
        passed = filter_module.process(news)['passed']
        print(f"    通過 {len(passed)} 條")

        print("[3/4] AI二創...")
        creator = AICreator()
        content = creator.create_content(passed[:count])
        print(f"    生成 {len(content)} 條腳本")

        print("[4/4] 生成發布內容...")
        publish_content = self._prepare_publish_content(content)

        # 保存
        with open(self.content_file, 'w', encoding='utf-8') as f:
            json.dump(publish_content, f, ensure_ascii=False, indent=2)

        print()
        print("=" * 50)
        print(f"  完成！生成 {len(publish_content)} 條發布內容")
        print(f"  保存位置: {self.content_file}")
        print("=" * 50)

        return publish_content

    def _prepare_publish_content(self, content_list):
        """準備發布內容"""
        publish_list = []
        current_hour = datetime.now().hour

        for i, item in enumerate(content_list):
            # 根據時間段分配內容類型
            if 6 <= current_hour < 12:
                time_slot = "morning"
                greeting = "各位師兄師姐早上好！"
            elif 12 <= current_hour < 18:
                time_slot = "afternoon"
                greeting = "午安時光，分享一個故事..."
            elif 18 <= current_hour < 22:
                time_slot = "evening"
                greeting = "晚上好，來聽一個溫暖的故事..."
            else:
                time_slot = "night"
                greeting = "夜深了，來聽一段禪語..."

            category = item.get('category', 'general')
            category_names = {
                'buddhism': '佛學正能量',
                'taoism': '道教養生',
                'pets': '寵物暖心',
                'agriculture': '三農勵志',
                'general': '正能量'
            }

            publish_item = {
                'id': item.get('id', f'content_{i}'),
                'time_slot': time_slot,
                'platform': 'douyin',
                'title': item.get('title', ''),
                'script': item.get('script', ''),
                'category': category,
                'category_name': category_names.get(category, '正能量'),
                'tags': item.get('tags', []),
                'greeting': greeting,
                'hashtags': self._generate_hashtags(category, time_slot),
                'publish_time': self._get_publish_time(time_slot),
                'video_path': item.get('video_path', ''),
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            publish_list.append(publish_item)

        return publish_list

    def _generate_hashtags(self, category, time_slot):
        """生成標籤"""
        base_tags = {
            'buddhism': ['#佛學', '#正能量', '#禪意', '#心靈成長', '#修行'],
            'taoism': ['#道教', '#養生', '#道法自然', '#傳統文化', '#修身養性'],
            'pets': ['#寵物', '#暖心', '#動物救助', '#萌寵', '#愛護動物'],
            'agriculture': ['#三農', '#鄉村振興', '#農業', '#農民', '#正能量'],
            'general': ['#正能量', '#暖心', '#故事', '#感人', '#分享']
        }

        time_tags = {
            'morning': ['#早安', '#早安正能量', '#新的一天'],
            'afternoon': ['#午安', '#午間時光', '#下午好'],
            'evening': ['#晚安', '#晚間故事', '#正能量滿滿'],
            'night': ['#夜深了', '#禪語', '#心靈語錄']
        }

        tags = base_tags.get(category, base_tags['general'])
        tags.extend(time_tags.get(time_slot, []))

        return list(set(tags))[:10]  # 最多10個標籤

    def _get_publish_time(self, time_slot):
        """獲取發布時間"""
        times = {
            'morning': '06:30',
            'afternoon': '12:30',
            'evening': '18:30',
            'night': '21:00'
        }
        return times.get(time_slot, '12:00')

    def show_daily_content(self):
        """顯示今日內容"""
        if not os.path.exists(self.content_file):
            print("今日內容未生成，先運行生成任務")
            return

        with open(self.content_file, 'r', encoding='utf-8') as f:
            content = json.load(f)

        print()
        print("=" * 60)
        print("  今日發布內容計劃")
        print("=" * 60)

        for i, item in enumerate(content, 1):
            print(f"\n【第 {i} 條】")
            print(f"  時間: {item['publish_time']}")
            print(f"  類型: {item['category_name']}")
            print(f"  標題: {item['title']}")
            print(f"  標籤: {' '.join(item['hashtags'][:5])}")
            print(f"  狀態: {item['status']}")

        print()
        print("=" * 60)

    def mark_as_published(self, content_id):
        """標記為已發布"""
        if not os.path.exists(self.content_file):
            return False

        with open(self.content_file, 'r', encoding='utf-8') as f:
            content = json.load(f)

        for item in content:
            if item['id'] == content_id:
                item['status'] = 'published'
                item['published_at'] = datetime.now().isoformat()

        with open(self.content_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

        return True

    def get_pending_content(self):
        """獲取待發布內容"""
        if not os.path.exists(self.content_file):
            return []

        with open(self.content_file, 'r', encoding='utf-8') as f:
            content = json.load(f)

        return [item for item in content if item['status'] == 'pending']


def main():
    operator = TikTokContentOperator()

    print()
    print("╔═══════════════════════════════════════════════════════╗")
    print("║          抖音 AI 數字人內容運營系統                    ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()
    print("1. 生成今日內容")
    print("2. 查看今日內容")
    print("3. 獲取待發布內容")
    print("0. 退出")
    print()

    while True:
        choice = input("請選擇: ").strip()

        if choice == '1':
            operator.generate_daily_content(5)

        elif choice == '2':
            operator.show_daily_content()

        elif choice == '3':
            pending = operator.get_pending_content()
            print(f"\n待發布內容: {len(pending)} 條")
            for item in pending:
                print(f"  - {item['publish_time']} | {item['title']}")

        elif choice == '0':
            print("再見！")
            break


if __name__ == '__main__':
    main()
