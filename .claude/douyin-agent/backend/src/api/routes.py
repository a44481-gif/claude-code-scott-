"""
FastAPI routes for Douyin Agent Backend
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["douyin"])


class PostCreate(BaseModel):
    title: str
    content: str
    platform: str
    tags: List[str] = []
    scheduled_at: str = ""


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "douyin-agent"}


@router.get("/metrics")
def get_metrics(executor) -> Dict:
    return executor.get_dashboard_data()


@router.get("/metrics/{platform}")
def get_platform_metrics(platform: str, executor) -> Dict:
    return {"platform": platform, "status": "ok"}


@router.post("/posts")
def create_post(post: PostCreate, executor) -> Dict:
    """創建排程帖子"""
    return {"status": "created", "post_id": "post_001"}


@router.get("/posts")
def list_posts() -> List[Dict]:
    """列出所有帖子"""
    return []


@router.get("/schedule")
def get_schedule() -> Dict:
    """獲取排程"""
    return {"posts": []}
