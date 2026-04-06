"""
全球 PSU 市場 AI 分析器
使用 MiniMax API 對全球電商平台數據進行深度分析
"""

import httpx
import logging
from datetime import date, datetime
from typing import Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class GlobalAnalyzer:
    """全球市場 AI 分析器"""

    def __init__(self, config: dict):
        mm_cfg = config.get("minimax", {})
        self.api_key = mm_cfg.get("api_key", "")
        self.base_url = mm_cfg.get("base_url", "https://api.minimax.chat/v1")
        self.model = mm_cfg.get("model", "MiniMax-Text-01")
        self.max_tokens = mm_cfg.get("max_tokens", 8192)
        self.temperature = 0.7

    def analyze(self, products: list[dict], today_str: str = "") -> str:
        """執行完整分析"""
        if not products:
            return "⚠️ 今日無收集到任何商品數據，分析報告無法生成。"

        today_str = today_str or date.today().isoformat()

        # 1. 本地統計
        stats = self._compute_statistics(products)

        # 2. 構建提示詞
        prompt = self._build_global_prompt(products, stats, today_str)

        # 3. 呼叫 AI 或本地統計
        if self.api_key and self.api_key != "YOUR_MINIMAX_API_KEY_HERE":
            try:
                return self._call_api(prompt)
            except Exception as e:
                logger.error(f"MiniMax API 失敗: {e}，使用本地統計: {e}")
                return self._build_local_report(stats, today_str)
        else:
            logger.info("未設定 MiniMax API Key，使用本地統計分析")
            return self._build_local_report(stats, today_str)

    def _compute_statistics(self, products: list[dict]) -> dict:
        """計算全局統計數據"""
        stats = {
            "total": len(products),
            "by_region": defaultdict(int),
            "by_brand": defaultdict(int),
            "by_platform": defaultdict(int),
            "by_wattage": defaultdict(int),
            "by_certification": defaultdict(int),
            "price_ranges": [],
            "products_with_price": 0,
            "total_price_usd": 0.0,
            "top_rated": [],
        }

        for p in products:
            stats["by_region"][p.get("region", "Unknown")] += 1
            stats["by_brand"][p.get("brand", "Unknown")] += 1
            stats["by_platform"][p.get("platform", "Unknown")] += 1

            wattage = p.get("wattage") or ""
            if wattage:
                # 正規化瓦數（提取數字部分）
                import re
                wm = re.search(r'(\d+)', wattage)
                if wm:
                    w = int(wm.group(1))
                    if w <= 300:
                        bucket = f"{w}W"
                    elif w <= 600:
                        bucket = f"{w}W"
                    elif w <= 1000:
                        bucket = f"{w}W"
                    else:
                        bucket = f"{w}W+"
                    stats["by_wattage"][bucket] += 1

            cert = p.get("certification") or ""
            if cert:
                stats["by_certification"][cert] += 1

            price = p.get("price")
            if price is not None:
                try:
                    pv = float(price)
                    stats["price_ranges"].append(pv)
                    stats["total_price_usd"] += pv
                    stats["products_with_price"] += 1
                except (ValueError, TypeError):
                    pass

        # 平均價格
        if stats["products_with_price"] > 0:
            stats["avg_price_usd"] = stats["total_price_usd"] / stats["products_with_price"]
        else:
            stats["avg_price_usd"] = 0

        return stats

    def _build_global_prompt(self, products: list[dict], stats: dict, today_str: str) -> str:
        """構建全球市場分析提示詞"""

        # 按品牌分組，取代表性商品
        by_brand = defaultdict(list)
        for p in products:
            by_brand[p.get("brand", "Unknown")].append(p)

        brand_blocks = []
        for brand, items in sorted(by_brand.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            top_items = items[:3]
            prices = [p.get("price") for p in items if p.get("price") is not None]
            avg_p = sum(prices) / len(prices) if prices else 0
            regions = set(p.get("region", "") for p in items)

            block = f"\n【{brand}】({len(items)} 個商品，均價 ${avg_p:.0f} USD)\n"
            block += f"  地區: {', '.join(sorted(regions))}\n"
            for item in top_items:
                name = (item.get("product_name") or "")[:60]
                price = item.get("price") or "N/A"
                platform = item.get("platform", "")
                block += f"  - {name}\n    💰 ${price} | 📍 {platform}\n"
            brand_blocks.append(block)

        brands_section = "\n".join(brand_blocks)

        # 區域概況
        region_blocks = []
        for region, count in sorted(stats["by_region"].items(), key=lambda x: x[1], reverse=True):
            region_pct = count / stats["total"] * 100
            region_blocks.append(f"  {region}: {count} ({region_pct:.1f}%)")
        region_section = "\n".join(region_blocks)

        # 瓦數分布
        wattage_blocks = []
        for w, cnt in sorted(stats["by_wattage"].items(), key=lambda x: x[1], reverse=True)[:8]:
            wattage_blocks.append(f"  {w}: {cnt} 個商品")
        wattage_section = "\n".join(wattage_blocks) or "  （數據不足）"

        # 平台分布
        platform_blocks = []
        for platform, count in sorted(stats["by_platform"].items(), key=lambda x: x[1], reverse=True)[:15]:
            pct = count / stats["total"] * 100
            platform_blocks.append(f"  {platform}: {count} ({pct:.1f}%)")
        platform_section = "\n".join(platform_blocks)

        prompt = f"""
你是全球電源供應器（PSU）市場分析師。请根據以下今日（{today_str}）全球電商平台實際銷售數據，撰寫一份專業的全球市場分析報告。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【數據概況】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
總計收集商品：{stats['total']} 個
平均價格：${stats['avg_price_usd']:.1f} USD（均已換算為美元）
覆蓋地區：{len(stats['by_region'])} 個
覆蓋平台：{len(stats['by_platform'])} 個
收集時間：{datetime.now().strftime('%H:%M')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【各地區分佈】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{region_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【各平台 TOP 15】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{platform_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【各品牌商品詳情】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{brands_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【熱門瓦數分布】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{wattage_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

請分析並回覆以下維度（使用繁體中文）：

## 1. 全球市場總覽
   - 全球 PSU 市場的整體價格區間分佈
   - 各區域市場（北美/歐洲/俄羅斯/亞洲/南美/中東）的市場規模對比

## 2. 區域市場分析
   【台灣市場】PChome、Momo 的價格水平與熱門品牌
   【日本市場】Amazon JP、Rakuten 的產品結構特點
   【韓國市場】Gmarket、Coupang 的市場概況
   【印度市場】Flipkart、Amazon.in 的價格競爭力
   【歐洲市場】Amazon DE/UK、MediaMarkt 的價格 vs 其他區域
   【俄羅斯市場】Wildberries、Ozon 的供應情況

## 3. 品牌競爭分析
   - 對比各品牌在全球各區域的市場存在度（哪些品牌佈局最廣）
   - 各品牌的價格定位（低端/中端/高端）
   - 性價比分析

## 4. 產品規格趨勢
   - 主流瓦數段（550W/650W/750W/850W/1000W+）在全球的分佈
   - 80+ 認證等級的普及情況
   - 全模組/半模組產品的比例

## 5. 價格波動與促銷洞察
   - 發現任何異常低價或高價產品
   - 哪些平台/地區出現價格促銷跡象

## 6. 區域市場差異總結
   - 各區域市場的用戶偏好差異
   - 台灣、日本、韓國、印度市場的獨特觀察
   - 跨境價格套利機會（如有）

## 7. 關鍵洞察與建議
   - 本日最重要的 3-5 個市場洞察
   - 針對每個重點品牌的策略建議

請用繁體中文撰寫，語氣專業，適合管理層閱讀。
所有結論需有明確的數據支撐。
"""
        return prompt.strip()

    def _call_api(self, prompt: str) -> str:
        """呼叫 MiniMax API"""
        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        with httpx.Client(timeout=120) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return "⚠️ AI 分析服務暫時無法回覆，請稍後重試。"

    def _build_local_report(self, stats: dict, today_str: str) -> str:
        """本地統計分析（無 AI API 時）"""
        lines = [f"# 🌍 全球 PSU 市場每日快報 — {today_str}\n"]
        lines.append(f"_（說明：未設定 MiniMax API Key，以下為本地統計分析）_\n")

        # 地區分布
        lines.append("## 📍 各地區覆蓋\n")
        lines.append("| 地區 | 商品數 | 佔比 |")
        lines.append("|------|--------|------|")
        for region, count in sorted(stats["by_region"].items(), key=lambda x: x[1], reverse=True):
            pct = count / stats["total"] * 100
            lines.append(f"| {region} | {count} | {pct:.1f}% |")

        # 品牌分布
        lines.append("\n## 🏷️ 各品牌覆蓋\n")
        lines.append("| 品牌 | 商品數 |")
        lines.append("|------|--------|")
        for brand, count in sorted(stats["by_brand"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| {brand} | {count} |")

        # 平台分布
        lines.append("\n## 🛒 各平台覆蓋（TOP 15）\n")
        lines.append("| 平台 | 商品數 | 佔比 |")
        lines.append("|------|--------|------|")
        for platform, count in sorted(stats["by_platform"].items(), key=lambda x: x[1], reverse=True)[:15]:
            pct = count / stats["total"] * 100
            lines.append(f"| {platform} | {count} | {pct:.1f}% |")

        # 瓦數分布
        if stats["by_wattage"]:
            lines.append("\n## ⚡ 熱門瓦數分布\n")
            for w, cnt in sorted(stats["by_wattage"].items(), key=lambda x: x[1], reverse=True)[:8]:
                lines.append(f"- **{w}**：{cnt} 個商品")

        # 價格概況
        lines.append(f"\n## 💰 價格概況\n")
        prices = sorted(stats["price_ranges"])
        if prices:
            lines.append(f"- 均價：${stats['avg_price_usd']:.1f} USD")
            lines.append(f"- 最低：${min(prices):.1f} USD")
            lines.append(f"- 最高：${max(prices):.1f} USD")

        # 認證分布
        if stats["by_certification"]:
            lines.append("\n## 🔖 80+ 認證分布\n")
            for cert, cnt in sorted(stats["by_certification"].items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- {cert}：{cnt} 個商品")

        lines.append(f"\n---\n")
        lines.append(f"_報告生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
        lines.append(f"\n_⚠️ 此為本地統計報告，設定 MiniMax API Key 可獲得 AI 深度分析_")
        return "\n".join(lines)
