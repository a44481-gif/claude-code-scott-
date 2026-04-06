"""
Douyin Agent - 主執行器
"""
import asyncio
import json
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger


class DouyinAPI:
    """抖音開放平台 API 客戶端"""

    def __init__(self, config: Dict):
        self.config = config
        self.client_id = config.get("client_id", "")
        self.client_secret = config.get("client_secret", "")
        self.access_token = None

    async def get_access_token(self) -> Optional[str]:
        """獲取 access token"""
        if self.access_token:
            return self.access_token

        url = "https://open.douyin.com/oauth/client_token"
        data = {
            "client_key": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credential",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(url, data=data)
                result = resp.json()
                if result.get("errno") == 0:
                    self.access_token = result["data"]["access_token"]
                    return self.access_token
        except Exception as e:
            logger.error(f"獲取抖音 access_token 失敗: {e}")
        return None

    async def get_user_info(self, open_id: str) -> Optional[Dict]:
        """獲取用戶信息"""
        token = await self.get_access_token()
        if not token:
            return None

        url = f"https://open.douyin.com/oauth/userinfo"
        params = {"access_token": token, "open_id": open_id}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, params=params)
                return resp.json()
        except Exception as e:
            logger.error(f"獲取抖音用戶信息失敗: {e}")
        return None

    async def get_video_list(self, open_id: str, count: int = 20) -> List[Dict]:
        """獲取視頻列表"""
        token = await self.get_access_token()
        if not token:
            return []

        url = "https://open.douyin.com/video/data"
        params = {"access_token": token, "open_id": open_id, "count": count}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, params=params)
                data = resp.json()
                if data.get("errno") == 0:
                    return data.get("data", {}).get("video_list", [])
        except Exception as e:
            logger.error(f"獲取抖音視頻列表失敗: {e}")
        return []


class TikTokAPI:
    """TikTok for Business API 客戶端"""

    def __init__(self, config: Dict):
        self.config = config
        self.access_token = config.get("tiktok_access_token", "")

    async def get_ad_metrics(self, advertiser_id: str) -> Optional[Dict]:
        """獲取廣告指標"""
        url = "https://business-api.tiktok.com/portal/api"
        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json",
        }
        data = {
            "advertiser_id": advertiser_id,
            "page": 1,
            "page_size": 20,
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(url, headers=headers, json=data)
                return resp.json()
        except Exception as e:
            logger.error(f"獲取 TikTok 指標失敗: {e}")
        return None


class DouyinAgent:
    """Douyin Agent 主執行器"""

    def __init__(self, cfg: Dict):
        self.cfg = cfg
        self.today_str = datetime.now().strftime("%Y%m%d")
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.reports_dir = self.base_dir / "reports"
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        self.douyin = DouyinAPI(cfg.get("douyin", {}))
        self.tiktok = TikTokAPI(cfg.get("tiktok", {}))

    async def collect_metrics(self) -> Dict:
        """收集所有平台指標"""
        logger.info("收集社交媒體指標...")
        metrics = {
            "date": self.today_str,
            "platforms": {},
            "collected_at": datetime.now().isoformat(),
        }

        # Douyin
        douyin_cfg = self.cfg.get("douyin", {})
        if douyin_cfg.get("enabled") and douyin_cfg.get("client_id"):
            open_id = douyin_cfg.get("open_id", "")
            videos = await self.douyin.get_video_list(open_id)
            metrics["platforms"]["douyin"] = {
                "video_count": len(videos),
                "videos": videos[:10],
            }

        # TikTok
        tiktok_cfg = self.cfg.get("tiktok", {})
        if tiktok_cfg.get("enabled"):
            adv_id = tiktok_cfg.get("advertiser_id", "")
            data = await self.tiktok.get_ad_metrics(adv_id)
            metrics["platforms"]["tiktok"] = data or {}

        # Save
        path = self.data_dir / f"social_metrics_{self.today_str}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

        logger.info(f"指標收集完成: {path}")
        return metrics

    async def post_scheduled(self) -> Dict:
        """發布排程中的內容"""
        logger.info("檢查排程發布...")
        schedule_file = self.data_dir / "content_schedule.json"
        if not schedule_file.exists():
            return {"status": "no_schedule", "posted": 0}

        with open(schedule_file) as f:
            schedule = json.load(f)

        now = datetime.now()
        posted = []

        for post in schedule.get("posts", []):
            scheduled = datetime.fromisoformat(post.get("scheduled_at", ""))
            if scheduled <= now and post.get("status") == "scheduled":
                # Simulate posting
                logger.info(f"發布: {post.get('title', '')}")
                post["status"] = "posted"
                post["posted_at"] = now.isoformat()
                posted.append(post)

        if posted:
            with open(schedule_file, "w") as f:
                json.dump(schedule, f, ensure_ascii=False, indent=2)

        return {"status": "completed", "posted": len(posted)}

    def get_dashboard_data(self) -> Dict:
        """獲取儀表板數據"""
        # Aggregate recent metrics
        metric_files = sorted(self.data_dir.glob("social_metrics_*.json"))[-7:]
        all_metrics = []

        for f in metric_files:
            with open(f) as fp:
                all_metrics.append(json.load(fp))

        return {
            "date_range": f"{self.today_str} (近 {len(all_metrics)} 天)",
            "daily_metrics": all_metrics,
            "summary": {
                "avg_views": self._calc_avg(all_metrics, "views"),
                "avg_likes": self._calc_avg(all_metrics, "likes"),
                "total_posts": len(all_metrics),
            }
        }

    def _calc_avg(self, metrics: List[Dict], field: str) -> float:
        vals = []
        for m in metrics:
            for platform_data in m.get("platforms", {}).values():
                if isinstance(platform_data, dict) and field in platform_data:
                    v = platform_data[field]
                    if isinstance(v, (int, float)):
                        vals.append(v)
        return round(sum(vals) / len(vals), 2) if vals else 0
