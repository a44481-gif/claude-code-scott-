#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI数字人新闻内容生产与全球分发系统 - 主程序
Digital Human News System - Main Entry Point
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config_loader import get_config
from src.utils.logger import setup_logger
from src.news.news_fetcher import NewsFetcher
from src.filter.content_filter import ContentFilter
from src.creator.ai_creator import AICreator
from src.human.digital_human import DigitalHumanGenerator
from src.publisher.publisher import PlatformPublisher
from src.notifier.email_notifier import EmailNotifier


class NewsSystem:
    """AI数字人新闻系统主类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化系统

        Args:
            config_path: 配置文件路径 (可选)
        """
        self.config = get_config()
        self.logger = self._setup_logging()

        # 初始化各模块
        self.news_fetcher = NewsFetcher()
        self.content_filter = ContentFilter()
        self.ai_creator = AICreator()
        self.digital_human = DigitalHumanGenerator()
        self.publisher = PlatformPublisher()
        self.notifier = EmailNotifier()

        # 执行结果
        self.execution_result: Dict[str, Any] = {
            'start_time': None,
            'end_time': None,
            'execution_time': 0,
            'news_fetched': 0,
            'news_passed': 0,
            'videos_created': 0,
            'videos_published': 0,
            'category_stats': {},
            'douyin_status': {},
            'youtube_status': {},
            'errors': [],
            'status': 'initialized'
        }

    def _setup_logging(self):
        """设置日志"""
        log_dir = self.config.get('paths.logs', 'logs')
        logger = setup_logger('main', log_dir)
        return logger

    def run(self) -> Dict[str, Any]:
        """
        执行完整的工作流程

        Returns:
            执行结果
        """
        self.logger.info("=" * 50)
        self.logger.info("AI数字人新闻系统启动")
        self.logger.info("=" * 50)

        start_time = time.time()
        self.execution_result['start_time'] = datetime.now().isoformat()

        try:
            # Step 1: 抓取新闻
            self.logger.info("[Step 1/6] 开始抓取新闻...")
            raw_news = self.news_fetcher.fetch_all_sources()
            self.execution_result['news_fetched'] = len(raw_news)
            self.logger.info(f"抓取完成，共 {len(raw_news)} 条新闻")

            # Step 2: 去重
            self.logger.info("[Step 2/6] 新闻去重...")
            deduplicated_news = self.news_fetcher.deduplicate(raw_news)
            self.logger.info(f"去重完成，剩余 {len(deduplicated_news)} 条")

            # Step 3: 内容筛选
            self.logger.info("[Step 3/6] 内容筛选与处理...")
            filter_result = self.content_filter.process(deduplicated_news)
            passed_news = filter_result['passed']
            self.execution_result['news_passed'] = len(passed_news)
            self.execution_result['category_stats'] = filter_result['statistics'].get(
                'category_distribution', {}
            )
            self.logger.info(f"筛选完成，通过 {len(passed_news)} 条")

            # Step 4: AI二创
            self.logger.info("[Step 4/6] AI二创内容生成...")
            created_content = self.ai_creator.create_content(passed_news)
            self.logger.info(f"二创完成，生成 {len(created_content)} 条内容")

            # Step 5: 数字人视频生成
            self.logger.info("[Step 5/6] 数字人视频生成...")
            videos = self.digital_human.generate_videos(created_content)
            self.execution_result['videos_created'] = len(videos)
            self.logger.info(f"视频生成完成，共 {len(videos)} 个视频")

            # Step 6: 多平台分发
            self.logger.info("[Step 6/6] 多平台发布...")
            publish_results = self.publisher.publish_all(videos)
            self.execution_result['videos_published'] = publish_results['total_success']
            self.execution_result['douyin_status'] = publish_results['douyin']
            self.execution_result['youtube_status'] = publish_results['youtube']
            self.logger.info(f"发布完成，成功发布 {publish_results['total_success']} 个视频")

            # 执行成功
            self.execution_result['status'] = 'success'

        except Exception as e:
            self.logger.error(f"执行出错: {str(e)}")
            self.execution_result['errors'].append(str(e))
            self.execution_result['status'] = 'failed'

            # 尝试发送错误告警
            try:
                self.notifier.send_error_alert(
                    str(e),
                    f"发生在: Step {self._get_current_step()}"
                )
            except Exception:
                pass

        finally:
            end_time = time.time()
            self.execution_result['end_time'] = datetime.now().isoformat()
            self.execution_result['execution_time'] = end_time - start_time

        # 发送日报
        self._send_report()

        # 输出结果
        self._print_summary()

        return self.execution_result

    def _get_current_step(self) -> int:
        """获取当前执行步骤"""
        if self.execution_result['news_fetched'] == 0:
            return 1
        elif self.execution_result['news_passed'] == 0:
            return 2
        return 6

    def _send_report(self):
        """发送执行报告"""
        try:
            # 生成简要总结
            summary = self._generate_summary()
            self.execution_result['summary'] = summary

            self.notifier.send_daily_report(self.execution_result)
        except Exception as e:
            self.logger.error(f"发送报告失败: {str(e)}")

    def _generate_summary(self) -> str:
        """生成执行总结"""
        news_count = self.execution_result['news_fetched']
        passed_count = self.execution_result['news_passed']
        video_count = self.execution_result['videos_created']
        publish_count = self.execution_result['videos_published']

        return (
            f"今日系统执行完成。共抓取新闻 {news_count} 条，"
            f"筛选通过 {passed_count} 条，生成 {video_count} 个视频，"
            f"成功发布 {publish_count} 个视频到抖音和YouTube平台。"
        )

    def _print_summary(self):
        """打印执行摘要"""
        self.logger.info("=" * 50)
        self.logger.info("执行摘要")
        self.logger.info("=" * 50)
        self.logger.info(f"状态: {self.execution_result['status']}")
        self.logger.info(f"抓取新闻: {self.execution_result['news_fetched']} 条")
        self.logger.info(f"筛选通过: {self.execution_result['news_passed']} 条")
        self.logger.info(f"生成视频: {self.execution_result['videos_created']} 个")
        self.logger.info(f"发布视频: {self.execution_result['videos_published']} 个")
        self.logger.info(f"执行耗时: {self.execution_result['execution_time']:.1f} 秒")

        if self.execution_result['errors']:
            self.logger.warning(f"错误数量: {len(self.execution_result['errors'])}")

        self.logger.info("=" * 50)
        self.logger.info("AI数字人新闻系统执行完成")
        self.logger.info("=" * 50)

    def run_step(self, step: str) -> Any:
        """
        运行单个步骤

        Args:
            step: 步骤名称 ('fetch', 'filter', 'create', 'generate', 'publish')

        Returns:
            步骤执行结果
        """
        step_map = {
            'fetch': (self.news_fetcher.fetch_all_sources, '抓取新闻'),
            'filter': (self.content_filter.process, '内容筛选'),
            'create': (self.ai_creator.create_content, 'AI二创'),
            'generate': (self.digital_human.generate_videos, '视频生成'),
            'publish': (self.publisher.publish_all, '平台发布')
        }

        if step not in step_map:
            raise ValueError(f"未知步骤: {step}")

        func, name = step_map[step]
        self.logger.info(f"执行步骤: {name}")

        try:
            result = func()
            self.logger.info(f"步骤 {name} 执行成功")
            return result
        except Exception as e:
            self.logger.error(f"步骤 {name} 执行失败: {str(e)}")
            raise


