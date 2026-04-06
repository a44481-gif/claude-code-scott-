"""
MSI Monitor Agent - 主執行器
"""
import asyncio
import json
import re
import hashlib
import feedparser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

from core import BaseCrawler, MsiUpdate


class MsiOfficialCrawler(BaseCrawler):
    """MSI 官網爬蟲"""

    async def crawl(self, **kwargs) -> List[Dict]:
        url = kwargs.get("url", "https://www.msi.com/news")
        html = await self.async_http_get(url)
        if not html:
            return []

        soup = self.parse_html(html)
        items = []

        # News items
        for article in soup.select(".news-list-item, .article-item, .news-item")[:15]:
            try:
                title_el = article.select_one("h3 a, .title a, a.title")
                date_el = article.select_one(".date, .time, span.date")
                desc_el = article.select_one(".desc, .summary, .excerpt")

                title = self.extract_text(title_el)
                link = title_el.get("href", "") if title_el else ""
                if link and not link.startswith("http"):
                    link = "https://www.msi.com" + link

                if title:
                    items.append({
                        "title": title,
                        "url": link,
                        "source": "msi_official",
                        "published_at": self.extract_text(date_el),
                        "description": self.extract_text(desc_el),
                        "update_type": self._detect_type(title),
                    })
            except Exception as e:
                logger.debug(f"解析 MSI 官網失敗: {e}")
        return items

    def _detect_type(self, title: str) -> str:
        title_lower = title.lower()
        if any(k in title_lower for k in ["driver", "驅動"]):
            return "driver_update"
        if any(k in title_lower for k in ["bios", "firmware", "韌體"]):
            return "BIOS"
        if any(k in title_lower for k in ["new product", "新產品", "launch", "發布"]):
            return "new_product"
        return "news"


class MsiRSSReader(BaseCrawler):
    """MSI RSS 訂閱讀取"""

    async def crawl(self, **kwargs) -> List[Dict]:
        feed_url = kwargs.get("url", "https://www.msi.com/rss/news.xml")
        try:
            import feedparser
            feed = feedparser.parse(feed_url)
            items = []
            for entry in feed.entries[:15]:
                items.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": "msi_rss",
                    "published_at": entry.get("published", ""),
                    "description": entry.get("summary", entry.get("description", ""))[:200],
                    "update_type": "news",
                })
            return items
        except Exception as e:
            logger.error(f"RSS 解析失敗: {e}")
            return []


