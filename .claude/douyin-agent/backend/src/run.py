"""
Douyin Agent Backend - 執行入口
用法:
  python run.py                  # FastAPI 服務
  python run.py --mode scheduler # 獨立排程模式
  python run.py --mode collect   # 一次性收集指標
"""
import sys
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

import asyncio
import argparse
from pathlib import Path
from core import setup_logger, load_config
from src.executor import DouyinAgent


def main():
    parser = argparse.ArgumentParser(description="Douyin Agent")
    parser.add_argument("--mode", default="api",
                        choices=["api", "scheduler", "collect", "server"],
                        help="執行模式")
    args = parser.parse_args()

    agent_dir = Path(__file__).parent.parent
    cfg = load_config(config_path=str(agent_dir / "config/settings.json"))
    setup_logger("douyin_agent", level="INFO", log_dir=str(agent_dir / "logs"))

    executor = DouyinAgent(cfg)

    if args.mode == "scheduler":
        from core import TaskScheduler
        scheduler = TaskScheduler(cfg)
        scheduler.add_interval_task("collect_metrics", executor.collect_metrics, hours=6)
        scheduler.add_interval_task("post_content", executor.post_scheduled, hours=4)
        scheduler.start()
        print("Douyin Agent 排程已啟動，按 Ctrl+C 停止")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            scheduler.shutdown()

    elif args.mode == "server":
        import uvicorn
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from src.api.routes import router

        app = FastAPI(title="Douyin Agent API")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.include_router(router)
        app.state.executor = executor

        print("啟動 Douyin Agent API 服務...")
        uvicorn.run(app, host="0.0.0.0", port=8005)

    else:
        result = asyncio.run(executor.collect_metrics())
        print(f"執行完成: {result}")


if __name__ == "__main__":
    main()
