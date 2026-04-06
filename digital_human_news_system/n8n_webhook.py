#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
n8n Webhook API 服務器
N8N Webhook API Server
支持 n8n 触发的自动化工作流
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config_loader import get_config
from src.utils.logger import setup_logger


class WebhookHandler(BaseHTTPRequestHandler):
    """Webhook请求处理器"""

    logger = None

    def log_message(self, format, *args):
        """重写日志方法"""
        if self.logger:
            self.logger.info(f"{self.client_address[0]} - {format % args}")
        else:
            super().log_message(format, *args)

    def send_json_response(self, status_code: int, data: Dict[str, Any]):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == '/health':
            self.send_json_response(200, {
                'status': 'healthy',
                'service': 'digital-human-news-system',
                'version': '1.0.0'
            })

        elif path == '/status':
            self.send_json_response(200, {
                'status': 'ready',
                'endpoints': [
                    'POST /webhook/trigger - 触发完整流程',
                    'POST /webhook/fetch - 抓取新闻',
                    'POST /webhook/create - AI二创',
                    'POST /webhook/generate - 生成视频',
                    'POST /webhook/publish - 发布视频',
                    'GET /status - 系统状态',
                    'GET /health - 健康检查'
                ]
            })

        elif path == '/webhook/live-start':
            self._handle_live_start(query)
        elif path == '/webhook/live-stop':
            self._handle_live_stop(query)
        elif path == '/webhook/live-status':
            self._handle_live_status(query)
        elif path == '/webhook/live-content':
            self._handle_live_content(query)
        else:
            self.send_json_response(404, {'error': 'Not found'})

    def do_POST(self):
        """处理POST请求"""
        parsed = urlparse(self.path)
        path = parsed.path

        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        query = parse_qs(body.decode('utf-8')) if body else {}

        # 设置CORS头
        self.send_header('Access-Control-Allow-Origin', '*')

        if path == '/webhook/trigger':
            self._handle_trigger(query)
        elif path == '/webhook/fetch':
            self._handle_fetch(query)
        elif path == '/webhook/create':
            self._handle_create(query)
        elif path == '/webhook/generate':
            self._handle_generate(query)
        elif path == '/webhook/publish':
            self._handle_publish(query)
        elif path == '/webhook/status':
            self._handle_status(query)
        else:
            self.send_json_response(404, {'error': 'Not found'})

    def _handle_trigger(self, query: Dict[str, list]):
        """触发完整工作流"""
        try:
            # 延迟导入避免循环依赖
            from main import NewsSystem

            self.logger.info("n8n触发完整工作流")

            # 在新线程中执行，不阻塞webhook响应
            def run_workflow():
                try:
                    system = NewsSystem()
                    result = system.run()
                    self.logger.info(f"工作流执行完成: {result['status']}")
                except Exception as e:
                    self.logger.error(f"工作流执行失败: {str(e)}")

            thread = threading.Thread(target=run_workflow)
            thread.start()

            self.send_json_response(200, {
                'success': True,
                'message': '工作流已触发，正在异步执行',
                'status': 'running',
                'webhook_id': f"wh_{int(__import__('time').time())}"
            })

        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def _handle_fetch(self, query: Dict[str, list]):
        """抓取新闻"""
        try:
            from src.news.news_fetcher import NewsFetcher

            self.logger.info("n8n触发新闻抓取")
            fetcher = NewsFetcher()
            news = fetcher.fetch_all_sources()

            self.send_json_response(200, {
                'success': True,
                'action': 'fetch',
                'count': len(news),
                'data': news[:10]  # 返回前10条预览
            })

        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def _handle_create(self, query: Dict[str, list]):
        """AI二创"""
        try:
            from src.news.news_fetcher import NewsFetcher
            from src.filter.content_filter import ContentFilter
            from src.creator.ai_creator import AICreator

            self.logger.info("n8n触发AI二创")

            # 获取已处理的新闻
            fetcher = NewsFetcher()
            news = fetcher.fetch_all_sources()
            news = fetcher.deduplicate(news)

            filter_module = ContentFilter()
            filter_result = filter_module.process(news)
            passed_news = filter_result['passed']

            creator = AICreator()
            content = creator.create_content(passed_news)

            self.send_json_response(200, {
                'success': True,
                'action': 'create',
                'input_count': len(passed_news),
                'output_count': len(content),
                'data': content[:5]  # 返回前5条预览
            })

        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def _handle_generate(self, query: Dict[str, list]):
        """生成视频"""
        try:
            from src.news.news_fetcher import NewsFetcher
            from src.filter.content_filter import ContentFilter
            from src.creator.ai_creator import AICreator
            from src.human.digital_human import DigitalHumanGenerator

            self.logger.info("n8n触发视频生成")

            # 完整流程获取内容
            fetcher = NewsFetcher()
            news = fetcher.deduplicate(fetcher.fetch_all_sources())

            filter_module = ContentFilter()
            passed_news = filter_module.process(news)['passed']

            creator = AICreator()
            content = creator.create_content(passed_news)

            # 生成视频
            generator = DigitalHumanGenerator()
            videos = generator.generate_videos(content)

            self.send_json_response(200, {
                'success': True,
                'action': 'generate',
                'videos_created': len(videos),
                'data': [{'video_id': v.get('video_id'), 'title': v.get('title')} for v in videos[:5]]
            })

        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def _handle_publish(self, query: Dict[str, list]):
        """发布视频"""
        try:
            from src.news.news_fetcher import NewsFetcher
            from src.filter.content_filter import ContentFilter
            from src.creator.ai_creator import AICreator
            from src.human.digital_human import DigitalHumanGenerator
            from src.publisher.publisher import PlatformPublisher

            self.logger.info("n8n触发视频发布")

            # 完整流程
            fetcher = NewsFetcher()
            news = fetcher.deduplicate(fetcher.fetch_all_sources())

            filter_module = ContentFilter()
            passed_news = filter_module.process(news)['passed']

            creator = AICreator()
            content = creator.create_content(passed_news)

            generator = DigitalHumanGenerator()
            videos = generator.generate_videos(content)

            # 发布
            publisher = PlatformPublisher()
            results = publisher.publish_all(videos)

            self.send_json_response(200, {
                'success': True,
                'action': 'publish',
                'total_videos': results['total_videos'],
                'published': results['total_success'],
                'failed': results['total_failed'],
                'douyin': results['douyin'],
                'youtube': results['youtube']
            })

        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def _handle_status(self, query: Dict[str, list]):
        """获取状态"""
        self.send_json_response(200, {
            'status': 'ready',
            'service': 'digital-human-news-system-n8n',
            'version': '1.0.0'
        })

    def _handle_live_start(self, query: Dict[str, list]):
        """开始直播"""
        try:
            from src.live.live_streamer import LiveStreamer

            self.logger.info("n8n触发开始直播")

            platform = query.get('platform', ['douyin'])[0] if isinstance(query.get('platform'), list) else 'douyin'
            title = query.get('title', ['正能量故事分享'])[0] if isinstance(query.get('title'), list) else '正能量故事分享'

            streamer = LiveStreamer()
            result = streamer.start_live(platform=platform, title=title)

            self.send_json_response(200, {
                'success': result.get('success', False),
                'platform': result.get('platform'),
                'title': result.get('title'),
                'start_time': result.get('start_time'),
                'stream_url': result.get('stream_url')
            })

        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def _handle_live_stop(self, query: Dict[str, list]):
        """停止直播"""
        try:
            from src.live.live_streamer import LiveStreamer

            self.logger.info("n8n触发停止直播")

            streamer = LiveStreamer()
            result = streamer.stop_live()

            self.send_json_response(200, result)

        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def _handle_live_status(self, query: Dict[str, list]):
        """获取直播状态"""
        try:
            from src.live.live_streamer import LiveStreamer

            streamer = LiveStreamer()
            stats = streamer.get_stats()

            self.send_json_response(200, {
                'success': True,
                'is_live': stats.get('is_live', False),
                'stats': stats
            })

        except Exception as e:
            self.send_json_response(500, {'error': str(e)})

    def _handle_live_content(self, query: Dict[str, list]):
        """获取直播内容"""
        try:
            from src.live.live_streamer import LiveStreamer

            streamer = LiveStreamer()
            content = streamer._prepare_content()

            self.send_json_response(200, {
                'success': True,
                'content': content
            })

        except Exception as e:
            self.send_json_response(500, {'error': str(e)})


