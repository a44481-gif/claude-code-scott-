#!/usr/bin/env python3
"""
健康食品 AI 扩客代理人 - 主入口
Usage:
    python run.py                          # 完整执行周期
    python run.py --mode collect           # 仅数据收集
    python run.py --mode analyze           # 仅AI分析
    python run.py --mode report            # 仅生成报告
    python run.py --mode email             # 仅发送邮件
    python run.py --mode scheduler         # 启动定时调度模式
    python run.py --mode test              # 测试模式
"""
import asyncio
import sys
import argparse
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from src.automation.executor import HealthFoodAgent
from src.scheduling.scheduler import create_default_scheduler

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/agent_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
)


def parse_args():
    parser = argparse.ArgumentParser(description="健康食品 AI 扩客代理人")
    parser.add_argument(
        "--mode",
        type=str,
        default="full",
        choices=["full", "collect", "analyze", "report", "email", "scheduler", "test"],
        help="运行模式"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="配置文件路径"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )
    return parser.parse_args()


async def run_collect(agent: HealthFoodAgent):
    """仅数据收集"""
    logger.info(">>> 执行模式: 数据收集")
    result = await agent.collect_data()
    logger.info(f"收集完成: {result}")
    return result


async def run_analyze(agent: HealthFoodAgent):
    """仅AI分析"""
    logger.info(">>> 执行模式: AI分析")
    result = await agent.analyze_and_decide()
    logger.info(f"分析完成: {result}")
    return result


async def run_report(agent: HealthFoodAgent):
    """仅生成报告"""
    logger.info(">>> 执行模式: 生成报告")
    path = await agent.generate_report()
    logger.info(f"报告已生成: {path}")
    return path


async def run_email(agent: HealthFoodAgent):
    """仅发送邮件"""
    logger.info(">>> 执行模式: 发送邮件")
    await agent.send_weekly_report()
    logger.info("邮件发送完成")


def run_scheduler(agent: HealthFoodAgent):
    """启动定时调度"""
    logger.info(">>> 执行模式: 定时调度")
    scheduler = create_default_scheduler(agent.config, agent)
    scheduler.start()
    logger.info("定时调度已启动，按 Ctrl+C 停止")

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("正在停止调度器...")
        scheduler.shutdown()
        logger.info("调度器已停止")


async def run_test(agent: HealthFoodAgent):
    """测试模式"""
    logger.info(">>> 执行模式: 测试")

    logger.info("[测试1] 产品爬虫...")
    products = await agent.taobao_crawler.crawl_all_keywords()
    logger.info(f"   爬取到 {len(products)} 个产品")

    logger.info("[测试2] 台湾市场数据...")
    market = await agent.taiwan_crawler.get_market_price_ranges()
    logger.info(f"   获取到 {len(market)} 个品类价格")

    logger.info("[测试3] 竞争对手分析...")
    competitor = await agent.competitor_crawler.analyze_competitor_landscape()
    logger.info(f"   分析了 {len(competitor.get('competitors', []))} 个竞争对手")

    logger.info("[测试4] 选品决策...")
    agent.products_data = products
    agent.market_data = market
    selected = agent._execute_product_selection()
    logger.info(f"   推荐 {len(selected)} 个产品")

    logger.info("[测试5] 定价策略...")
    pricing = agent.pricing_engine.generate_pricing_report(selected[:5], market)
    logger.info(f"   生成 {len(pricing.get('products', []))} 个定价方案")

    logger.info("[测试6] 报告生成...")
    report_path = await agent.generate_report()
    logger.info(f"   报告: {report_path}")

    logger.info("=" * 50)
    logger.info("所有测试完成!")
    logger.info("=" * 50)


async def run_full(agent: HealthFoodAgent):
    """完整执行"""
    logger.info(">>> 执行模式: 完整周期")
    result = await agent.run_full_cycle()
    logger.info(f"执行结果: {result}")
    return result


async def main():
    args = parse_args()

    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    # 初始化代理
    agent = HealthFoodAgent(config_path=args.config)

    # 根据模式执行
    if args.mode == "collect":
        await run_collect(agent)
    elif args.mode == "analyze":
        await run_analyze(agent)
    elif args.mode == "report":
        await run_report(agent)
    elif args.mode == "email":
        await run_email(agent)
    elif args.mode == "scheduler":
        run_scheduler(agent)
    elif args.mode == "test":
        await run_test(agent)
    else:
        await run_full(agent)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常: {e}")
        sys.exit(1)
