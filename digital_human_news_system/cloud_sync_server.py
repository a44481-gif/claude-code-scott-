#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地结果接收服务器
接收云端推送的结果并存储
"""

import os
import sys
import json
import hmac
import hashlib
import sqlite3
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# 项目根目录
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)


class LocalDB:
    """本地SQLite数据库"""

    def __init__(self):
        self.db_path = os.path.join(PROJECT_DIR, 'data', 'cloud_sync.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sync_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    result_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    processed_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    news_fetched INTEGER DEFAULT 0,
                    content_created INTEGER DEFAULT 0,
                    videos_generated INTEGER DEFAULT 0,
                    errors TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS content_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    script TEXT,
                    category TEXT,
                    language TEXT,
                    tags TEXT,
                    status TEXT DEFAULT 'pending',
                    source TEXT,
                    received_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def save_result(self, source: str, result_type: str, data: dict) -> int:
        """保存结果"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                '''INSERT INTO sync_results (source, result_type, data, received_at)
                   VALUES (?, ?, ?, ?)''',
                (source, result_type, json.dumps(data, ensure_ascii=False),
                 datetime.now().isoformat())
            )
            return cursor.lastrowid

    def save_content(self, content: dict, source: str = 'cloud') -> int:
        """保存内容到队列"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                '''INSERT INTO content_queue (title, script, category, language, tags, source)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (content.get('title'), content.get('script'),
                 content.get('category'), content.get('language'),
                 json.dumps(content.get('tags', []), ensure_ascii=False),
                 source)
            )
            return cursor.lastrowid

    def update_stats(self, news_count: int = None, content_count: int = None,
                     video_count: int = None, errors: str = None):
        """更新每日统计"""
        today = datetime.now().strftime('%Y-%m-%d')

        with sqlite3.connect(self.db_path) as conn:
            # 先尝试更新
            conn.execute(f'''
                INSERT INTO daily_stats (date, news_fetched, content_created, videos_generated, errors, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    updated_at = excluded.updated_at,
                    news_fetched = COALESCE(excluded.news_fetched, news_fetched),
                    content_created = COALESCE(excluded.content_created, content_created),
                    videos_generated = COALESCE(excluded.videos_generated, videos_generated)
            ''', (today, news_count or 0, content_count or 0,
                  video_count or 0, errors, datetime.now().isoformat()))

    def get_pending_content(self, limit: int = 10):
        """获取待处理内容"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                '''SELECT * FROM content_queue
                   WHERE status = 'pending'
                   ORDER BY received_at DESC
                   LIMIT ?''',
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def mark_processed(self, content_id: int):
        """标记为已处理"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                '''UPDATE content_queue SET status = 'processed' WHERE id = ?''',
                (content_id,)
            )

    def get_today_stats(self):
        """获取今日统计"""
        today = datetime.now().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                '''SELECT * FROM daily_stats WHERE date = ?''', (today,)
            )
            return dict(cursor.fetchone()) if cursor.fetchone() else None

    def get_all_stats(self, days: int = 7):
        """获取多日统计"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                '''SELECT * FROM daily_stats
                   ORDER BY date DESC LIMIT ?''', (days,)
            )
            return [dict(row) for row in cursor.fetchall()]


class WebhookHandler(BaseHTTPRequestHandler):
    """Webhook处理器"""

    db = LocalDB()
    webhook_secret = "your_webhook_secret_key"  # 配置密钥

    def log_message(self, format, *args):
        """日志"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

    def verify_signature(self) -> bool:
        """验证签名"""
        signature = self.headers.get('X-Signature', '')
        if not signature:
            return True  # 开发模式跳过验证

        expected = hmac.new(
            self.webhook_secret.encode(),
            self.rfile.read(int(self.headers.get('Content-Length', 0))),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, f"sha256={expected}")

    def send_json(self, status: int, data: dict):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_OPTIONS(self):
        """CORS预检"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Signature')
        self.end_headers()

    def do_GET(self):
        """GET请求"""
        parsed = urlparse(self.path)

        if parsed.path == '/health':
            self.send_json(200, {'status': 'healthy', 'service': 'local-sync-server'})

        elif parsed.path == '/stats':
            stats = self.db.get_today_stats()
            self.send_json(200, stats or {'message': 'No data today'})

        elif parsed.path == '/pending':
            pending = self.db.get_pending_content()
            self.send_json(200, {'count': len(pending), 'items': pending})

        elif parsed.path == '/all-stats':
            stats = self.db.get_all_stats()
            self.send_json(200, {'stats': stats})

        else:
            self.send_json(404, {'error': 'Not found'})

    def do_POST(self):
        """POST请求 - 接收云端数据"""
        parsed = urlparse(self.path)

        if parsed.path == '/webhook/cloud-result':
            self._handle_cloud_result()
        elif parsed.path == '/webhook/content':
            self._handle_content()
        elif parsed.path == '/webhook/stats':
            self._handle_stats()
        else:
            self.send_json(404, {'error': 'Not found'})

    def _handle_cloud_result(self):
        """处理云端结果"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            # 保存到数据库
            result_id = self.db.save_result(
                source=data.get('source', 'unknown'),
                result_type=data.get('type', 'unknown'),
                data=data.get('data', {})
            )

            self.log_message(f"收到云端结果: {data.get('type')} - ID: {result_id}")

            self.send_json(200, {
                'success': True,
                'id': result_id,
                'message': 'Result saved'
            })

        except Exception as e:
            self.send_json(500, {'error': str(e)})

    def _handle_content(self):
        """处理云端内容"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            # 保存内容
            if isinstance(data, list):
                for item in data:
                    self.db.save_content(item, source='cloud')
                count = len(data)
            else:
                self.db.save_content(data, source='cloud')
                count = 1

            self.log_message(f"收到云端内容: {count} 条")

            self.send_json(200, {
                'success': True,
                'count': count,
                'message': f'{count} content saved'
            })

        except Exception as e:
            self.send_json(500, {'error': str(e)})

    def _handle_stats(self):
        """处理云端统计"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            self.db.update_stats(
                news_count=data.get('news_fetched'),
                content_count=data.get('content_created'),
                video_count=data.get('videos_generated'),
                errors=data.get('errors')
            )

            self.log_message(f"更新统计: 新闻{data.get('news_fetched',0)} 内容{data.get('content_created',0)} 视频{data.get('videos_generated',0)}")

            self.send_json(200, {'success': True, 'message': 'Stats updated'})

        except Exception as e:
            self.send_json(500, {'error': str(e)})


def run_server(host: str = '0.0.0.0', port: int = 8081):
    """启动本地服务器"""
    server = HTTPServer((host, port), WebhookHandler)
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         本地结果接收服务器                                 ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    print(f"  地址: http://{host}:{port}")
    print()
    print("  端点:")
    print("  ├── POST /webhook/cloud-result  接收云端结果")
    print("  ├── POST /webhook/content       接收云端内容")
    print("  ├── POST /webhook/stats        接收云端统计")
    print("  ├── GET  /health               健康检查")
    print("  ├── GET  /stats                今日统计")
    print("  ├── GET  /pending              待处理内容")
    print("  └── GET  /all-stats            多日统计")
    print()
    print(f"  数据库: {WebhookHandler.db.db_path}")
    print()
    print("  按 Ctrl+C 停止服务器")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='本地结果接收服务器')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=8081, help='监听端口')
    args = parser.parse_args()
    run_server(args.host, args.port)
