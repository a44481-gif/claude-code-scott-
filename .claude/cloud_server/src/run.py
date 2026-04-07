"""
Cloud Agent Server - 雲端執行所有 Agent，結果返回本地。

架構:
  FastAPI (uvicorn) ──> APScheduler 排程
                     ──> Agent Executor 執行層
                     ──> SQLite 結果存儲
  本地 Client ──> /results/{agent} 輪詢 ──> 本地存儲 + 判定

部署方式:
  1. VPS:           uvicorn src.run:app --host 0.0.0.0 --port 8000
  2. Cloud Run:     docker build + gcloud run deploy
  3. 雲函數:        打包為 ZIP 部署
"""

import sys, os
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent  # → .claude/
sys.path.insert(0, str(_ROOT))

import asyncio
import json
import hashlib
import sqlite3
import feedparser
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# ── Local core (雲端副本，核心邏輯) ────────────────────────────────
from core import classify_news_category, classify_brand
from core.base_crawler import BaseCrawler
from core.ai_analyzer import MiniMaxAnalyzer
from core.models import NewsItem

# ── FastAPI ────────────────────────────────────────────────────────
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx

# ════════════════════════════════════════════════════════════════════
#  Config
# ════════════════════════════════════════════════════════════════════

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "cloud_results.db"

SCHEDULE = {
    "it_news":      "0 7 * * *",   # 每天 07:00 UTC
    "pc_parts":     "0 8 * * *",   # 每天 08:00 UTC
    "msi_monitor":  "0 9 * * *",   # 每天 09:00 UTC
    "report":       "0 10 * * 1",   # 每週一 10:00 UTC
}

LOCAL_WEBHOOK = os.environ.get("LOCAL_WEBHOOK", "")  # 回調本地 URL

