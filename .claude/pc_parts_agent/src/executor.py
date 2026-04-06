"""
PC Parts Agent - 主執行器
"""
import asyncio
import json
import re
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

from core import BaseCrawler, MiniMaxAnalyzer, classify_brand, classify_category
from core import extract_wattage, extract_certification


class JDCrawler(BaseCrawler):
    """京東電商爬蟲"""

    async def crawl(self, **kwargs) -> List[Dict]:
        keyword = kwargs.get("keyword", "RTX 4090 顯卡")
        page = kwargs.get("page", 1)
        url = f"https://search.jd.com/Search?keyword={keyword}&enc=utf-8&wq={keyword}&page={page}"

        html = await self.async_http_get(url)
        if not html:
            return []

        soup = self.parse_html(html)
        items = []
        for gl_item in soup.select(".gl-item")[:20]:
            try:
                title_el = gl_item.select_one(".p-name em, .p-name a")
                price_el = gl_item.select_one(".p-price i, .p-price strong i")
                brand = classify_brand(self.extract_text(title_el))

                title = self.extract_text(title_el)
                price = self.extract_float(self.extract_text(price_el))
                product_id = gl_item.get("data-sku", "")
                link = f"https://item.jd.com/{product_id}.html"

                if title and price:
                    items.append({
                        "model_name": title,
                        "brand": brand or "Other",
                        "category": classify_category(title),
                        "price": price,
                        "currency": "CNY",
                        "source": "JD",
                        "product_id": product_id or hashlib.md5(title.encode()).hexdigest()[:12],
                        "url": link,
                        "wattage": extract_wattage(title),
                        "certification": extract_certification(title),
                    })
            except Exception as e:
                logger.debug(f"解析京東商品失敗: {e}")
        return items


class AmazonCrawler(BaseCrawler):
    """Amazon US 爬蟲"""

    async def crawl(self, **kwargs) -> List[Dict]:
        keyword = kwargs.get("keyword", "RTX 4090")
        url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"

        html = await self.async_http_get(url)
        if not html:
            return []

        soup = self.parse_html(html)
        items = []
        for result in soup.select("[data-component-type='s-search-result']")[:20]:
            try:
                title_el = result.select_one("h2 a span, a span.a-size-medium")
                price_el = result.select_one(".a-price .a-offscreen, .a-offscreen")
                brand_el = result.select_one(".a-size-base-plus, .a-color-secondary")

                title = self.extract_text(title_el)
                price_text = self.extract_text(price_el)
                price = self.clean_price(price_text)
                link = result.select_one("h2 a").get("href", "") if result.select_one("h2 a") else ""
                if link and not link.startswith("http"):
                    link = "https://www.amazon.com" + link

                if title:
                    items.append({
                        "model_name": title,
                        "brand": classify_brand(title),
                        "category": classify_category(title),
                        "price": price or 0,
                        "currency": "USD",
                        "source": "Amazon",
                        "product_id": hashlib.md5(title.encode()).hexdigest()[:12],
                        "url": link,
                    })
            except Exception as e:
                logger.debug(f"解析 Amazon 失敗: {e}")
        return items


