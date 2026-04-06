"""
全球 PSU 市場每日自動化報告 — 主執行腳本
功能：全球 35+ 電商平台數據收集 → AI 分析 → PPT 報告 → Email 發送
"""

import argparse
import json
import logging
import subprocess
import sys
import time
import traceback
from datetime import date
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 自動注入 src 目錄
sys.path.insert(0, str(Path(__file__).parent))

from global_crawlers import CRAWLER_REGISTRY
from analysis.ai_analyzer import GlobalAnalyzer
from report.ppt_generator import PPTReporter
from notification.email_sender import GlobalEmailSender

# 日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
    encoding="utf-8",
)
logger = logging.getLogger("Global_PSU_Report")


# ─── 配置載入 ───────────────────────────────────────────────────────

def load_config(config_path: str | None = None) -> dict:
    base = Path(__file__).parent
    cfg_file = Path(config_path) if config_path else base / "config.yaml"

    if not cfg_file.exists():
        logger.error(f"設定檔不存在: {cfg_file}")
        # 返回預設配置
        return {
            "brands": [
                {"name": "華碩（ASUS）", "aliases": ["ASUS", "Asus"]},
                {"name": "技嘉（GIGABYTE）", "aliases": ["GIGABYTE", "Gigabyte"]},
                {"name": "微星（MSI）", "aliases": ["MSI", "Msi"]},
                {"name": "海盜船（Corsair）", "aliases": ["Corsair", "CORSAIR"]},
                {"name": "海韻（Seasonic）", "aliases": ["Seasonic", "SEASONIC"]},
                {"name": "安鈦克（Antec）", "aliases": ["ANTEC", "antec"]},
                {"name": "酷冷至尊（Cooler Master）", "aliases": ["Cooler Master", "COOLER MASTER"]},
                {"name": "BQT", "aliases": ["BQT", "bqt"]},
                {"name": "九州風神（DeepCool）", "aliases": ["DeepCool", "DEEPCOOL"]},
                {"name": "聯力（Lian Li）", "aliases": ["Lian Li", "LIAN LI"]},
            ],
            "crawler": {
                "timeout": 30,
                "retry": 3,
                "delay_between_requests": 2,
            },
            "minimax": {"api_key": ""},
            "email": {
                "smtp_server": "smtp.163.com",
                "smtp_port": 465,
                "sender": "h13751019800@163.com",
                "password": "",
                "recipient": "h13751019800@163.com",
            },
            "output": {
                "report_dir": "reports",
                "save_raw_data": True,
            },
            "platforms": {
                "enabled": [p[0].__name__ for p in CRAWLER_REGISTRY],
            },
        }

    import yaml
    with open(cfg_file, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─── 數據收集 ───────────────────────────────────────────────────────

def collect_all(config: dict, mode: str = "primary") -> list[dict]:
    """
    收集全球電商數據
    mode: "primary" = 只運行 priority=1 的爬蟲（HTTP可直接抓）
          "all" = 運行所有爬蟲
          "selected" = 只運行配置中指定的爬蟲
    """
    brands = config.get("brands", [])
    if not brands:
        logger.error("設定檔中未找到品牌列表")
        return []

    all_products = []

    # 選擇要運行的爬蟲
    if mode == "primary":
        registry = [(c, kw, pri, note) for c, kw, pri, note in CRAWLER_REGISTRY if pri == 1]
        logger.info(f"=== 使用 Primary 模式：{len(registry)} 個爬蟲（HTTP 直接可抓）===")
    else:
        registry = CRAWLER_REGISTRY
        logger.info(f"=== 使用 All 模式：{len(registry)} 個爬蟲（含 JS/API 渲染平台）===")

    # 按地區分組，並行執行
    # 先分組，便於日誌顯示
    region_groups: dict[str, list] = {}
    for crawler_cls, kw, pri, note in registry:
        region = getattr(crawler_cls, "REGION", "Unknown")
        if region not in region_groups:
            region_groups[region] = []
        region_groups[region].append((crawler_cls, kw))

    total_crawlers = sum(len(v) for v in region_groups.values())
    logger.info(f"共 {total_crawlers} 個爬蟲，分 {len(region_groups)} 個地區組")

    # 使用多線程執行（限制並發數）
    MAX_WORKERS = 6  # 同時運行最多 6 個爬蟲

    def run_crawler(crawler_cls, keywords, config, idx, total):
        try:
            logger.info(f"[{idx}/{total}] 啟動爬蟲: {crawler_cls.__name__}")
            crawler = crawler_cls(config)
            products = []

            # 嘗試每個關鍵字
            for kw in keywords[:2]:  # 每爬蟲最多 2 個關鍵字
                try:
                    results = crawler.collect(brands, kw, pages=1)
                    products.extend(results)
                except Exception as e:
                    logger.warning(f"[{crawler_cls.__name__}] 關鍵字 '{kw}' 失敗: {e}")
                time.sleep(config.get("crawler", {}).get("delay_between_requests", 2))

            crawler.close()
            logger.info(f"[{crawler_cls.__name__}] 完成: 收集到 {len(products)} 個商品")
            return [p.to_dict() for p in products]
        except Exception as e:
            logger.error(f"[{crawler_cls.__name__}] 爬蟲錯誤: {e}")
            return []

    idx = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for region, crawlers in region_groups.items():
            logger.info(f"  地區 [{region}]: {len(crawlers)} 個爬蟲")
            for crawler_cls, kw in crawlers:
                idx += 1
                future = executor.submit(run_crawler, crawler_cls, kw, config, idx, total_crawlers)
                futures[future] = crawler_cls.__name__

        for future in as_completed(futures):
            crawler_name = futures[future]
            try:
                products = future.result()
                all_products.extend(products)
            except Exception as e:
                logger.error(f"[{crawler_name}] 任務失敗: {e}")

    # 去重（依 URL）
    seen = set()
    unique = []
    for p in all_products:
        key = p.get("url") or p.get("product_name", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(p)

    logger.info(f"✅ 總計收集到 {len(unique)} 個獨特商品（去重後）")
    return unique


# ─── 主流程 ────────────────────────────────────────────────────────

def run(
    config_path: str | None = None,
    mode: str = "full",
    collect_only: bool = False,
    analyze_only: bool = False,
    demo_mode: bool = False,
) -> bool:
    """
    mode:
      full       - 收集 + 分析 + PPT + 寄送（預設）
      collect    - 只收集數據
      analyze    - 分析 + PPT + 寄送（需有上次數據）
    demo_mode: 使用 mock_data.py 生成的模擬數據（無需網絡）
    """
    config = load_config(config_path)
    today_str = date.today().isoformat()

    report_dir = Path(__file__).parent / config.get("output", {}).get("report_dir", "reports")
    report_dir.mkdir(exist_ok=True)

    raw_data_path = report_dir / f"raw_data_{today_str}.json"
    ppt_path = report_dir / f"全球PSU報告_{today_str}.pptx"
    analysis_path = report_dir / f"analysis_{today_str}.txt"

    products: list[dict] = []

    if demo_mode:
        # ── Demo 模式：使用模擬數據 ──
        logger.info("\n🎭 Demo 模式：使用模擬數據進行演示")
        mock_file = report_dir / "mock_data.json"
        if not mock_file.exists():
            logger.info("  生成模擬數據...")
            subprocess.run(["python", "mock_data.py"], check=True)
        with open(mock_file, encoding="utf-8") as f:
            products = json.load(f)
        logger.info(f"  ✅ 使用 {len(products)} 個模擬商品")
        logger.info(f"  💾 另存至: {raw_data_path}")
        with open(raw_data_path, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

    elif not analyze_only:
        # ── 1. 收集 ──
        logger.info(f"\n🚀 開始全球 PSU 數據收集 [{today_str}]")
        logger.info(f"📋 目標品牌: {[b['name'] for b in config.get('brands', [])]}")
        logger.info(f"🌐 目標平台: {len(CRAWLER_REGISTRY)} 個")

        # 映射 run mode → collect_all mode
        crawl_mode = "primary" if mode in ("full", "collect") else "all"
        products = collect_all(config, mode=crawl_mode)

        if products and config.get("output", {}).get("save_raw_data", True):
            with open(raw_data_path, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 原始數據已保存: {raw_data_path}")

        if collect_only:
            logger.info("✅ 數據收集完成（collect-only 模式）")
            return True

        if not products:
            logger.warning("⚠️ 沒有收集到任何商品，請檢查網絡或 API 設定")
            # 嘗試讀取上次數據
            latest = max(report_dir.glob("raw_data_*.json"), default=None)
            if latest:
                logger.info(f"📂 讀取上次數據: {latest.name}")
                with open(latest, encoding="utf-8") as f:
                    products = json.load(f)
            else:
                logger.error("找不到任何歷史數據，無法繼續")
                return False
    else:
        # 讀取上次數據
        latest = max(report_dir.glob("raw_data_*.json"), default=None)
        if not latest:
            logger.error("找不到原始數據檔，請先執行完整收集")
            return False
        with open(latest, encoding="utf-8") as f:
            products = json.load(f)
        logger.info(f"📂 讀取歷史數據: {latest.name}（{len(products)} 個商品）")

    # ── 2. AI 分析 ──
    logger.info("\n🤖 開始 MiniMax AI 分析...")
    analyzer = GlobalAnalyzer(config)
    analysis = analyzer.analyze(products, today_str)

    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write(analysis)
    logger.info(f"💾 分析報告已保存: {analysis_path}")

    # ── 3. PPT 生成 ──
    logger.info("\n📊 生成 PPT 報告...")
    try:
        ppt_reporter = PPTReporter(config)
        ppt_reporter.set_data(products, analysis)
        ppt_file = ppt_reporter.generate(str(ppt_path))
        if ppt_file:
            logger.info(f"✅ PPT 已生成: {ppt_file}")
        else:
            logger.warning("⚠️ PPT 生成失敗（python-pptx 未安裝），將只發送郵件")
            ppt_file = None
    except Exception as e:
        logger.error(f"PPT 生成失敗: {e}")
        traceback.print_exc()
        ppt_file = None

    # ── 4. Email 發送 ──
    logger.info("\n📧 發送 Email 報告...")
    sender = GlobalEmailSender(config)
    success = sender.send_report(
        analysis_text=analysis,
        raw_data=products if config.get("output", {}).get("save_raw_data") else None,
        ppt_path=str(ppt_path) if ppt_path.exists() else None,
        report_date=today_str,
    )

    if success:
        logger.info("\n" + "=" * 60)
        logger.info("✅ 每日報告流程全部完成！")
        logger.info(f"   📅 日期: {today_str}")
        logger.info(f"   📦 商品: {len(products)} 個")
        logger.info(f"   📊 分析: {analysis_path}")
        if ppt_file:
            logger.info(f"   📄 PPT: {ppt_path}")
        logger.info(f"   📧 郵件: 已發送至 {config.get('email', {}).get('recipient')}")
        logger.info("=" * 60)
    else:
        logger.error("❌ Email 發送失敗，請檢查 SMTP 設定")

    return success


# ─── 入口 ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="全球電商平台 PSU 每日自動化報告"
    )
    parser.add_argument(
        "--config", "-c",
        help="設定檔路徑（預設：config.yaml）",
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["full", "collect", "analyze"],
        default="full",
        help="執行模式：full=收集+分析+PPT+寄送, collect=只收集, analyze=分析+PPT+寄送",
    )
    parser.add_argument(
        "--crawler-mode",
        choices=["primary", "all"],
        default="primary",
        help="爬蟲模式：primary=HTTP直接可抓的平台, all=所有平台（含JS渲染）",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="使用模擬數據運行（用於演示，無需網絡）",
    )
    args = parser.parse_args()

    try:
        success = run(
            config_path=args.config,
            mode=args.mode,
            collect_only=(args.mode == "collect"),
            analyze_only=(args.mode == "analyze"),
            demo_mode=args.demo,
        )
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("用戶中斷")
        sys.exit(1)
    except Exception as e:
        logger.error(f"執行失敗: {e}")
        traceback.print_exc()
        sys.exit(1)