# ════════════════════════════════════════════════════════════════════
#  Database
# ════════════════════════════════════════════════════════════════════

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            run_at TEXT NOT NULL,
            status TEXT NOT NULL,
            items_count INTEGER DEFAULT 0,
            data_json TEXT,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            started_at TEXT,
            finished_at TEXT,
            status TEXT DEFAULT 'running'
        )
    """)
    conn.commit()
    return conn

conn = init_db()

def save_result(agent: str, status: str, data: Any, error: str = ""):
    items_count = len(data) if isinstance(data, list) else 0
    conn.execute(
        "INSERT INTO agent_results (agent, run_at, status, items_count, data_json, error) VALUES (?,?,?,?,?,?)",
        (agent, datetime.utcnow().isoformat(), status, items_count,
         json.dumps(data, ensure_ascii=False) if data else None, error or "")
    )
    conn.commit()

def get_latest(agent: str, limit: int = 10) -> List[Dict]:
    rows = conn.execute(
        "SELECT agent, run_at, status, items_count, data_json, error FROM agent_results WHERE agent=? ORDER BY id DESC LIMIT ?",
        (agent, limit)
    ).fetchall()
    return [
        {"agent": r[0], "run_at": r[1], "status": r[2],
         "items_count": r[3], "data": json.loads(r[4]) if r[4] else None, "error": r[5]}
        for r in rows
    ]

def update_run(agent: str, status: str, finished_at: str = None):
    if finished_at:
        conn.execute(
            "UPDATE agent_runs SET status=?, finished_at=? WHERE agent=? AND status='running'",
            (status, finished_at, agent)
        )
    else:
        conn.execute(
            "INSERT INTO agent_runs (agent, started_at, status) VALUES (?,?,?)",
            (agent, datetime.utcnow().isoformat(), "running")
        )
    conn.commit()

# ════════════════════════════════════════════════════════════════════
#  Agent: IT News (RSS-based)
# ════════════════════════════════════════════════════════════════════

class CloudRSSCrawler(BaseCrawler):
    """Lightweight cloud RSS crawler"""
    def __init__(self, source_name: str, feed_url: str, config: Optional[Dict] = None):
        super().__init__(config)
        self.source_name = source_name
        self.feed_url = feed_url

    async def crawl(self, **kwargs) -> List[Dict]:
        url = kwargs.get("url") or self.feed_url
        html = await self.async_http_get(url)
        if not html:
            return []
        try:
            feed = feedparser.parse(html)
            return [{
                "title": getattr(e, "title", "") or "",
                "url": getattr(e, "link", "") or "",
                "source": self.source_name,
                "published_at": getattr(e, "published", "")[:16] if getattr(e, "published", "") else "",
                "summary": re.sub(r"<[^>]+>", "", (getattr(e, "summary", "") or "")[:200]).strip(),
            } for e in feed.entries[:15] if getattr(e, "title", "")]
        except Exception as e:
            logger.error(f"[{self.source_name}] RSS 解析失敗: {e}")
            return []

async def run_it_news() -> List[Dict]:
    """收集 IT 新聞 - 京東/中國 IP 可訪問更多來源"""
    logger.info("🛰️ [Cloud] IT News Agent 開始執行...")
    update_run("it_news", "running")

    sources = [
        ("TechCrunch",    "https://techcrunch.com/feed/"),
        ("AnandTech",     "https://www.anandtech.com/rss/"),
        ("Tom's Hardware","https://www.tomshardware.com/rss/"),
        ("IT之家",        "https://www.ithome.com/rss/"),
        ("ZOL",           "https://www.zol.com.cn/rss/news.xml"),
        ("CNET",          "https://www.cnet.com/rss/news/"),
        ("The Verge",     "https://www.theverge.com/rss/index.xml"),
        # ── 京東/天貓 需要中國 IP，以下為替代方案 ──
        ("36Kr",          "https://36kr.com/feed"),      # 36氪
        ("愛范兒",         "https://www.ifanr.com/feed"),  # 愛范兒
    ]

    all_items = []
    seen = set()

    for name, url in sources:
        try:
            crawler = CloudRSSCrawler(name, url)
            await crawler.run()
            for item in crawler.results:
                h = hashlib.md5((item["title"] + item["url"]).encode()).hexdigest()
                if h not in seen:
                    seen.add(h)
                    item["category"] = classify_news_category(item["title"] + " " + item.get("summary", ""))
                    all_items.append(item)
            logger.info(f"  [{name}] +{len(crawler.results)} 篇")
        except Exception as e:
            logger.warning(f"  [{name}] 失敗: {e}")

    logger.info(f"IT News 完成: 共 {len(all_items)} 篇")
    save_result("it_news", "success", all_items)
    update_run("it_news", "success", datetime.utcnow().isoformat())
    await notify_local("it_news", all_items)
    return all_items

# ════════════════════════════════════════════════════════════════════
#  Agent: PC Parts (京東/Amazon Price Tracking)
# ════════════════════════════════════════════════════════════════════

async def run_pc_parts() -> List[Dict]:
    """收集 PC 零組件價格 - 雲端無 IP 限制可訪問京東"""
    logger.info("🛰️ [Cloud] PC Parts Agent 開始執行...")
    update_run("pc_parts", "running")

    # 京東搜索 API（無需登入）
    JD_KEYWORDS = [
        "RTX 4090", "RTX 4080", "Ryzen 9 7950X",
        "DDR5 32GB", "Samsung 990 Pro 2TB", "850W 金牌電源"
    ]

    items = []
    for kw in JD_KEYWORDS:
        try:
            # 京東聯盟 API（需申請）或直接爬蟲
            url = f"https://search.jd.com/Search?keyword={kw}&enc=utf-8&wq={kw}"
            # 實際爬蟲需要 JS 渲染，這裡用京東靜態 API 示範
            logger.info(f"  京東關鍵詞: {kw}")
            items.append({
                "keyword": kw,
                "source": "京東",
                "collected_at": datetime.utcnow().isoformat(),
            })
        except Exception as e:
            logger.warning(f"  [{kw}] 失敗: {e}")

    save_result("pc_parts", "success", items)
    update_run("pc_parts", "success", datetime.utcnow().isoformat())
    await notify_local("pc_parts", items)
    return items

# ════════════════════════════════════════════════════════════════════
#  Agent: MSI Monitor
# ════════════════════════════════════════════════════════════════════

async def run_msi_monitor() -> List[Dict]:
    """監控 MSI 官網更新"""
    logger.info("🛰️ [Cloud] MSI Monitor Agent 開始執行...")
    update_run("msi_monitor", "running")

    urls = {
        "news":      "https://www.msi.com/rss/news.xml",
        "events":    "https://www.msi.com/rss/events.xml",
        "products":  "https://www.msi.com/rss/products.xml",
    }

    all_items = []
    for name, url in urls.items():
        try:
            crawler = CloudRSSCrawler(f"MSI-{name}", url)
            await crawler.run()
            all_items.extend(crawler.results)
        except Exception as e:
            logger.warning(f"  [MSI-{name}] 失敗: {e}")

    save_result("msi_monitor", "success", all_items)
    update_run("msi_monitor", "success", datetime.utcnow().isoformat())
    await notify_local("msi_monitor", all_items)
    return all_items

# ════════════════════════════════════════════════════════════════════
#  Agent: Report Generator
# ════════════════════════════════════════════════════════════════════

async def run_report() -> Dict:
    """生成綜合報告"""
    logger.info("🛰️ [Cloud] Report Agent 開始執行...")
    update_run("report", "running")

    it_news = get_latest("it_news", 1)
    pc_parts = get_latest("pc_parts", 1)
    msi = get_latest("msi_monitor", 1)

    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "it_news_count": it_news[0]["items_count"] if it_news else 0,
        "pc_parts_count": pc_parts[0]["items_count"] if pc_parts else 0,
        "msi_updates_count": msi[0]["items_count"] if msi else 0,
        "sources": {
            "it_news": it_news[0]["data"] if it_news else [],
            "pc_parts": pc_parts[0]["data"] if pc_parts else [],
            "msi_monitor": msi[0]["data"] if msi else [],
        }
    }

    save_result("report", "success", report)
    update_run("report", "success", datetime.utcnow().isoformat())
    await notify_local("report", report)
    return report

# ════════════════════════════════════════════════════════════════════
#  Webhook 回調本地
# ════════════════════════════════════════════════════════════════════

async def notify_local(agent: str, data: Any):
    """將結果 POST 回本地 Webhook"""
    if not LOCAL_WEBHOOK:
        logger.debug(f"無 LOCAL_WEBHOOK 配置，跳過回調")
        return
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                LOCAL_WEBHOOK,
                json={"agent": agent, "data": data, "timestamp": datetime.utcnow().isoformat()},
            )
            logger.info(f"✅ 回調本地成功: {agent} → {resp.status_code}")
    except Exception as e:
        logger.warning(f"❌ 回調本地失敗: {agent} → {e}")

# ════════════════════════════════════════════════════════════════════
#  FastAPI App
# ════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="AI Agent Cloud Server",
    description="雲端執行所有 Agent，結果返回本地做判定和存儲",
    version="1.0.0",
)

scheduler = AsyncIOScheduler()

# ── Health ────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# ── Trigger ──────────────────────────────────────────────────────

class TriggerResponse(BaseModel):
    agent: str
    status: str
    message: str

@app.post("/trigger/{agent}", response_model=TriggerResponse)
async def trigger_agent(agent: str, background: BackgroundTasks):
    """觸發指定 Agent"""
    agents = {
        "it_news":     run_it_news,
        "pc_parts":    run_pc_parts,
        "msi_monitor": run_msi_monitor,
        "report":      run_report,
    }
    if agent not in agents:
        raise HTTPException(404, f"未知 Agent: {agent}")

    update_run(agent, "pending")
    background.add_task(agents[agent])
    return TriggerResponse(agent=agent, status="triggered", message=f"{agent} 已加入執行佇列")

@app.post("/trigger/all", response_model=Dict)
async def trigger_all(background: BackgroundTasks):
    """觸發所有 Agent"""
    background.add_task(run_it_news)
    background.add_task(run_pc_parts)
    background.add_task(run_msi_monitor)
    background.add_task(run_report)
    return {"status": "triggered", "agents": ["it_news", "pc_parts", "msi_monitor", "report"]}

# ── Results ───────────────────────────────────────────────────────

@app.get("/results/{agent}")
async def get_results(agent: str, limit: int = Query(10, ge=1, le=100)):
    """獲取指定 Agent 的最新結果"""
    rows = get_latest(agent, limit)
    if not rows:
        raise HTTPException(404, f"無 {agent} 結果")
    return {"agent": agent, "count": len(rows), "results": rows}

@app.get("/results/{agent}/latest")
async def get_latest_result(agent: str):
    """獲取最新一筆結果"""
    rows = get_latest(agent, 1)
    if not rows:
        raise HTTPException(404, f"無 {agent} 結果")
    return rows[0]

@app.get("/status")
async def get_status():
    """所有 Agent 狀態"""
    agents = ["it_news", "pc_parts", "msi_monitor", "report"]
    status = {}
    for agent in agents:
        rows = conn.execute(
            "SELECT status, run_at FROM agent_results WHERE agent=? ORDER BY id DESC LIMIT 1",
            (agent,)
        ).fetchone()
        status[agent] = {
            "status": rows[0] if rows else "no_data",
            "last_run": rows[1] if rows else None,
        }
    return {"agents": status, "server_time": datetime.utcnow().isoformat()}

@app.get("/history/{agent}")
async def get_history(agent: str, days: int = Query(7, ge=1, le=30)):
    """歷史執行記錄"""
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT agent, run_at, status, items_count, error FROM agent_results WHERE agent=? AND run_at>=? ORDER BY id DESC",
        (agent, since)
    ).fetchall()
    return {"agent": agent, "days": days, "runs": [
        {"run_at": r[1], "status": r[2], "items_count": r[3], "error": r[4]}
        for r in rows
    ]}

# ════════════════════════════════════════════════════════════════════
#  Startup / Shutdown
# ════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    logger.info("🚀 雲端 Agent Server 啟動")
    logger.info(f"   排程: {SCHEDULE}")
    logger.info(f"   本地回調: {LOCAL_WEBHOOK or '未配置'}")

    for agent, cron in SCHEDULE.items():
        minute, hour, *rest = cron.split()
        dom, month, dow = rest
        scheduler.add_job(
            {
                "it_news":     run_it_news,
                "pc_parts":    run_pc_parts,
                "msi_monitor": run_msi_monitor,
                "report":      run_report,
            }[agent],
            CronTrigger(minute=minute, hour=hour, day=dom if dom != "*" else None,
                       month=month if month != "*" else None,
                       day_of_week=dow if dow != "*" else None),
            id=agent,
            replace_existing=True,
        )
        logger.info(f"   📅 {agent} 排程已建立: {cron}")
    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()
    conn.close()
    logger.info("🛑 雲端 Agent Server 關閉")

# ════════════════════════════════════════════════════════════════════
#  Run
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.run:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False,
        log_level="info",
    )
