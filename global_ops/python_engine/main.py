#!/usr/bin/env python3
"""
GlobalOPS · Python 执行引擎 · 主入口
用法:
    python main.py generate                    # 从 DB 取 pending 内容，触发处理
    python main.py publish --platform youtube  # 发布到指定平台
    python main.py analytics                   # 数据分析
    python main.py revenue                     # 收益报表
    python main.py task --type generate        # 处理调度任务
    python main.py stats                       # 内容库统计
"""

import sys
import io
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

BASE_DIR = Path(__file__).parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s · %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"global_ops_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("GlobalOPS")

# 延迟导入（避免启动时就检查 DB）
from src.config import get_env, PLATFORMS
from src.db_client import DBClient


def cmd_stats(args):
    """内容库统计"""
    db = DBClient()
    stats = db.get_content_stats()
    print("\n📊 内容库统计")
    print(f"   状态分布: {stats['by_status']}")
    print(f"   题材分布: {stats['by_theme']}")

    # 每日发布统计
    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT platform, COUNT(*) as count
            FROM publish_log
            WHERE published_at >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY platform
        """)
        pub_stats = {r[0]: r[1] for r in cur.fetchall()}
    print(f"   近7天发布: {pub_stats}")
    db.close()


def cmd_analytics(args):
    """数据分析"""
    db = DBClient()
    days = args.days or 30
    revenue = db.get_revenue_summary(days)

    print(f"\n📈 运营数据（近{days}天）")
    print(f"   总收益（毛）: ${revenue['total_gross']:.2f}")
    print(f"   总收益（净）: ${revenue['total_net']:.2f}")
    print(f"   平台分布: {revenue['by_platform']}")

    # 爆款内容
    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT content_id, platform, views_7d, likes, published_at
            FROM publish_log
            WHERE published_at >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY views_7d DESC LIMIT 5
        """, (days,))
        print("\n🔥 Top 5 内容:")
        for i, row in enumerate(cur.fetchall(), 1):
            print(f"   {i}. [{row[1]}] {row[0]} | 7天播放:{row[2]} | 点赞:{row[3]} | {row[4].strftime('%m-%d') if row[4] else 'N/A'}")
    db.close()


def cmd_revenue(args):
    """收益报表"""
    db = DBClient()
    days = args.days or 30
    revenue = db.get_revenue_summary(days)

    print(f"\n💰 收益报表（近{days}天）")
    print(f"   总毛收益: ${revenue['total_gross']:.2f}")
    print(f"   总净收益: ${revenue['total_net']:.2f}")
    for platform, data in revenue["by_platform"].items():
        print(f"   · {platform}: 毛${data['total']:.2f} / 净${data['net']:.2f}")
    db.close()


def cmd_publish(args):
    """发布到指定平台"""
    db = DBClient()
    platform = args.platform
    limit = args.limit or 5

    print(f"\n🚀 开始发布到 {platform}（最多 {limit} 条）")

    # 获取待发布内容
    contents = db.get_pending_content(limit=limit)
    if not contents:
        print("   ⚠️  没有待发布内容")
        db.close()
        return

    # 获取可用账号
    account = db.get_available_account(platform)
    if not account:
        print(f"   ⚠️  没有可用的 {platform} 账号，请先添加")
        db.close()
        return

    print(f"   使用账号: {account['account_name']} ({account['account_id']})")

    # 动态导入 uploader（避免循环依赖）
    if platform == "youtube":
        from src.uploader.youtube import YouTubeUploader
        uploader = YouTubeUploader(account)
    else:
        print(f"   ⚠️  平台 {platform} 的上传器尚未实现")
        db.close()
        return

    published = 0
    for content in contents:
        try:
            print(f"   ▶ 发布: {content['content_id']} - {content.get('title', '')[:50]}")
            result = uploader.upload_content(content)
            if result:
                db.log_publish({
                    "content_id": content["content_id"],
                    "platform": platform,
                    "account_id": account["account_id"],
                    "account_name": account["account_name"],
                    "video_url": result.get("url"),
                    "video_id": result.get("id"),
                    "title": content.get("title"),
                    "description": content.get("caption"),
                    "tags_applied": content.get("tags", []),
                    "published_at": datetime.now(),
                    "status": "published",
                })
                db.update_content_status(content["content_id"], "published",
                                        video_output=result.get("url"))
                db.update_account_upload(account["account_id"])
                published += 1
                print(f"   ✅ 成功: {result.get('url')}")
            else:
                print(f"   ❌ 上传失败")
        except Exception as e:
            logger.exception(f"发布失败: {content['content_id']}")
            print(f"   ❌ 错误: {e}")

    print(f"\n   完成: {published}/{len(contents)} 条发布成功")
    db.close()


