"""
IT News Agent - 執行入口
用法:
  python run.py                  # 完整流程
  python run.py --mode collect   # 只收集
  python run.py --mode brief     # 只生成簡報
  python run.py --mode send      # 只發送
  python run.py --mode scheduler # 排程模式
"""
import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent  # → .claude/
sys.path.insert(0, str(_ROOT))

import asyncio
import argparse
from pathlib import Path
from core import setup_logger, load_config
from it_news_agent.src.executor import ItNewsExecutor

def main():
    parser = argparse.ArgumentParser(description="IT News Agent")
    parser.add_argument("--mode", default="full",
                        choices=["full", "collect", "brief", "send", "scheduler"],
                        help="執行模式")
    parser.add_argument("--config", default="config/settings.json",
                        help="配置文件路徑")
    args = parser.parse_args()

    # Setup
    agent_dir = Path(__file__).resolve().parent.parent  # → it_news_agent/
    cfg = load_config(config_path=str(agent_dir / args.config))
    setup_logger("it_news", level="INFO", log_dir=str(agent_dir / "logs"))

    executor = ItNewsExecutor(cfg)

    if args.mode == "scheduler":
        from core import TaskScheduler
        scheduler = TaskScheduler(cfg)
        scheduler.add_cron_task("daily_collect", executor.run, cfg["crawling"]["schedule"])
        scheduler.start()
        print("IT News Agent 排程已啟動，按 Ctrl+C 停止")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            scheduler.shutdown()
    else:
        result = asyncio.run(executor.run(mode=args.mode))
        print(f"執行完成: {result.get('status', 'unknown')}")


if __name__ == "__main__":
    main()