def run_scheduler():
    """运行定时任务调度器"""
    import schedule
    from datetime import time as dt_time

    config = get_config()
    scheduler_config = config.get_section('scheduler')

    fetch_hour = scheduler_config.get('news_fetch_hour', 6)
    fetch_minute = scheduler_config.get('news_fetch_minute', 0)
    report_hour = scheduler_config.get('report_hour', 22)
    report_minute = scheduler_config.get('report_minute', 0)

    logger = setup_logger('scheduler')

    def job():
        """定时任务"""
        logger.info("定时任务触发，开始执行...")
        system = NewsSystem()
        system.run()

    # 设置定时任务
    schedule.every().day.at(f"{fetch_hour:02d}:{fetch_minute:02d}").do(job)

    logger.info(f"定时任务已设置: 每天 {fetch_hour:02d}:{fetch_minute:02d} 执行")

    # 运行调度器
    logger.info("调度器启动，等待任务执行...")
    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    """主函数入口"""
    parser = argparse.ArgumentParser(
        description='AI数字人新闻内容生产与全球分发系统'
    )
    parser.add_argument(
        '--mode',
        choices=['full', 'fetch', 'filter', 'create', 'generate', 'publish', 'scheduler'],
        default='full',
        help='运行模式'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='配置文件路径'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试模式（使用模拟数据）'
    )

    args = parser.parse_args()

    try:
        if args.mode == 'scheduler':
            run_scheduler()
        else:
            system = NewsSystem(args.config)

            if args.mode == 'full':
                system.run()
            else:
                result = system.run_step(args.mode)
                print(json.dumps(result, ensure_ascii=False, indent=2))

    except KeyboardInterrupt:
        print("\n用户中断执行")
        sys.exit(0)
    except Exception as e:
        print(f"执行失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