def run_server(host: str = '0.0.0.0', port: int = 8080):
    """运行Webhook服务器"""
    server = HTTPServer((host, port), WebhookHandler)
    print(f"🌐 n8n Webhook服务器启动")
    print(f"   地址: http://{host}:{port}")
    print(f"   端点:")
    print(f"   === 视频流程 ===")
    print(f"   - POST /webhook/trigger   触发完整流程")
    print(f"   - POST /webhook/fetch    抓取新闻")
    print(f"   - POST /webhook/create   AI二创")
    print(f"   - POST /webhook/generate 生成视频")
    print(f"   - POST /webhook/publish  发布视频")
    print(f"   === 直播 ===")
    print(f"   - POST /webhook/live-start   开始直播")
    print(f"   - POST /webhook/live-stop    停止直播")
    print(f"   - POST /webhook/live-status 获取直播状态")
    print(f"   - POST /webhook/live-content 获取直播内容")
    print(f"   === 系统 ===")
    print(f"   - GET  /health    健康检查")
    print(f"   - GET  /status   系统状态")
    print(f"\n按 Ctrl+C 停止服务器\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(description='n8n Webhook API服务器')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=8080, help='监听端口')
    args = parser.parse_args()

    # 设置日志
    logger = setup_logger('n8n_webhook')
    WebhookHandler.logger = logger

    run_server(args.host, args.port)


if __name__ == '__main__':
    main()
