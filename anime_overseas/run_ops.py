"""
动漫出海运营 · 主入口脚本
anime_overseas/run_ops.py

用法:
    python run_ops.py --action daily_ops
    python run_ops.py --action translate --file input.srt --lang id
    python run_ops.py --action clip --input video.mp4
    python run_ops.py --action full_pipeline --anime 斗罗大陆 --lang en
"""

import sys
import os

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("AnimeOps")


def daily_ops():
    """每日运营流程"""
    logger.info("=" * 60)
    logger.info("动漫出海 · 每日运营")
    logger.info("=" * 60)

    from analytics_dashboard import run_daily_report
    from revenue_tracker import RevenueTracker
    from multi_platform_publisher import generate_content_calendar

    # 1. 数据采集 + 报告
    logger.info("[1/5] 采集数据...")
    run_daily_report()

    # 2. 打印收益追踪
    logger.info("[2/5] 收益数据...")
    tracker = RevenueTracker()
    report = tracker.generate_monthly_report()
    print(report)

    # 3. 生成内容日历
    logger.info("[3/5] 生成内容日历...")
    calendar = generate_content_calendar(
        anime_list=["斗罗大陆", "凡人修仙传", "斗破苍穹"],
        episodes_per_day=3,
        days=7,
    )
    logger.info(f"已生成 {len(calendar)} 条内容计划")

    # 4. 检查待发布任务
    logger.info("[4/5] 检查定时任务...")
    from multi_platform_publisher import PublishScheduler
    scheduler = PublishScheduler()
    pending = scheduler.get_pending_tasks()
    logger.info(f"待执行任务: {len(pending)} 个")

    # 5. 版权安全检查
    logger.info("[5/5] 版权抽查...")
    from copyright_screener import CopyrightScreener
    screener = CopyrightScreener()
    test = screener.analyze("斗罗大陆", duration=60, content_type="clip")
    logger.info(f"版权风险: {test['risk_level']} ({test['risk_score']}分)")

    logger.info("=" * 60)
    logger.info("每日运营流程完成!")
    logger.info("=" * 60)


def translate_file(input_file: str, target_lang: str, quality: str = "standard"):
    """翻译字幕文件"""
    from translate_automation import translate_and_localize

    logger.info(f"翻译字幕: {input_file} -> {target_lang}")
    result = translate_and_localize(
        input_srt=input_file,
        target_lang=target_lang,
        anime_name="Anime",
        quality=quality,
    )
    logger.info(f"完成: {result}")


def clip_video(input_file: str, start: float, duration: float, watermark: str = None):
    """剪辑视频片段"""
    from video_editor import AnimeVideoEditor

    logger.info(f"剪辑视频: {input_file} @ {start}s +{duration}s")
    editor = AnimeVideoEditor()
    result = editor.clip_by_duration(
        input_path=input_file,
        start_time=start,
        duration=duration,
        watermark_text=watermark or "@AnimeChannel",
    )
    logger.info(f"完成: {result}")


def generate_thumbnail(title: str, subtitle: str = None, template: str = "shocking"):
    """生成封面"""
    from thumbnail_generator import ThumbnailGenerator

    logger.info(f"生成封面: {title}")
    gen = ThumbnailGenerator()
    result = gen.generate(
        output_path=f"thumbnail_{datetime.now().strftime('%H%M%S')}.png",
        title=title,
        subtitle=subtitle,
        template=template,
    )
    logger.info(f"完成: {result}")


def full_pipeline(anime_name: str, episode: int = None, target_lang: str = "en",
                   include_subtitle: bool = True):
    """
    完整工作流：
    1. 生成标题+标签
    2. 生成封面
    3. 生成字幕翻译
    4. 生成发布元数据
    """
    logger.info("=" * 60)
    logger.info(f"动漫出海 · 完整工作流: {anime_name}")
    logger.info("=" * 60)

    from multi_platform_publisher import MultiPlatformPublisher

    publisher = MultiPlatformPublisher()
    publisher.set_target_language(target_lang)

    metadata = publisher.generate_content_metadata(
        anime_name=anime_name,
        episode=episode,
        target_lang=target_lang,
    )

    logger.info(f"标题: {metadata['title']}")
    logger.info(f"标签: {', '.join(metadata['tags'][:8])}")

    # 生成封面
    gen = ThumbnailGenerator()
    thumb_file = gen.generate(
        output_path=f"thumb_{anime_name}_EP{episode or '?'}_{datetime.now().strftime('%H%M')}.png",
        title=metadata['title'][:40],
        subtitle=f"{anime_name} EP{episode or '?'}",
        template="shocking",
    )
    logger.info(f"封面: {thumb_file}")

    logger.info("=" * 60)
    logger.info("完整工作流完成！下一步：")
    logger.info("1. 剪辑视频并应用字幕")
    logger.info("2. 使用 multi_platform_publisher 上传")
    logger.info("3. 追踪数据并更新收益")
    logger.info("=" * 60)