class MsiMonitorExecutor:
    """MSI Monitor Agent 主執行器"""

    def __init__(self, cfg: Dict):
        self.cfg = cfg
        self.today_str = datetime.now().strftime("%Y%m%d")
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / cfg.get("reporting", {}).get("data_dir", "data")
        self.reports_dir = self.base_dir / cfg.get("reporting", {}).get("output_dir", "reports")
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.items: List[Dict] = []

    async def collect(self) -> List[Dict]:
        """並行收集所有 MSI 頻道"""
        logger.info("開始收集 MSI 更新...")
        channels = self.cfg.get("channels", {})

        tasks = []

        # MSI Official
        if channels.get("msi_official", {}).get("enabled"):
            urls = channels["msi_official"].get("urls", {})
            for section, url in urls.items():
                crawler = MsiOfficialCrawler(self.cfg.get("crawling", {}))
                tasks.append(crawler.run(url=url))
                logger.info(f"  爬取 MSI 官網: {section}")

        # RSS Feeds
        if channels.get("rss_feeds", {}).get("enabled"):
            for feed_url in channels["rss_feeds"].get("feeds", []):
                reader = MsiRSSReader(self.cfg.get("crawling", {}))
                tasks.append(reader.run(url=feed_url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_items = []
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"爬蟲異常: {result}")

        # Deduplicate
        seen = set()
        unique = []
        for item in all_items:
            h = hashlib.md5(item["title"].encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                unique.append(item)

        self.items = unique
        logger.info(f"收集完成: {len(unique)} 條記錄")
        return unique

    def diff_updates(self) -> Dict:
        """比對新舊更新，找出新增項目"""
        prev_path = self.data_dir / f"msi_updates_{self._yesterday()}.json"
        curr_items = {i["url"]: i for i in self.items}

        new_items = []
        if prev_path.exists():
            with open(prev_path) as f:
                prev_data = json.load(f)
            prev_items = {i["url"]: i for i in prev_data.get("items", [])}

            for url, item in curr_items.items():
                if url not in prev_items:
                    new_items.append(item)
        else:
            new_items = list(curr_items.values())

        by_type = {}
        for item in new_items:
            t = item.get("update_type", "news")
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(item)

        return {
            "date": self.today_str,
            "total_items": len(self.items),
            "new_items": new_items,
            "new_count": len(new_items),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "generated_at": datetime.now().isoformat(),
        }

    def _yesterday(self) -> str:
        from datetime import timedelta
        return (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

    def save_data(self) -> str:
        path = self.data_dir / f"msi_updates_{self.today_str}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "date": self.today_str,
                "items": self.items,
                "collected_at": datetime.now().isoformat(),
                "total": len(self.items),
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"數據已保存: {path}")
        return str(path)

    def generate_report(self, diff: Dict) -> str:
        """生成 HTML 報告"""
        update_type_names = self.cfg.get("update_types", {})

        type_sections = ""
        for utype, items in self._group_by_type(diff["new_items"]).items():
            type_name = update_type_names.get(utype, utype)
            items_html = ""
            for item in items[:10]:
                items_html += f"""
                <div class="item">
                    <h3><a href="{item['url']}" target="_blank">{item['title']}</a></h3>
                    <span class="meta">{item.get('source', '')} | {item.get('published_at', '')}</span>
                    <p>{item.get('description', '')[:150]}</p>
                </div>"""
            type_sections += f"""
            <div class="type-section">
                <h2>{type_name} ({len(items)})</h2>
                {items_html}
            </div>"""

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>MSI 產品監控報告 {self.today_str}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .stats {{ display: flex; gap: 20px; margin-top: 15px; }}
        .stat {{ background: rgba(255,255,255,0.15); padding: 10px 20px; border-radius: 6px; }}
        .stat .num {{ font-size: 28px; font-weight: bold; }}
        .stat .label {{ font-size: 12px; opacity: 0.8; }}
        .type-section {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }}
        .type-section h2 {{ color: #e74c3c; border-bottom: 2px solid #e74c3c; padding-bottom: 8px; margin-bottom: 15px; }}
        .item {{ padding: 12px; margin: 8px 0; background: #f8f9fa; border-radius: 6px; border-left: 3px solid #e74c3c; }}
        .item h3 {{ margin: 0 0 5px; font-size: 16px; }}
        .item h3 a {{ color: #1a1a2e; text-decoration: none; }}
        .item h3 a:hover {{ color: #e74c3c; }}
        .item .meta {{ font-size: 12px; color: #888; }}
        .item p {{ margin: 5px 0 0; font-size: 13px; color: #666; }}
        .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MSI 產品監控報告</h1>
            <p>{self.today_str}</p>
            <div class="stats">
                <div class="stat"><div class="num">{diff['total_items']}</div><div class="label">總記錄</div></div>
                <div class="stat"><div class="num">{diff['new_count']}</div><div class="label">新增</div></div>
            </div>
        </div>
        {type_sections or '<p style="padding:20px">暫無新增更新</p>'}
        <div class="footer"><p>由 AI Business Intelligence Platform - MSI Monitor Agent 自動生成</p></div>
    </div>
</body>
</html>"""

        path = self.reports_dir / f"msi_report_{self.today_str}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"MSI 報告已生成: {path}")
        return str(path)

    def _group_by_type(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        groups = {}
        for item in items:
            t = item.get("update_type", "news")
            if t not in groups:
                groups[t] = []
            groups[t].append(item)
        return groups

    async def run(self, mode: str = "full") -> Dict:
        logger.info(f"MSI Monitor Agent 啟動，模式: {mode}")
        result = {"status": "success"}

        try:
            if mode in ("full", "collect"):
                await self.collect()
                self.save_data()

            if mode in ("full", "diff", "report"):
                if not self.items:
                    await self.collect()
                diff = self.diff_updates()
                report_path = self.generate_report(diff)
                result["diff"] = diff
                result["new_count"] = diff["new_count"]
                result["report_path"] = report_path

        except Exception as e:
            logger.error(f"執行失敗: {e}")
            result["status"] = "failed"
            result["error"] = str(e)

        return result
