#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多平台自动分发模块
Multi-Platform Publisher Module
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.config_loader import get_config
from ..utils.logger import setup_logger


class PlatformPublisher:
    """多平台分发器"""

    def __init__(self):
        self.config = get_config()
        self.logger = setup_logger('publisher')
        self.douyin_config = self.config.get_section('publishing').get('douyin', {})
        self.youtube_config = self.config.get_section('publishing').get('youtube', {})

    def publish_all(
        self,
        videos: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        发布视频到所有平台

        Args:
            videos: 视频列表

        Returns:
            发布结果统计
        """
        results = {
            'total_videos': len(videos),
            'douyin': {'success': 0, 'failed': 0, 'details': []},
            'youtube': {'success': 0, 'failed': 0, 'details': []},
            'total_success': 0,
            'total_failed': 0
        }

        # 按平台分发
        if self.douyin_config.get('enabled', False):
            douyin_results = self._publish_douyin(videos)
            results['douyin'] = douyin_results

        if self.youtube_config.get('enabled', False):
            youtube_results = self._publish_youtube(videos)
            results['youtube'] = youtube_results

        results['total_success'] = (
            results['douyin']['success'] + results['youtube']['success']
        )
        results['total_failed'] = (
            results['douyin']['failed'] + results['youtube']['failed']
        )

        self._save_publish_results(results)
        return results

    def _publish_douyin(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        发布视频到抖音

        Args:
            videos: 视频列表

        Returns:
            发布结果
        """
        results = {'success': 0, 'failed': 0, 'details': []}

        # 只发布中文视频
        zh_videos = [v for v in videos if v.get('language') == 'zh']

        self.logger.info(f"开始发布 {len(zh_videos)} 个视频到抖音")

        for video in zh_videos:
            try:
                result = self._upload_to_douyin(video)
                results['details'].append(result)
                if result['status'] == 'success':
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                self.logger.error(f"抖音发布失败: {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'video_id': video.get('video_id'),
                    'status': 'failed',
                    'error': str(e)
                })

        self.logger.info(
            f"抖音发布完成: 成功 {results['success']}, 失败 {results['failed']}"
        )
        return results

    def _upload_to_douyin(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """
        上传单个视频到抖音

        Args:
            video: 视频信息

        Returns:
            上传结果
        """
        # 准备上传数据
        title = self._format_douyin_title(video.get('title', ''))
        tags = self._format_douyin_tags(video.get('tags', []))
        description = f"{title}\n\n{tags}"

        upload_data = {
            'video_path': video.get('video_path', ''),
            'title': title,
            'description': description,
            'category': self._map_category(video.get('category', 'general')),
            'visibility': 'public',
            'allow_comment': True,
            'allow_share': True
        }

        # 模拟API调用
        # 实际实现需要使用抖音开放平台API
        # https://open.douyin.com/

        cookie = self.douyin_config.get('cookie', '')
        if cookie and cookie != 'YOUR_DOUYIN_COOKIE':
            # 真实上传逻辑 (伪代码)
            # response = self._douyin_api_upload(upload_data)
            # return {'status': 'success', 'url': response.get('aweme_id')}
            pass

        # 模拟上传成功
        time.sleep(0.3)

        return {
            'video_id': video.get('video_id'),
            'platform': 'douyin',
            'status': 'success',
            'publish_url': f"https://www.douyin.com/video/simulated_{video.get('video_id')}",
            'publish_time': datetime.now().isoformat()
        }

    def _publish_youtube(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        发布视频到YouTube

        Args:
            videos: 视频列表

        Returns:
            发布结果
        """
        results = {'success': 0, 'failed': 0, 'details': []}

        # 只发布英文视频
        en_videos = [v for v in videos if v.get('language') == 'en']

        self.logger.info(f"开始发布 {len(en_videos)} 个视频到YouTube")

        for video in en_videos:
            try:
                result = self._upload_to_youtube(video)
                results['details'].append(result)
                if result['status'] == 'success':
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                self.logger.error(f"YouTube发布失败: {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'video_id': video.get('video_id'),
                    'status': 'failed',
                    'error': str(e)
                })

        self.logger.info(
            f"YouTube发布完成: 成功 {results['success']}, 失败 {results['failed']}"
        )
        return results

    def _upload_to_youtube(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """
        上传单个视频到YouTube

        Args:
            video: 视频信息

        Returns:
            上传结果
        """
        # 准备上传数据
        title = self._format_youtube_title(video.get('title', ''))
        description = self._format_youtube_description(video)

        upload_data = {
            'video_path': video.get('video_path', ''),
            'title': title,
            'description': description,
            'tags': self._format_youtube_tags(video),
            'category': '22',  # People & Blogs
            'privacy_status': 'public'
        }

        # 模拟API调用
        # 实际实现需要使用YouTube Data API v3
        # 需要OAuth2认证和client_secrets.json

        client_secrets = self.youtube_config.get('client_secrets', '')
        if client_secrets and os.path.exists(client_secrets):
            # 真实上传逻辑 (伪代码)
            # youtube = get_authenticated_service()
            # response = youtube.videos().insert(
            #     part="snippet,status",
            #     body={
            #         "snippet": {...},
            #         "status": {"privacyStatus": "public"}
            #     },
            #     media_body=MediaFileUpload(video_path)
            # ).execute()
            pass

        # 模拟上传成功
        time.sleep(0.3)

        return {
            'video_id': video.get('video_id'),
            'platform': 'youtube',
            'status': 'success',
            'video_id_youtube': f"simulated_{video.get('video_id')}",
            'publish_url': f"https://www.youtube.com/watch?v=simulated_{video.get('video_id')}",
            'publish_time': datetime.now().isoformat()
        }

    def _format_douyin_title(self, title: str) -> str:
        """
        格式化抖音标题 (最多55字符)

        Args:
            title: 原始标题

        Returns:
            格式化后的标题
        """
        # 抖音标题限制
        max_length = 55
        if len(title) > max_length:
            return title[:max_length - 3] + '...'
        return title

    def _format_douyin_tags(self, tags: List[str]) -> str:
        """
        格式化抖音标签

        Args:
            tags: 标签列表

        Returns:
            格式化后的标签字符串
        """
        # 选择前5个标签
        selected_tags = tags[:5]
        return ' '.join(selected_tags)

    def _format_youtube_title(self, title: str) -> str:
        """
        格式化YouTube标题 (最多100字符)

        Args:
            title: 原始标题

        Returns:
            格式化后的标题
        """
        max_length = 100
        if len(title) > max_length:
            return title[:max_length - 3] + '...'
        return title

    def _format_youtube_description(self, video: Dict[str, Any]) -> str:
        """
        格式化YouTube视频描述

        Args:
            video: 视频信息

        Returns:
            格式化后的描述
        """
        description_parts = [
            "Thank you for watching!",
            "",
            "In this video, we share inspiring stories about:",
            "",
            f"Category: {video.get('category', 'general').title()}",
            "",
            "Tags:",
            ", ".join(video.get('tags', [])),
            "",
            "Subscribe for more positive and heartwarming content!",
            "",
            "#positiveenergy #inspiring #heartwarming #dailystories"
        ]

        return "\n".join(description_parts)

    def _format_youtube_tags(self, video: Dict[str, Any]) -> List[str]:
        """
        格式化YouTube标签

        Args:
            video: 视频信息

        Returns:
            标签列表 (最多500字符)
        """
        tags = video.get('tags', [])

        # 添加默认标签
        default_tags = ['positive', 'inspiring', 'heartwarming', 'good news']
        all_tags = tags + default_tags

        # 去重
        unique_tags = list(dict.fromkeys(all_tags))

        # 确保总长度不超过500字符
        selected_tags = []
        total_length = 0

        for tag in unique_tags:
            tag_length = len(tag) + 1  # +1 for comma
            if total_length + tag_length <= 500:
                selected_tags.append(tag)
                total_length += tag_length
            else:
                break

        return selected_tags

    def _map_category(self, category: str) -> str:
        """
        映射分类到平台分类ID

        Args:
            category: 内部分类

        Returns:
            平台分类ID
        """
        douyin_category_map = {
            'buddhism': '60000',  # 文化
            'taoism': '60000',    # 文化
            'pets': '150000',    # 宠物
            'agriculture': '160000',  # 三农
            'general': '60000'   # 通用 -> 文化
        }
        return douyin_category_map.get(category, '60000')

    def _save_publish_results(self, results: Dict[str, Any]) -> None:
        """
        保存发布结果

        Args:
            results: 发布结果
        """
        output_dir = self.config.get('paths.output', 'data/output')
        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.join(
            output_dir,
            f"publish_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        self.logger.info(f"发布结果已保存: {filename}")

    def get_publish_status(self, video_id: str) -> Dict[str, Any]:
        """
        获取视频发布状态

        Args:
            video_id: 视频ID

        Returns:
            发布状态
        """
        # 实际实现应查询数据库或API
        return {
            'video_id': video_id,
            'douyin': {'status': 'published', 'url': ''},
            'youtube': {'status': 'published', 'url': ''}
        }
