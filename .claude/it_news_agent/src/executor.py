"""
IT News Agent - 主執行器
使用已確認可用的 RSS Feeds:
  - TechCrunch /feed/         (application/rss+xml)
  - Tom's Hardware /rss/      (application/xml)
  - CNET /rss/news/          (text/xml)
  - The Verge /rss/index.xml  (application/xml)
  - IT之家 /rss/              (text/xml, gzip 中文)
"""
import asyncio
import json
import re
import hashlib
import feedparser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

from core import BaseCrawler, MiniMaxAnalyzer
from core import classify_news_category


# ── RSS Crawler ───────────────────────────────────────────────────

class RSSCrawler(BaseCrawler):
    """通用 RSS/Atom feed 爬蟲，支援 gzip 壓縮回應"""

    def __init__(self, source_name: str, config: Optional[Dict] = None):
        super().__init__(config)
        self.source_name = source_name
        self.feed_url: Optional[str] = None

    async def crawl(self, **kwargs) -> List[Dict]:
        url = kwargs.get("url") or self.feed_url
        if not url:
            logger.warning(f"[{self.source_name}] 未配置 RSS URL")
            return []

        html = await self.async_http_get(url)
        if not html:
            return []

        try:
            feed = feedparser.parse(html)
            if not feed.entries:
                logger.warning(f"[{self.source_name}] feed.entries=0 (html.len={len(html)})")
                return []

            items = []
            for entry in feed.entries[:15]:
                title = getattr(entry, "title", "") or ""
                link = getattr(entry, "link", "") or ""
                summary = (
                    getattr(entry, "summary", "")
                    or getattr(entry, "description", "")
                    or ""
                )
                pub_time = ""
                pub = getattr(entry, "published", "") or getattr(entry, "updated", "")
                if pub:
                    pub_time = pub[:16] if len(pub) >= 16 else pub
                summary = re.sub(r"<[^>]+>", "", summary)[:200].strip()

                if title:
                    items.append({
                        "title": title.strip(),
                        "url": link.strip(),
                        "source": self.source_name,
                        "published_at": pub_time,
                        "summary": summary,
                    })

            logger.info(f"[{self.source_name}] 解析到 {len(items)} 篇文章")
            return items

        except Exception as e:
            logger.error(f"[{self.source_name}] RSS 解析失敗: {e}")
            return []


# ── Site crawlers (全部使用確認可用的 feed URL) ───────────────────

class TechCrunchCrawler(RSSCrawler):
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("TechCrunch", config)
        self.feed_url = "https://techcrunch.com/feed/"


class TomshardwareCrawler(RSSCrawler):
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("Tom's Hardware", config)
        self.feed_url = "https://www.tomshardware.com/rss/"


class CNETCrawler(RSSCrawler):
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("CNET", config)
        self.feed_url = "https://www.cnet.com/rss/news/"


class TheVergeCrawler(RSSCrawler):
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("The Verge", config)
        self.feed_url = "https://www.theverge.com/rss/index.xml"


class IthomeCrawler(RSSCrawler):
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("IT之家", config)
        self.feed_url = "https://www.ithome.com/rss/"


# ── Executor ─────────────────────────────────────────────────────

