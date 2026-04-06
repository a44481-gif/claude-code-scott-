"""
Agents Orchestrator - 主調度器
用法:
  python run.py                  # 完整流程（依次執行所有 Agent）
  python run.py --mode run-all  # 執行所有 Agent
  python run.py --mode status   # 查看 Agent 狀態
  python run.py --mode scheduler # 啟動排程
"""
import sys
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])

import asyncio
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

# Setup logging first
from core import setup_logger, TaskScheduler, load_config


class Orchestrator:
    """主調度器 - 協調所有 Agent"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        cfg_path = self.base_dir / "config/orchestrator.json"
        self.cfg = load_config(config_path=str(cfg_path)) if cfg_path.exists() else {}
        setup_logger("orchestrator", level="INFO", log_dir=str(self.base_dir / "logs"))
        self.status = {}
        self.results = {}

    def run_agent(self, agent_name: str, module_path: str, mode: str = "full") -> dict:
        """執行單個 Agent"""
        logger.info(f"開始執行: {agent_name}")
        self.status[agent_name] = "running"

        try:
            # Dynamic import
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "executor",
                str(self.base_dir / module_path / "src/executor.py")
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["executor"] = module
                spec.loader.exec_module(module)

                ExecutorClass = getattr(module, f"{agent_name.replace('_', '')}Executor", None)
                if not ExecutorClass:
                    # Try exact match
                    ExecutorClass = getattr(module, "Executor", None)

                if ExecutorClass:
                    executor = ExecutorClass(self.cfg.get(agent_name, {}))
                    if hasattr(executor, "run"):
                        result = asyncio.run(executor.run(mode=mode))
                    elif hasattr(executor, "run_async"):
                        result = asyncio.run(executor.run_async(mode=mode))
                    else:
                        result = asyncio.run(executor.run(mode=mode))
                else:
                    result = {"status": "error", "message": f"未找到 Executor 類"}
            else:
                result = {"status": "error", "message": "模塊加載失敗"}

            self.status[agent_name] = "completed"
            self.results[agent_name] = result
            logger.info(f"{agent_name} 完成: {result.get('status', 'unknown')}")
            return result

        except Exception as e:
            logger.error(f"{agent_name} 執行失敗: {e}")
            self.status[agent_name] = "failed"
            self.results[agent_name] = {"status": "failed", "error": str(e)}
            return {"status": "failed", "error": str(e)}

    def run_all(self) -> dict:
        """順序執行所有 Agent"""
        logger.info("=== 開始執行所有 Agent ===")

        agents = [
            ("it_news_agent", "it_news_agent"),
            ("pc_parts_agent", "pc_parts_agent"),
            ("msi_monitor_agent", "msi_monitor_agent"),
            ("report_agent", "report_agent"),
        ]

        results = {}
        for agent_id, agent_name in agents:
            result = self.run_agent(agent_name, agent_id, mode="full")
            results[agent_id] = result

        logger.info("=== 所有 Agent 執行完成 ===")
        return {
            "status": "completed",
            "results": results,
            "completed_at": datetime.now().isoformat(),
        }

    def get_status(self) -> dict:
        """獲取所有 Agent 狀態"""
        return {
            "agents": self.status,
            "last_results": {
                name: {
                    "status": res.get("status", "unknown"),
                    "items": res.get("items_collected", res.get("total", "")),
                }
                for name, res in self.results.items()
            },
            "checked_at": datetime.now().isoformat(),
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agents Orchestrator")
    parser.add_argument("--mode", default="run-all",
                        choices=["run-all", "status", "scheduler"],
                        help="執行模式")
    args = parser.parse_args()

    orchestrator = Orchestrator()

    if args.mode == "run-all":
        result = orchestrator.run_all()
        print(f"\n執行完成: {json.dumps(result, ensure_ascii=False, indent=2, default=str)}")

    elif args.mode == "status":
        status = orchestrator.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2, default=str))

    elif args.mode == "scheduler":
        scheduler = TaskScheduler({})
        # Agent 1+2+3 並行 → Agent 4 順序執行
        scheduler.add_cron_task("run_all_agents", orchestrator.run_all, "0 6 * * *")
        scheduler.start()
        print("Orchestrator 排程已啟動 (每天 06:00)，按 Ctrl+C 停止")
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            scheduler.shutdown()


if __name__ == "__main__":
    main()