def show_help():
    """显示帮助信息"""
    help_text = """
动漫出海运营代理人 · 主入口

使用方法:
    python run_ops.py <action> [options]

可用操作:

  daily_ops
    执行每日运营流程（数据采集+报告+版权检查）
    示例: python run_ops.py daily_ops

  translate
    翻译字幕文件
    参数:
      --file  输入SRT文件路径
      --lang  目标语言 (en/id/vi/th/ar/es/pt)
      --quality 翻译质量 (fast/standard/professional)
    示例: python run_ops.py translate --file input.srt --lang id

  clip
    剪辑视频片段
    参数:
      --input   输入视频路径
      --start   开始时间（秒）
      --duration 剪辑时长（秒）
      --watermark 水印文字
    示例: python run_ops.py clip --input video.mp4 --start 30 --duration 60

  thumbnail
    生成封面图
    参数:
      --title    主标题
      --subtitle 副标题
      --template 模板 (shocking/emotional/action/romance/news/ranking)
    示例: python run_ops.py thumbnail --title "震撼来袭" --template shocking

  full_pipeline
    完整内容制作工作流
    参数:
      --anime   动漫名称
      --episode 集数
      --lang    目标语言
    示例: python run_ops.py full_pipeline --anime 斗罗大陆 --episode 5 --lang en

  revenue
    查看收益报表
    示例: python run_ops.py revenue

  calendar
    生成内容日历
    参数:
      --days   天数
      --lang   语言
    示例: python run_ops.py calendar --days 30 --lang en

文件结构:
  anime_overseas/
  ├── anime_ops_config.py          配置文件
  ├── translate_automation.py     字幕翻译
  ├── video_editor.py             视频剪辑
  ├── thumbnail_generator.py       封面生成
  ├── multi_platform_publisher.py  多平台发布
  ├── analytics_dashboard.py      数据分析
  ├── revenue_tracker.py           收益追踪
  ├── copyright_screener.py       版权筛查
  ├── 动漫出海运营方案.md         商业方案
  ├── 动漫出海SOP.md              操作手册
  └── requirements.txt             Python依赖
"""
    print(help_text)


def show_revenue():
    """显示收益报表"""
    from revenue_tracker import RevenueTracker
    tracker = RevenueTracker()
    print(tracker.generate_monthly_report())

    goal = tracker.check_goal_progress(2000)
    print(f"\n💵 月目标 $2000 进度: {goal['progress']}%")
    print(f"   预估全月: ${goal['projected']:.2f}")
    if not goal['is_on_track']:
        print(f"   每日需再赚: ${goal['needed_daily']:.2f}")


def show_calendar(days: int = 30, lang: str = "en"):
    """显示内容日历"""
    from multi_platform_publisher import generate_content_calendar

    anime_list = ["斗罗大陆", "凡人修仙传", "斗破苍穹", "一人之下", "狐妖小红娘"]
    calendar = generate_content_calendar(anime_list, 3, days, lang)

    print("=" * 60)
    print(f"动漫出海 · {days}天内容日历")
    print("=" * 60)
    for entry in calendar:
        print(f"[{entry['date']} 第{entry['post_slot']}条] {entry['title']}")
    print("=" * 60)
    print(f"总计: {len(calendar)} 条内容")


# ============ 主入口 ============

def main():
    parser = argparse.ArgumentParser(description="动漫出海运营代理人", add_help=False)
    parser.add_argument("action", nargs="?", default="help",
                        choices=["daily_ops", "translate", "clip", "thumbnail",
                                "full_pipeline", "revenue", "calendar", "help"])

    args, unknown = parser.parse_known_args()

    if args.action == "daily_ops":
        daily_ops()
    elif args.action == "translate":
        p = argparse.ArgumentParser()
        p.add_argument("--file", required=True)
        p.add_argument("--lang", default="en")
        p.add_argument("--quality", default="standard")
        a = p.parse_args(unknown)
        translate_file(a.file, a.lang, a.quality)
    elif args.action == "clip":
        p = argparse.ArgumentParser()
        p.add_argument("--input", required=True)
        p.add_argument("--start", type=float, default=0)
        p.add_argument("--duration", type=float, default=60)
        p.add_argument("--watermark")
        a = p.parse_args(unknown)
        clip_video(a.input, a.start, a.duration, a.watermark)
    elif args.action == "thumbnail":
        p = argparse.ArgumentParser()
        p.add_argument("--title", required=True)
        p.add_argument("--subtitle")
        p.add_argument("--template", default="shocking")
        a = p.parse_args(unknown)
        generate_thumbnail(a.title, a.subtitle, a.template)
    elif args.action == "full_pipeline":
        p = argparse.ArgumentParser()
        p.add_argument("--anime", required=True)
        p.add_argument("--episode", type=int)
        p.add_argument("--lang", default="en")
        a = p.parse_args(unknown)
        full_pipeline(a.anime, a.episode, a.lang)
    elif args.action == "revenue":
        show_revenue()
    elif args.action == "calendar":
        p = argparse.ArgumentParser()
        p.add_argument("--days", type=int, default=30)
        p.add_argument("--lang", default="en")
        a = p.parse_args(unknown)
        show_calendar(a.days, a.lang)
    else:
        show_help()


if __name__ == "__main__":
    main()
