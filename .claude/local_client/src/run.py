"""
Local Agent Client - 本地輪詢雲端結果，本地存儲 + 判定。

功能:
  1. 輪詢雲端 Server 的 /results/{agent} API
  2. 本地存儲到 SQLite（本地判定）
  3. 比對歷史數據（趨勢判定）
  4. 觸發本地警報（價格異常/新聞熱點）
  5. 生成 HTML 報告
  6. 訂閱模式：長輪詢等待新結果

用法:
  python src/run.py                    # 一次性同步
  python src/run.py --watch            # 持續監控模式
  python src/run.py --agent it_news   # 只同步指定 Agent
  python src/run.py --since 7         # 同步最近 7 天歷史
"""

import sys, os
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT))

import asyncio
import json
import time
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import argparse
import httpx
from loguru import logger

# ── Config ────────────────────────────────────────────────────────

CLOUD_URL  = os.environ.get("CLOUD_URL",  "http://localhost:8000")
LOCAL_DB   = Path(__file__).resolve().parent.parent / "data" / "local_results.db"
LOCAL_DB.parent.mkdir(parents=True, exist_ok=True)

# 報警閾值
PRICE_DROP_THRESHOLD = 0.10   # 價格下跌 10% 觸發警報
HOT_NEWS_THRESHOLD   = 5      # 單日熱點新聞數量觸發警報

# ── Database ───────────────────────────────────────────────────────