class PcPartsExecutor:
    """PC Parts Agent 主執行器"""

    def __init__(self, cfg: Dict):
        self.cfg = cfg
        self.analyzer = MiniMaxAnalyzer(cfg.get("ai", {}))
        self.today_str = datetime.now().strftime("%Y%m%d")
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / cfg.get("reporting", {}).get("data_dir", "data")
        self.reports_dir = self.base_dir / cfg.get("reporting", {}).get("output_dir", "reports")
        self.db_path = self.base_dir / cfg.get("database", {}).get("path", "data/price_history.db")
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.db_path.parent.mkdir(exist_ok=True)
        self.items: List[Dict] = []

    def init_db(self):
        """初始化 SQLite 數據庫"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                model_name TEXT,
                brand TEXT,
                category TEXT,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'CNY',
                source TEXT,
                wattage TEXT,
                certification TEXT,
                url TEXT,
                recorded_at TEXT NOT NULL,
                UNIQUE(product_id, source, recorded_at)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT UNIQUE,
                model_name TEXT,
                threshold REAL,
                last_price REAL,
                alert_type TEXT DEFAULT 'drop',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        return conn

    async def collect(self) -> List[Dict]:
        """並行收集電商數據"""
        logger.info("開始收集 PC 零組件價格...")
        conn = self.init_db()

        crawlers = []
        for source_name, source_cfg in self.cfg.get("sources", {}).items():
            if not source_cfg.get("enabled"):
                continue
            keywords = source_cfg.get("keywords", [])
            for keyword in keywords[:3]:
                if source_name == "jd":
                    crawlers.append(JDCrawler(self.cfg.get("crawling", {})))
                elif source_name == "amazon":
                    crawlers.append(AmazonCrawler(self.cfg.get("crawling", {})))

        tasks = []
        for crawler in crawlers:
            keyword = kwargs.get("keywords", ["RTX 4090"])[0] if hasattr(crawler, 'keyword') else "GPU"
            tasks.append(crawler.run(keyword=keyword))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_items = []
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"爬蟲異常: {result}")

        # Save to DB
        now = datetime.now().isoformat()
        for item in all_items:
            item["recorded_at"] = now
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO price_history
                    (product_id, model_name, brand, category, price, currency, source, wattage, certification, url, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item["product_id"], item["model_name"], item["brand"],
                    item["category"], item["price"], item.get("currency", "CNY"),
                    item["source"], item.get("wattage"), item.get("certification"),
                    item.get("url", ""), item["recorded_at"]
                ))
            except Exception as e:
                logger.debug(f"寫入 DB 失敗: {e}")

        conn.commit()
        conn.close()

        self.items = all_items
        logger.info(f"收集完成: {len(all_items)} 條記錄")
        return all_items

    def analyze_prices(self) -> Dict:
        """分析價格趨勢"""
        conn = sqlite3.connect(str(self.db_path))

        # Recent prices
        df_recent = conn.execute("""
            SELECT brand, category, source, AVG(price) as avg_price, COUNT(*) as cnt
            FROM price_history
            WHERE recorded_at >= date('now', '-7 days')
            GROUP BY brand, category, source
        """).fetchall()

        # 30-day average
        df_30day = conn.execute("""
            SELECT product_id, model_name, AVG(price) as avg_price
            FROM price_history
            WHERE recorded_at >= date('now', '-30 days')
            GROUP BY product_id
        """).fetchall()
        avg_30day = {r[0]: r[2] for r in df_30day}

        conn.close()

        analysis = {
            "date": self.today_str,
            "recent_stats": [
                {"brand": r[0], "category": r[1], "source": r[2], "avg_price": round(r[3], 2), "count": r[4]}
                for r in df_recent
            ],
            "price_changes": [],
            "generated_at": datetime.now().isoformat(),
        }

        # Compare recent vs 30-day average
        recent_map = {r[0]: r[3] for r in df_recent}
        for product_id, avg_price in avg_30day.items():
            if product_id in recent_map:
                change = (recent_map[product_id] - avg_price) / avg_price * 100
                if abs(change) > 5:
                    analysis["price_changes"].append({
                        "product_id": product_id,
                        "change_pct": round(change, 1),
                        "trend": "up" if change > 0 else "down",
                    })

        return analysis

    def check_alerts(self) -> List[Dict]:
        """檢查價格提醒"""
        conn = sqlite3.connect(str(self.db_path))
        threshold_pct = self.cfg.get("alerts", {}).get("price_drop_threshold", 0.10)

        alerts = []
        recent = conn.execute("""
            SELECT product_id, model_name, brand, MIN(price) as min_price
            FROM price_history
            WHERE recorded_at >= date('now', '-1 days')
            GROUP BY product_id
        """).fetchall()

        historical = conn.execute("""
            SELECT product_id, AVG(price) as avg_price
            FROM price_history
            WHERE recorded_at >= date('now', '-30 days')
            AND recorded_at < date('now', '-1 days')
            GROUP BY product_id
        """).fetchall()
        hist_map = {r[0]: r[1] for r in historical}

        for product_id, model_name, brand, min_price in recent:
            if product_id in hist_map:
                avg = hist_map[product_id]
                drop = (avg - min_price) / avg
                if drop >= threshold_pct:
                    alerts.append({
                        "product_id": product_id,
                        "model_name": model_name,
                        "brand": brand,
                        "current_price": min_price,
                        "avg_price_30d": round(avg, 2),
                        "drop_pct": round(drop * 100, 1),
                        "trend": "down",
                    })

        conn.close()
        return alerts

    def save_data(self) -> str:
        path = self.data_dir / f"prices_{self.today_str}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "date": self.today_str,
                "items": self.items,
                "collected_at": datetime.now().isoformat(),
                "total": len(self.items),
            }, f, ensure_ascii=False, indent=2)
        return str(path)

    def generate_report(self, analysis: Dict, alerts: List[Dict]) -> str:
        """生成 HTML 價格報告"""
        alert_rows = ""
        for a in alerts[:10]:
            alert_rows += f"""
            <tr>
                <td>{a['brand']}</td>
                <td>{a['model_name'][:40]}</td>
                <td>¥{a['current_price']:.0f}</td>
                <td>¥{a['avg_price_30d']:.0f}</td>
                <td class="{'down' if a['drop_pct'] > 0 else 'up'}">{a['drop_pct']}%</td>
            </tr>"""

        stats_rows = ""
        for s in analysis.get("recent_stats", []):
            stats_rows += f"""
            <tr>
                <td>{s['brand']}</td>
                <td>{s['category']}</td>
                <td>{s['source']}</td>
                <td>¥{s['avg_price']:.0f}</td>
                <td>{s['count']}</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>DIY PC 零組件價格報告 {self.today_str}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }}
        th {{ background: #11998e; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f5f5f5; }}
        .down {{ color: #e74c3c; font-weight: bold; }}
        .up {{ color: #27ae60; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DIY PC 零組件價格報告</h1>
            <p>{self.today_str} | 共 {len(self.items)} 條記錄</p>
        </div>

        <div class="card">
            <h2>📉 價格提醒 (降價 ≥10%)</h2>
            <table>
                <tr><th>品牌</th><th>型號</th><th>現價</th><th>30日均價</th><th>降幅</th></tr>
                {alert_rows or '<tr><td colspan="5">暫無價格提醒</td></tr>'}
            </table>
        </div>

        <div class="card">
            <h2>📊 品牌/類別 價格統計</h2>
            <table>
                <tr><th>品牌</th><th>類別</th><th>來源</th><th>均價</th><th>數量</th></tr>
                {stats_rows or '<tr><td colspan="5">暫無數據</td></tr>'}
            </table>
        </div>
    </div>
</body>
</html>"""

        path = self.reports_dir / f"price_report_{self.today_str}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"價格報告已生成: {path}")
        return str(path)

    async def run(self, mode: str = "full") -> Dict:
        logger.info(f"PC Parts Agent 啟動，模式: {mode}")
        result = {"status": "success"}

        try:
            if mode in ("full", "collect"):
                await self.collect()
                self.save_data()

            if mode in ("full", "analyze"):
                if not self.items:
                    await self.collect()
                analysis = self.analyze_prices()
                alerts = self.check_alerts()
                report_path = self.generate_report(analysis, alerts)
                result["analysis"] = analysis
                result["alerts_count"] = len(alerts)
                result["report_path"] = report_path

            if mode == "alert":
                alerts = self.check_alerts()
                result["alerts"] = alerts

        except Exception as e:
            logger.error(f"執行失敗: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        return result
