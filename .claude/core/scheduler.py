"""
Task Scheduler - APScheduler wrapper.
Based on health_food_agent/scheduling/scheduler.py.
"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from typing import Callable, Optional, Dict, Any


class TaskScheduler:
    """任务调度器 - APScheduler wrapper"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self.tasks: Dict[str, Callable] = {}

    def add_daily_task(
        self,
        task_id: str,
        func: Callable,
        hour: int = 8,
        minute: int = 0,
    ):
        """添加每日任务"""
        trigger = CronTrigger(hour=hour, minute=minute, timezone="Asia/Shanghai")
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
            misfire_grace_time=3600,
        )
        logger.info(f"已添加每日任务 [{task_id}]: {hour:02d}:{minute:02d}")

    def add_weekly_task(
        self,
        task_id: str,
        func: Callable,
        day_of_week: str = "mon",
        hour: int = 9,
        minute: int = 0,
    ):
        """添加每周任务 (day_of_week: mon-sun)"""
        trigger = CronTrigger(
            day_of_week=day_of_week, hour=hour, minute=minute,
            timezone="Asia/Shanghai"
        )
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
            misfire_grace_time=3600,
        )
        logger.info(f"已添加每周任务 [{task_id}]: {day_of_week} {hour:02d}:{minute:02d}")

    def add_interval_task(
        self,
        task_id: str,
        func: Callable,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ):
        """添加间隔任务"""
        trigger = IntervalTrigger(hours=hours, minutes=minutes, seconds=seconds)
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
        )
        logger.info(f"已添加间隔任务 [{task_id}]: 每{hours}h{minutes}m")

    def add_cron_task(
        self,
        task_id: str,
        func: Callable,
        cron_expr: str,
    ):
        """
        添加 cron 表达式任务
        cron_expr: "0 7 * * *" = 每天 07:00
                   "0 */4 * * *" = 每 4 小时
                   "30 8 * * 1-5" = 工作日 08:30
        """
        parts = cron_expr.split()
        if len(parts) == 5:
            minute, hour, day, month, dow = parts
            trigger = CronTrigger(
                minute=minute, hour=hour, day=day, month=month,
                day_of_week=dow, timezone="Asia/Shanghai"
            )
        else:
            logger.error(f"无效的 cron 表达式: {cron_expr}")
            return

        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
            misfire_grace_time=3600,
        )
        logger.info(f"已添加 cron 任务 [{task_id}]: {cron_expr}")

    def remove_task(self, task_id: str):
        """移除任务"""
        try:
            self.scheduler.remove_job(task_id)
            logger.info(f"已移除任务: {task_id}")
        except Exception as e:
            logger.warning(f"移除任务失败: {task_id} - {e}")

    def start(self):
        """启动调度器"""
        self.scheduler.start()
        logger.info("任务调度器已启动 (Asia/Shanghai)")

    def shutdown(self, wait: bool = True):
        """关闭调度器"""
        self.scheduler.shutdown(wait=wait)
        logger.info("任务调度器已关闭")

    def list_tasks(self) -> list:
        """列出所有任务"""
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else "N/A",
                "trigger": str(job.trigger),
            }
            for job in jobs
        ]

    async def run_task_now(self, task_id: str):
        """立即执行指定任务"""
        job = self.scheduler.get_job(task_id)
        if job:
            logger.info(f"立即执行任务: {task_id}")
            result = job.func()
            if asyncio.iscoroutine(result):
                await result
        else:
            logger.warning(f"任务不存在: {task_id}")