def init_local_db():
    conn = sqlite3.connect(str(LOCAL_DB), check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS local_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            cloud_run_at TEXT,
            local_stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            items_count INTEGER DEFAULT 0,
            data_json TEXT,
            verdict TEXT,
            alerts TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT DEFAULT 'info',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            price REAL,
            source TEXT,
            collected_at TEXT,
            local_stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_run ON local_results(agent, cloud_run_at)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_price_keyword ON price_history(keyword, collected_at)
    """)
    conn.commit()
    return conn

conn = init_local_db()

# ── 本地判定 ───────────────────────────────────────────────────────

def judge_it_news(data: List[Dict]) -> Dict:
    """判定 IT 新聞"""
    if not data:
        return {"verdict": "無數據", "alerts": []}

    alerts = []
    verdict_parts = []

    # 1. 數量判定
    count = len(data)
    verdict_parts.append(f"今日收集 {count} 篇")

    # 2. 來源分佈
    sources = {}
    for item in data:
        src = item.get("source", "Unknown")
        sources[src] = sources.get(src, 0) + 1
    verdict_parts.append(f"涵蓋 {len(sources)} 個來源")

    # 3. 類別分佈
    categories = {}
    for item in data:
        cat = item.get("category", "General")
        categories[cat] = categories.get(cat, 0) + 1

    top_cat = max(categories, key=categories.get) if categories else "N/A"
    verdict_parts.append(f"熱點類別: {top_cat} ({categories.get(top_cat, 0)} 篇)")

    # 4. 熱點警報
    hot_sources = [s for s, c in sources.items() if c >= HOT_NEWS_THRESHOLD]
    if hot_sources:
        alerts.append({
            "type": "hot_source",
            "severity": "info",
            "message": f"來源 '{hot_sources[0]}' 集中發布 {sources[hot_sources[0]]} 篇新聞，可能是重大事件"
        })

    # 5. AI 基礎設施熱點
    ai_items = [i for i in data if i.get("category") == "AI Infrastructure"]
    if len(ai_items) >= 3:
        alerts.append({
            "type": "ai_boom",
            "severity": "warning",
            "message": f"檢測到 {len(ai_items)} 篇 AI 基礎設施相關新聞，行業可能有重大發布"
        })

    return {
        "verdict": " | ".join(verdict_parts),
        "alerts": alerts,
        "stats": {
            "total": count,
            "sources": sources,
            "categories": categories,
        }
    }

def judge_pc_parts(data: List[Dict]) -> Dict:
    """判定 PC 零組件價格"""
    if not data:
        return {"verdict": "無數據", "alerts": []}

    alerts = []

    for item in data:
        price = item.get("price")
        prev_price = item.get("prev_price")
        keyword = item.get("keyword", "N/A")

        if price and prev_price:
            drop = (prev_price - price) / prev_price
            if drop >= PRICE_DROP_THRESHOLD:
                alerts.append({
                    "type": "price_drop",
                    "severity": "warning",
                    "message": f"【{keyword}】價格下跌 {drop:.1%}：¥{prev_price} → ¥{price}"
                })
            elif drop >= 0.05:
                alerts.append({
                    "type": "price_mild_drop",
                    "severity": "info",
                    "message": f"【{keyword}】小幅下跌 {drop:.1%}：¥{prev_price} → ¥{price}"
                })

    return {
        "verdict": f"追蹤 {len(data)} 個關鍵詞 | {len([a for a in alerts if a['severity']=='warning'])} 個重要警報",
        "alerts": alerts,
    }

def judge_msi(data: List[Dict]) -> Dict:
    """判定 MSI 監控"""
    if not data:
        return {"verdict": "無數據", "alerts": []}

    types_count = {}
    for item in data:
        t = item.get("type", "news")
        types_count[t] = types_count.get(t, 0) + 1

    alerts = []
    for t, count in types_count.items():
        if t == "new_product" and count >= 1:
            alerts.append({
                "type": "new_product",
                "severity": "warning",
                "message": f"MSI 新品發布：{count} 款新產品"
            })

    return {
        "verdict": f"MSI {len(data)} 條更新：{', '.join(f'{v} 個{k}' for k,v in types_count.items())}",
        "alerts": alerts,
    }

def judge(data: Any, agent: str) -> Dict:
    """統一判定入口"""
    if agent == "it_news":
        return judge_it_news(data or [])
    elif agent == "pc_parts":
        return judge_pc_parts(data or [])
    elif agent == "msi_monitor":
        return judge_msi(data or [])
    elif agent == "report":
        return {"verdict": f"報告已生成，包含 {data.get('it_news_count',0)} 篇新聞", "alerts": []}
    return {"verdict": "無判定規則", "alerts": []}

# ── 存儲 ─────────────────────────────────────────────────────────

def store_result(agent: str, cloud_data: Dict) -> int:
    """將雲端結果存入本地，並執行判定"""
    data = cloud_data.get("data")
    verdict = judge(data, agent)

    # 存入 SQLite
    conn.execute(
        """INSERT INTO local_results
           (agent, cloud_run_at, items_count, data_json, verdict, alerts)
           VALUES (?,?,?,?,?,?)""",
        (agent,
         cloud_data.get("run_at"),
         len(data) if isinstance(data, list) else 0,
         json.dumps(data, ensure_ascii=False) if data else None,
         verdict["verdict"],
         json.dumps(verdict["alerts"], ensure_ascii=False))
    )
    conn.commit()

    # 存入價格歷史
    if agent == "pc_parts" and isinstance(data, list):
        for item in data:
            if item.get("price"):
                conn.execute(
                    "INSERT INTO price_history (keyword, price, source, collected_at) VALUES (?,?,?,?)",
                    (item.get("keyword",""), item["price"], item.get("source",""),
                     item.get("collected_at", datetime.utcnow().isoformat()))
                )
        conn.commit()

    # 存入警報
    for alert in verdict.get("alerts", []):
        conn.execute(
            "INSERT INTO alerts (agent, alert_type, message, severity) VALUES (?,?,?,?)",
            (agent, alert["type"], alert["message"], alert.get("severity", "info"))
        )
    conn.commit()

    row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return row_id

# ── 輪詢 ──────────────────────────────────────────────────────────

async def sync_agent(agent: str, verbose: bool = True) -> Optional[Dict]:
    """從雲端同步單個 Agent 的最新結果"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{CLOUD_URL}/results/{agent}/latest")
            if resp.status_code == 404:
                if verbose:
                    logger.warning(f"[{agent}] 雲端尚無數據")
                return None

            cloud_data = resp.json()

            # 檢查是否已存
            existing = conn.execute(
                "SELECT id FROM local_results WHERE agent=? AND cloud_run_at=?",
                (agent, cloud_data.get("run_at"))
            ).fetchone()

            if existing:
                if verbose:
                    logger.info(f"[{agent}] 結果已存在 (id={existing[0]})，跳過")
                return None

            # 存入本地並判定
            row_id = store_result(agent, cloud_data)
            verdict = judge(cloud_data.get("data"), agent)

            if verbose:
                logger.info(f"[{agent}] ✅ 同步成功 (id={row_id})")
                logger.info(f"     判定: {verdict['verdict']}")
                for alert in verdict.get("alerts", []):
                    sev = alert.get("severity", "info")
                    icon = "🔴" if sev == "warning" else "🔵" if sev == "info" else "⚪"
                    logger.info(f"     {icon} {alert['message']}")

            return {"id": row_id, "verdict": verdict}

    except httpx.ConnectError:
        logger.error(f"[{agent}] 無法連接雲端 Server ({CLOUD_URL})")
        return None
    except Exception as e:
        logger.error(f"[{agent}] 同步失敗: {e}")
        return None

async def sync_all(verbose: bool = True) -> Dict:
    """同步所有 Agent"""
    agents = ["it_news", "pc_parts", "msi_monitor", "report"]
    results = {}
    for agent in agents:
        r = await sync_agent(agent, verbose)
        results[agent] = r
    return results