def cmd_task(args):
    """处理调度任务队列"""
    db = DBClient()
    task_type = args.type
    limit = args.limit or 10

    tasks = db.get_due_tasks(task_type=task_type, limit=limit)
    if not tasks:
        print(f"没有待处理的 {task_type or '任意'} 任务")
        db.close()
        return

    print(f"\n📋 处理 {len(tasks)} 个 {task_type or '任意'} 任务")
    for task in tasks:
        print(f"   ▶ [{task['task_type']}] {task['task_uuid']} | {task['content_id']}")
        db.update_task_status(task["task_uuid"], "running")

        try:
            result = {}
            # TODO: 根据 task_type 分发到具体处理模块
            # if task['task_type'] == 'generate': ...
            # elif task['task_type'] == 'clip': ...
            # elif task['task_type'] == 'publish': ...
            db.update_task_status(task["task_uuid"], "completed", result=result)
            print(f"   ✅ 完成")
        except Exception as e:
            logger.exception(f"任务失败: {task['task_uuid']}")
            db.update_task_status(task["task_uuid"], "failed", error=str(e))
            print(f"   ❌ 失败: {e}")

    db.close()


def cmd_generate(args):
    """触发内容处理流程"""
    db = DBClient()
    theme = args.theme
    region = args.region or "southeast_asia"
    limit = args.limit or 10

    contents = db.get_pending_content(limit=limit, theme=theme, region=region)
    if not contents:
        print("没有待处理内容（所有内容已处理或数据库为空）")
        print("提示: 先运行 node content_engine/src/generator.js 填充内容库")
        db.close()
        return

    print(f"\n⚙️  处理 {len(contents)} 条内容")
    for content in contents:
        print(f"   ▶ {content['content_id']} [{content['theme_type']}] - {content.get('title', '')[:40]}")
        # TODO: 触发剪辑、字幕、封面流程
        db.update_content_status(content["content_id"], "generated")
        print(f"   ✅ 已标记为 generated")

    db.close()


def cmd_add_account(args):
    """添加平台账号"""
    db = DBClient()
    db.insert_account({
        "platform": args.platform,
        "account_id": args.account_id,
        "account_name": args.account_name or args.account_id,
        "account_handle": args.handle,
        "region": args.region or "global",
        "language": args.lang or "en",
        "status": "active",
        "credentials": {},
    })
    print(f"✅ 账号 {args.account_id} ({args.platform}) 已添加")
    db.close()


def main():
    parser = argparse.ArgumentParser(description="GlobalOPS · 统一运营引擎")
    sub = parser.add_subparsers(dest="cmd")

    # stats
    sub.add_parser("stats", help="内容库统计")

    # analytics
    p_analytics = sub.add_parser("analytics", help="数据分析")
    p_analytics.add_argument("--days", type=int, help="统计天数")

    # revenue
    p_rev = sub.add_parser("revenue", help="收益报表")
    p_rev.add_argument("--days", type=int, help="统计天数")

    # publish
    p_pub = sub.add_parser("publish", help="发布内容到平台")
    p_pub.add_argument("--platform", required=True, choices=["youtube", "tiktok", "instagram", "facebook", "pinterest"])
    p_pub.add_argument("--limit", type=int, default=5)

    # task
    p_task = sub.add_parser("task", help="处理调度任务")
    p_task.add_argument("--type", help="任务类型: generate/clip/publish/analytics")
    p_task.add_argument("--limit", type=int, default=10)

    # generate
    p_gen = sub.add_parser("generate", help="处理待生成内容")
    p_gen.add_argument("--theme", help="题材过滤")
    p_gen.add_argument("--region", help="地区过滤")
    p_gen.add_argument("--limit", type=int, default=10)

    # add-account
    p_acc = sub.add_parser("add-account", help="添加平台账号")
    p_acc.add_argument("--platform", required=True)
    p_acc.add_argument("--account-id", required=True)
    p_acc.add_argument("--account-name")
    p_acc.add_argument("--handle")
    p_acc.add_argument("--region", default="global")
    p_acc.add_argument("--lang", default="en")

    args = parser.parse_args()

    if args.cmd == "stats":
        cmd_stats(args)
    elif args.cmd == "analytics":
        cmd_analytics(args)
    elif args.cmd == "revenue":
        cmd_revenue(args)
    elif args.cmd == "publish":
        cmd_publish(args)
    elif args.cmd == "task":
        cmd_task(args)
    elif args.cmd == "generate":
        cmd_generate(args)
    elif args.cmd == "add-account":
        cmd_add_account(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
