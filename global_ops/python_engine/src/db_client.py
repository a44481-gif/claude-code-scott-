"""
GlobalOPS · 数据库客户端
统一的 PostgreSQL 操作接口
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from .config import DB_CONFIG

logger = logging.getLogger("GlobalOPS.DB")


class DBClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conn = None
        return cls._instance

    def __init__(self):
        if self._conn is None:
            self._connect()

    def _connect(self):
        try:
            self._conn = psycopg2.connect(**DB_CONFIG)
            self._conn.autocommit = False
            logger.info("✅ 数据库连接成功")
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise

    @property
    def conn(self):
        if self._conn is None or self._conn.closed:
            self._connect()
        return self._conn

    def commit(self):
        self.conn.commit()

    def close(self):
        if self._conn and not self._conn.closed:
            self._conn.close()

    # ===== 内容库操作 =====

    def get_pending_content(self, limit: int = 10, theme: str = None, region: str = None) -> list[dict]:
        """获取待处理内容"""
        sql = """
            SELECT * FROM content_items
            WHERE status IN ('generated', 'pending')
        """
        params = []
        if theme:
            sql += " AND theme_type = %s"
            params.append(theme)
        if region:
            sql += " AND target_region = %s"
            params.append(region)
        sql += " ORDER BY priority DESC, created_at ASC LIMIT %s"
        params.append(limit)

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]

    def get_content_by_id(self, content_id: str) -> Optional[dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM content_items WHERE content_id = %s", (content_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def update_content_status(self, content_id: str, status: str, **kwargs):
        """更新内容状态及附加字段"""
        fields = ["status = %s"]
        values = [status]
        for k, v in kwargs.items():
            fields.append(f"{k} = %s")
            values.append(v)
        values.append(content_id)
        sql = f"UPDATE content_items SET {', '.join(fields)} WHERE content_id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, values)
        self.commit()

    def insert_content(self, data: dict) -> str:
        """插入新内容，返回 content_id"""
        cols = list(data.keys())
        vals = list(data.values())
        placeholders = ["%s"] * len(cols)
        sql = f"INSERT INTO content_items ({','.join(cols)}) VALUES ({','.join(placeholders)}) ON CONFLICT (content_id) DO UPDATE SET updated_at=NOW()"
        with self.conn.cursor() as cur:
            cur.execute(sql, vals)
        self.commit()
        return data.get("content_id", "")

    def get_content_stats(self) -> dict:
        """获取内容库统计"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT status, COUNT(*) as count
                FROM content_items GROUP BY status
            """)
            statuses = {r["status"]: r["count"] for r in cur.fetchall()}

            cur.execute("SELECT theme_type, COUNT(*) as count FROM content_items GROUP BY theme_type")
            themes = {r["theme_type"]: r["count"] for r in cur.fetchall()}

            return {"by_status": statuses, "by_theme": themes}

    # ===== 发布记录操作 =====

    def log_publish(self, data: dict) -> int:
        sql = """
            INSERT INTO publish_log (
                content_id, platform, account_id, account_name,
                video_url, video_id, title, description, tags_applied,
                scheduled_at, published_at, status, views_24h, views_7d,
                views_total, likes, comments_count, shares, revenue, cpm, error_message
            ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            ) RETURNING id
        """
        defaults = {
            "content_id": None, "platform": None, "account_id": None, "account_name": None,
            "video_url": None, "video_id": None, "title": None, "description": None,
            "tags_applied": None, "scheduled_at": None, "published_at": None,
            "status": "scheduled", "views_24h": 0, "views_7d": 0, "views_total": 0,
            "likes": 0, "comments_count": 0, "shares": 0, "revenue": 0, "cpm": 0,
            "error_message": None
        }
        for k, v in defaults.items():
            data.setdefault(k, v)
        tags = data.get("tags_applied")
        if isinstance(tags, list):
            data["tags_applied"] = Json(tags)

        with self.conn.cursor() as cur:
            cur.execute(sql, [
                data.get("content_id"), data.get("platform"), data.get("account_id"),
                data.get("account_name"), data.get("video_url"), data.get("video_id"),
                data.get("title"), data.get("description"), data.get("tags_applied"),
                data.get("scheduled_at"), data.get("published_at"), data.get("status"),
                data.get("views_24h", 0), data.get("views_7d", 0), data.get("views_total", 0),
                data.get("likes", 0), data.get("comments_count", 0), data.get("shares", 0),
                data.get("revenue", 0), data.get("cpm", 0), data.get("error_message")
            ])
            return_id = cur.fetchone()[0]
        self.commit()
        return return_id

    def get_publish_log(self, platform: str = None, limit: int = 50) -> list[dict]:
        sql = "SELECT * FROM publish_log"
        params = []
        if platform:
            sql += " WHERE platform = %s"
            params.append(platform)
        sql += " ORDER BY published_at DESC LIMIT %s"
        params.append(limit)
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]

    # ===== 账号矩阵操作 =====

    def get_available_account(self, platform: str, region: str = None) -> Optional[dict]:
        sql = """
            SELECT * FROM platform_accounts
            WHERE platform = %s AND status = 'active'
        """
        params = [platform]
        if region:
            sql += " AND (region = %s OR region = 'global')"
            params.append(region)
        sql += " ORDER BY last_upload_at ASC NULLS FIRST LIMIT 1"
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None

    def update_account_upload(self, account_id: str):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE platform_accounts
                SET total_uploads = total_uploads + 1,
                    last_upload_at = %s,
                    updated_at = %s
                WHERE account_id = %s
            """, (datetime.now(), datetime.now(), account_id))
        self.commit()

    def insert_account(self, data: dict) -> str:
        cols = list(data.keys())
        vals = list(data.values())
        placeholders = ["%s"] * len(cols)
        sql = f"INSERT INTO platform_accounts ({','.join(cols)}) VALUES ({','.join(placeholders)})"
        if data.get("account_id"):
            sql += " ON CONFLICT (account_id) DO UPDATE SET updated_at=NOW()"
        with self.conn.cursor() as cur:
            cur.execute(sql, vals)
        self.commit()
        return data.get("account_id", "")

    # ===== 调度任务操作 =====

    def create_task(self, task_type: str, scheduled_time: datetime, content_id: str = None,
                    platform: str = None, account_id: str = None, params: dict = None,
                    priority: int = 5) -> str:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO scheduled_tasks
                (task_type, content_id, platform, account_id, scheduled_time, priority, params)
                VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING task_uuid
            """, (task_type, content_id, platform, account_id, scheduled_time, priority, Json(params or {})))
            uuid = cur.fetchone()[0]
        self.commit()
        return uuid

    def get_due_tasks(self, task_type: str = None, limit: int = 20) -> list[dict]:
        sql = """
            SELECT * FROM scheduled_tasks
            WHERE status = 'pending'
              AND scheduled_time <= %s
        """
        params = [datetime.now()]
        if task_type:
            sql += " AND task_type = %s"
            params.append(task_type)
        sql += " ORDER BY priority ASC, scheduled_time ASC LIMIT %s"
        params.append(limit)
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]

    def update_task_status(self, task_uuid: str, status: str, result: dict = None, error: str = None):
        update_fields = ["status = %s"]
        values = [status]
        if status == "running":
            update_fields.append("started_at = %s")
            values.append(datetime.now())
        elif status in ("completed", "failed"):
            update_fields.append("completed_at = %s")
            values.append(datetime.now())
        if result:
            update_fields.append("result = %s")
            values.append(Json(result))
        if error:
            update_fields.append("error_message = %s")
            values.append(error)
            update_fields.append("retry_count = retry_count + 1")
        values.append(task_uuid)
        sql = f"UPDATE scheduled_tasks SET {', '.join(update_fields)} WHERE task_uuid = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, values)
        self.commit()

    # ===== 收益操作 =====

    def log_revenue(self, date: str, platform: str, gross: float, revenue_type: str,
                    account_id: str = None, content_id: str = None,
                    currency: str = "USD", estimated: bool = False) -> int:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO daily_revenue
                (date, platform, account_id, content_id, gross_revenue, net_revenue, currency, revenue_type, estimated)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
            """, (date, platform, account_id, content_id, gross, gross * 0.7, currency, revenue_type, estimated))
            return_id = cur.fetchone()[0]
        self.commit()
        return return_id

    def get_revenue_summary(self, days: int = 30) -> dict:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT platform, SUM(gross_revenue) as total, SUM(net_revenue) as net
                FROM daily_revenue
                WHERE date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY platform
            """, (days,))
            by_platform = {r["platform"]: {"total": float(r["total"] or 0), "net": float(r["net"] or 0)}
                           for r in cur.fetchall()}

            cur.execute("""
                SELECT SUM(gross_revenue) as total, SUM(net_revenue) as net
                FROM daily_revenue
                WHERE date >= CURRENT_DATE - INTERVAL '%s days'
            """, (days,))
            row = cur.fetchone()
            return {
                "total_gross": float(row["total"] or 0),
                "total_net": float(row["net"] or 0),
                "by_platform": by_platform
            }

    # ===== 每日统计 =====

    def upsert_daily_stats(self, date: str, stats: dict):
        sql = """
            INSERT INTO daily_stats (date, total_videos_published, total_views, total_likes,
                                      total_comments, total_revenue, new_subscribers, platform_breakdown)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (date) DO UPDATE SET
                total_videos_published = EXCLUDED.total_videos_published,
                total_views = EXCLUDED.total_views,
                total_likes = EXCLUDED.total_likes,
                total_comments = EXCLUDED.total_comments,
                total_revenue = EXCLUDED.total_revenue,
                new_subscribers = EXCLUDED.new_subscribers,
                platform_breakdown = EXCLUDED.platform_breakdown,
                updated_at = NOW()
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, [
                date,
                stats.get("total_videos_published", 0),
                stats.get("total_views", 0),
                stats.get("total_likes", 0),
                stats.get("total_comments", 0),
                stats.get("total_revenue", 0),
                stats.get("new_subscribers", 0),
                Json(stats.get("platform_breakdown", {}))
            ])
        self.commit()
