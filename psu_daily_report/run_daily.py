"""
PSU 每日銷售報告自動化 — 主執行腳本
功能：收集京東/天貓/Amazon 電源供應器數據 → MiniMax AI 分析 → Email 寄送

使用方式：
  python run_daily.py                  # 立即執行一次完整流程
  python run_daily.py --collect-only   # 只收集數據，不分析也不寄送
  python run_daily.py --analyze-only   # 讀取上次數據，只做分析（調試用）
  python run_daily.py --config <path>  # 指定設定檔路徑
"""

import argparse
import json
import logging
import sys
import os
from datetime import date, datetime
from pathlib import Path

# 加入模組路徑
sys.path.insert(0, str(Path(__file__).parent))

from crawlers import JDCrawler, AmazonCrawler, TmallCrawler
from analysis.ai_analyzer import MiniMaxAnalyzer
from notification.email_sender import EmailSender

# ─────────────────────────── 日誌設定 ───────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("PSU_Report")


# ─────────────────────────── 設定載入 ───────────────────────────
def load_config(config_path: str | None = None) -> dict:
    base = Path(__file__).parent
    if config_path:
        cfg_file = Path(config_path)
    else:
        cfg_file = base / "config.yaml"

    if not cfg_file.exists():
        # 嘗試讀取 YAML（Python 3.9+ 內建）
        try:
            import yaml
            with open(cfg_file, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except ImportError:
            logger.warning("PyYAML 未安裝，嘗試手動解析 config.yaml")
            return _parse_yaml_manual(cfg_file)
    else:
        try:
            import yaml
            with open(cfg_file, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except ImportError:
            logger.warning("PyYAML 未安裝，請執行 pip install pyyaml")
            sys.exit(1)


def _parse_yaml_manual(cfg_file: Path) -> dict:
    """極簡 YAML 解析（僅支援基本結構，備用）"""
    result = {}
    current_section = None
    with open(cfg_file, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("#") or not line.strip():
                continue
            if ":" in line and not line.strip().startswith("-"):
                key = line.split(":")[0].strip()
                if key in ("brands", "minimax", "email", "crawler", "schedule", "output"):
                    current_section = key
                    result[key] = {}
            elif line.strip().startswith("- name:"):
                if "brands" not in result:
                    result["brands"] = []
                name = line.split("name:")[1].strip().strip('"')
                result["brands"].append({"name": name, "aliases": []})
    return result


# ─────────────────────────── 數據收集 ───────────────────────────
def collect_all(config: dict) -> list[dict]:
    """並行收集三個平台的數據"""
    brands = config.get("brands", [])
    if not brands:
        logger.error("設定檔中未找到品牌列表")
        return []

    all_products = []
    keywords = ["電源供應器", "PC電源", "ATX電源"]

    # 京東
    logger.info("=== 開始收集京東數據 ===")
    try:
        with JDCrawler(config) as jd:
            for kw in keywords:
                all_products.extend(jd.collect(brands, kw))
    except Exception as e:
        logger.error(f"京東爬蟲錯誤: {e}")

    # Amazon（用英文關鍵字）
    logger.info("=== 開始收集 Amazon 數據 ===")
    amazon_keywords = ["power supply unit", "PSU computer", "ATX power supply"]
    try:
        with AmazonCrawler(config) as amz:
            for kw in amazon_keywords:
                all_products.extend(amz.collect(brands, kw))
    except Exception as e:
        logger.error(f"Amazon 爬蟲錯誤: {e}")

    # 天貓
    logger.info("=== 開始收集天貓數據 ===")
    try:
        with TmallCrawler(config) as tm:
            for kw in keywords:
                all_products.extend(tm.collect(brands, kw))
    except Exception as e:
        logger.error(f"天貓爬蟲錯誤: {e}")

    # 去重（依 URL）
    seen = set()
    unique = []
    for p in all_products:
        key = p.url or p.product_name
        if key and key not in seen:
            seen.add(key)
            unique.append(p)

    logger.info(f"✅ 總計收集到 {len(unique)} 個獨特商品")
    return [p.__dict__ for p in unique]


# ─────────────────────────── 主流程 ───────────────────────────
def run(
    config_path: str | None = None,
    mode: str = "full",
) -> bool:
    """
    mode:
      full       - 收集 + 分析 + 寄送（預設）
      collect    - 只收集
      analyze    - 分析並寄送（需有上次數據）
    """
    config = load_config(config_path)
    today_str = date.today().isoformat()

    # 報告輸出目錄
    report_dir = Path(__file__).parent / config.get("output", {}).get(
        "report_dir", "reports"
    )
    report_dir.mkdir(exist_ok=True)
    raw_data_path = report_dir / f"raw_data_{today_str}.json"

    products: list[dict] = []

    if mode in ("full", "collect"):
        # ── 1. 收集 ──
        logger.info(f"🚀 開始每日 PSU 數據收集 [{today_str}]")
        products = collect_all(config)

        # 保存原始數據
        if config.get("output", {}).get("save_raw_data", True) and products:
            with open(raw_data_path, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 原始數據已保存: {raw_data_path}")

        if mode == "collect":
            return True

    else:
        # 讀取上次數據
        latest = max(report_dir.glob("raw_data_*.json"), default=None)
        if not latest:
            logger.error("找不到原始數據檔，請先執行完整收集")
            return False
        with open(latest, encoding="utf-8") as f:
            products = json.load(f)
        logger.info(f"📂 讀取歷史數據: {latest.name}")

    if not products:
        logger.warning("⚠️ 沒有收集到任何商品，跳過分析和寄送")
        return False

    # ── 2. AI 分析 ──
    logger.info("🤖 呼叫 MiniMax AI 分析...")
    analyzer = MiniMaxAnalyzer(config)
    analysis = analyzer.analyze(products)

    # 保存分析報告
    report_path = report_dir / f"report_{today_str}.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(analysis)
    logger.info(f"💾 分析報告已保存: {report_path}")

    # ── 3. Email 寄送 ──
    logger.info("📧 發送 Email 報告...")
    sender = EmailSender(config)
    success = sender.send_report(
        analysis_text=analysis,
        raw_data=products if config.get("output", {}).get("save_raw_data") else None,
        report_date=today_str,
    )

    if success:
        logger.info("✅ 每日報告流程全部完成！")
    else:
        logger.error("❌ Email 發送失敗，請檢查設定")

    return success


# ─────────────────────────── 入口 ───────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="PSU 每日銷售報告自動化"
    )
    parser.add_argument(
        "--config", "-c",
        help="設定檔路徑（預設：config.yaml）",
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["full", "collect", "analyze"],
        default="full",
        help="執行模式：full=收集+分析+寄送, collect=只收集, analyze=只分析寄送",
    )
    args = parser.parse_args()

    success = run(config_path=args.config, mode=args.mode)
    sys.exit(0 if success else 1)
