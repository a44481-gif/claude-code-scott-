"""
PC Parts Agent - 執行入口
用法:
  python run.py                  # 完整流程
  python run.py --mode collect   # 收集價格數據
  python run.py --mode analyze   # 分析趨勢
  python run.py --mode alert     # 檢查價格提醒
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
from pc_parts_agent.src.executor import PcPartsExecutor


def main():
    parser = argparse.ArgumentParser(description="PC Parts Agent")
    parser.add_argument("--mode", default="full",
                        choices=["full", "collect", "analyze", "alert", "report", "scheduler"],
                        help="執行模式")
    args = parser.parse_args()

    agent_dir = Path(__file__).resolve().parent.parent  # → pc_parts_agent/
    cfg = load_config(config_path=str(agent_dir / "config/settings.json"))
    setup_logger("pc_parts", level="INFO", log_dir=str(agent_dir / "logs"))

    executor = PcPartsExecutor(cfg)

    if args.mode == "scheduler":
        from core import TaskScheduler
        scheduler = TaskScheduler(cfg)
        scheduler.add_cron_task("daily_collect", executor.run, cfg["crawling"]["schedule"])
        scheduler.start()
        print("PC Parts Agent 排程已啟動，按 Ctrl+C 停止")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            scheduler.shutdown()
    else:
        result = asyncio.run(executor.run(mode=args.mode))
        print(f"執行完成: {result.get('status', 'unknown')}")


if __name__ == "__main__":
    main()