class ItNewsExecutor:
    def __init__(self, cfg: Dict):
        self.cfg = cfg
        self.analyzer = MiniMaxAnalyzer(cfg.get("ai", {}))
        self.today_str = datetime.now().strftime("%Y%m%d")
        base_dir = Path(__file__).parent.parent
        self.data_dir = base_dir / cfg.get("reporting", {}).get("data_dir", "data")
        self.reports_dir = base_dir / cfg.get("reporting", {}).get("output_dir", "reports")
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

    _CRAWLERS = {
        "techcrunch": TechCrunchCrawler,
        "tomshardware": TomshardwareCrawler,
        "cnet": CNETCrawler,
        "theverge": TheVergeCrawler,
        "ithome": IthomeCrawler,
    }

    # ── Phase 1: collect ────────────────────────────────────────

    async def collect(self) -> Dict:
        sources = self.cfg.get("sources", {})
        crawling_cfg = self.cfg.get("crawling", {})

        tasks, names = [], []
        for key, src in sources.items():
            if not src.get("enabled", True):
                continue
            cls = self._CRAWLERS.get(key)
            if cls is None:
                continue
            tasks.append(self._run(cls, crawling_cfg, src))
            names.append(src.get("name", key))

        logger.info(f"開始收集 {len(tasks)} 個來源: {', '.join(names)}")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_items = []
        for r in results:
            if isinstance(r, list):
                all_items.extend(r)
            elif isinstance(r, Exception):
                logger.error(f"來源執行異常: {r}")

        # 去重
        seen, unique = set(), []
        for item in all_items:
            h = hashlib.md5((item["title"] + item["url"]).encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                unique.append(item)

        for item in unique:
            item["category"] = classify_news_category(
                item.get("title", "") + " " + item.get("summary", "")
            )

        logger.info(f"收集完成: {len(unique)} 篇")
        return {"items": unique}

    async def _run(self, cls, crawling_cfg, src) -> List[Dict]:
        crawler = cls(crawling_cfg)
        logger.info(f"  來源: {src.get('name', '')}")
        try:
            await crawler.run()
            return crawler.results
        except Exception as e:
            logger.error(f"  [{cls.__name__}] 執行失敗: {e}")
            return []

    # ── Phase 2: brief ──────────────────────────────────────────

    async def generate_brief(self, data: Dict) -> Dict:
        items = data.get("items", [])
        if not items:
            return {"brief": "今日無新聞數據。", "stats": {}}

        brief = self.analyzer.summarize_news(items)
        stats = {"total": len(items), "by_category": {}, "by_source": {}}
        for item in items:
            stats["by_source"][item["source"]] = stats["by_source"].get(item["source"], 0) + 1
            cat = item.get("category", "General")
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

        return {"brief": brief, "stats": stats}

    # ── Phase 3: save ───────────────────────────────────────────

    async def save_data(self, data: Dict) -> str:
        path = self.data_dir / f"news_{self.today_str}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"數據已保存: {path}")
        return str(path)

    async def save_html_report(self, data: Dict) -> str:
        items = data.get("items", [])
        brief_data = data.get("brief_data", {})
        stats = brief_data.get("stats", {})
        brief = brief_data.get("brief", "")

        rows = ""
        for item in items[:20]:
            rows += f"""<li class="news-item">
    <a href="{item['url']}" target="_blank">{item['title']}</a>
    <div class="meta">{item['source']} | {item.get('published_at','')} | <span class="tag">{item.get('category','')}</span></div>
  </li>"""

        html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>IT 新聞簡報 {self.today_str}</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
  h1 {{ border-bottom: 2px solid #1a73e8; padding-bottom: 8px; }}
  .kpi {{ display: flex; gap: 16px; margin: 16px 0; }}
  .kpi .card {{ background: #f8f9fa; border-radius: 8px; padding: 16px; flex: 1; text-align: center; }}
  .kpi .num {{ font-size: 2em; font-weight: bold; color: #1a73e8; }}
  .news-list {{ list-style: none; padding: 0; }}
  .news-item {{ border-bottom: 1px solid #eee; padding: 12px 0; }}
  .news-item a {{ color: #1a73e8; text-decoration: none; font-weight: 500; }}
  .news-item .meta {{ font-size: 0.85em; color: #888; margin-top: 4px; }}
  .tag {{ background: #e8f0fe; color: #1a73e8; border-radius: 4px; padding: 2px 8px; font-size: 0.8em; }}
  blockquote {{ background: #f8f9fa; border-left: 4px solid #1a73e8; padding: 12px; margin: 16px 0; }}
</style>
</head>
<body>
<h1>IT 新聞簡報 {self.today_str}</h1>
<div class="kpi"><div class="card"><div class="num">{stats.get('total', 0)}</div>總文章數</div></div>
<h2>AI 摘要</h2>
<blockquote>{brief}</blockquote>
<h2>來源分佈</h2>
<p>""" + " ".join(
            f'<span class="tag">{k}: {v}</span>' for k, v in stats.get("by_source", {}).items()
        ) + f"""</p>
<h2>最新新聞</h2>
<ul class="news-list">{rows}</ul>
</body></html>"""

        path = self.reports_dir / f"news_brief_{self.today_str}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"HTML 報告已保存: {path}")
        return str(path)

    # ── Main ────────────────────────────────────────────────────

    async def run(self, mode: str = "full") -> Dict:
        logger.info(f"IT News Agent 啟動，模式: {mode}")

        if mode == "collect":
            data = await self.collect()
            await self.save_data(data)
            return {"status": "success", "items": len(data.get("items", []))}

        data = await self.collect()
        brief_data = await self.generate_brief(data)
        data["brief_data"] = brief_data
        await self.save_data(data)
        await self.save_html_report(data)
        return {"status": "success", "stats": brief_data.get("stats", {})}