async def watch_mode(interval: int = 300):
    """持續監控模式：每 N 秒輪詢一次"""
    logger.info(f"🔄 監控模式啟動，每 {interval} 秒輪詢一次，Ctrl+C 停止")
    seen_hashes = set()

    # 初始化：讀取已有結果的 hash
    for row in conn.execute("SELECT agent, cloud_run_at FROM local_results"):
        seen_hashes.add((row[0], row[1]))

    while True:
        try:
            agents = ["it_news", "pc_parts", "msi_monitor"]
            for agent in agents:
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        resp = await client.get(f"{CLOUD_URL}/results/{agent}/latest")
                        if resp.status_code != 200:
                            continue
                        cloud_data = resp.json()
                        key = (agent, cloud_data.get("run_at", ""))
                        if key not in seen_hashes:
                            seen_hashes.add(key)
                            row_id = store_result(agent, cloud_data)
                            verdict = judge(cloud_data.get("data"), agent)
                            logger.info(f"🆕 [{agent}] 新結果！id={row_id} | {verdict['verdict']}")
                            for alert in verdict.get("alerts", []):
                                logger.warning(f"   ⚠️ {alert['message']}")
                except Exception as e:
                    logger.debug(f"[{agent}] 輪詢異常: {e}")

            await asyncio.sleep(interval)
        except KeyboardInterrupt:
            logger.info("監控模式已停止")
            break

# ── 報告 ─────────────────────────────────────────────────────────

def generate_local_report(agent: str, days: int = 7) -> str:
    """生成本地 HTML 報告"""
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        """SELECT agent, cloud_run_at, items_count, verdict, alerts
           FROM local_results WHERE agent=? AND cloud_run_at>=?
           ORDER BY id DESC""",
        (agent, since)
    ).fetchall()

    if not rows:
        return f"<p>無 {agent} 歷史數據</p>"

    rows_html = ""
    for r in rows:
        alerts = json.loads(r[4] or "[]")
        alerts_html = "".join(
            f"<li class='alert-{a.get('severity','info')}'>{a['message']}</li>"
            for a in alerts
        )
        rows_html += f"""
        <tr>
            <td>{r[1][:16]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>
            <td><ul>{alerts_html}</ul></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>本地報告 - {agent}</title>
<style>
    body{{font-family:sans-serif;max-width:1100px;margin:0 auto;padding:20px}}
    table{{width:100%;border-collapse:collapse;margin-top:16px}}
    th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
    th{{background:#1a73e8;color:#fff}}
    tr:nth-child(even){{background:#f9f9f9}}
    .alert-warning{{color:#c00}}
    .alert-info{{color:#06c}}
    .kpi{{display:flex;gap:16px;margin:16px 0}}
    .card{{background:#f8f9fa;border-radius:8px;padding:16px;flex:1;text-align:center}}
    .num{{font-size:2em;font-weight:bold;color:#1a73e8}}
</style></head>
<body>
<h1>📊 {agent} 本地報告（近 {days} 天）</h1>
<div class="kpi">
    <div class="card"><div class="num">{len(rows)}</div>執行次數</div>
    <div class="card"><div class="num">{sum(r[2] for r in rows)}</div>總數據量</div>
</div>
<table>
<tr><th>執行時間</th><th>數據量</th><th>判定</th><th>警報</th></tr>
{rows_html}
</table></body></html>"""

    out_path = Path(__file__).resolve().parent.parent / "reports" / f"local_{agent}_{datetime.now().strftime('%Y%m%d')}.html"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"本地報告已保存: {out_path}")
    return str(out_path)

# ── CLI ───────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="本地 Agent Client")
    parser.add_argument("--watch", action="store_true", help="持續監控模式")
    parser.add_argument("--interval", type=int, default=300, help="監控間隔秒數（預設 300）")
    parser.add_argument("--agent", help="只同步指定 Agent")
    parser.add_argument("--days", type=int, default=7, help="報告天數（預設 7）")
    parser.add_argument("--report", action="store_true", help="生成本地 HTML 報告")
    args = parser.parse_args()

    logger.info(f"連接雲端: {CLOUD_URL}")

    if args.watch:
        await watch_mode(args.interval)
    elif args.report:
        for agent in ["it_news", "pc_parts", "msi_monitor"]:
            generate_local_report(agent, args.days)
    elif args.agent:
        await sync_agent(args.agent)
    else:
        results = await sync_all()
        # 顯示摘要
        for agent, r in results.items():
            if r:
                print(f"✅ {agent}: {r['verdict']['verdict']}")

if __name__ == "__main__":
    asyncio.run(main())
