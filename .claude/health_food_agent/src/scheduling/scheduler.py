"""
定时任务调度器
"""
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from typing import Callable, Optional


class TaskScheduler:
    """任务调度器"""

    def __init__(self, config: dict):
        self.config = config
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self.tasks = {}

    def add_daily_task(self, task_id: str, func: Callable,
                       hour: int = 8, minute: int = 0):
        """添加每日任务"""
        trigger = CronTrigger(hour=hour, minute=minute, timezone="Asia/Shanghai")
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
            misfire_grace_time=3600,  # 1小时内可补执行
        )
        logger.info(f"已添加每日任务 [{task_id}]: {hour:02d}:{minute:02d}")

    def add_weekly_task(self, task_id: str, func: Callable,
                       day_of_week: str = "mon", hour: int = 9, minute: int = 0):
        """添加每周任务"""
        # day_of_week: mon, tue, wed, thu, fri, sat, sun
        trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute,
                             timezone="Asia/Shanghai")
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
            misfire_grace_time=3600,
        )
        logger.info(f"已添加每周任务 [{task_id}]: {day_of_week} {hour:02d}:{minute:02d}")

    def add_interval_task(self, task_id: str, func: Callable, hours: int = 0,
                         minutes: int = 0, seconds: int = 0):
        """添加间隔任务"""
        trigger = IntervalTrigger(hours=hours, minutes=minutes, seconds=seconds)
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
        )
        logger.info(f"已添加间隔任务 [{task_id}]: 每{hours}小时{minutes}分钟")

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
        logger.info("任务调度器已启动")

    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown(wait=False)
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
            await job.func()
        else:
            logger.warning(f"任务不存在: {task_id}")


def create_default_scheduler(config: dict, executor) -> TaskScheduler:
    """创建默认调度器并配置任务"""
    scheduler = TaskScheduler(config)

    # 每日数据收集 - 早上8点
    scheduler.add_daily_task(
        "daily_collection",
        executor.collect_data,
        hour=8, minute=0
    )

    # 每日AI分析 - 早上8:30
    scheduler.add_daily_task(
        "daily_analysis",
        executor.analyze_and_decide,
        hour=8, minute=30
    )

    # 每周报告生成 - 周一早上9点
    scheduler.add_weekly_task(
        "weekly_report",
        executor.generate_report,
        day_of_week="mon", hour=9, minute=0
    )

    # 每周邮件发送 - 周一早上9:30
    scheduler.add_weekly_task(
        "weekly_email",
        executor.send_weekly_report,
        day_of_week="mon", hour=9, minute=30
    )

    return scheduler
