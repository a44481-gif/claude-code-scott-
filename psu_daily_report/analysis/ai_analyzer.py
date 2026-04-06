"""
MiniMax AI 分析模組
使用 MiniMax API 對 PSU 銷售數據進行深度分析
"""

import httpx
import json
import logging
from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AnalysisConfig:
    api_key: str
    base_url: str = "https://api.minimax.chat/v1"
    model: str = "MiniMax-Text-01"
    max_tokens: int = 4096
    temperature: float = 0.7


class MiniMaxAnalyzer:
    """MiniMax AI 分析器"""

    def __init__(self, config: dict):
        mm_cfg = config.get("minimax", {})
        self._cfg = AnalysisConfig(
            api_key=mm_cfg.get("api_key", ""),
            base_url=mm_cfg.get("base_url", "https://api.minimax.chat/v1"),
            model=mm_cfg.get("model", "MiniMax-Text-01"),
            max_tokens=mm_cfg.get("max_tokens", 4096),
        )

    def _build_prompt(self, products: list, today_str: str) -> str:
        """構建分析提示詞"""

        # 按品牌分組
        by_brand: dict[str, list] = {}
        for p in products:
            brand = p.get("brand") or "Unknown"
            if brand not in by_brand:
                by_brand[brand] = []
            by_brand[brand].append(p)

        # 格式化數據摘要
        lines = []
        total = 0
        for brand, items in sorted(by_brand.items(), key=lambda x: len(x[1]), reverse=True):
            lines.append(f"\n【{brand}】共 {len(items)} 個商品：")
            for item in items[:5]:  # 每品牌最多5個
                name = item.get("product_name", "")[:60]
                price = item.get("price", "N/A")
                currency = item.get("currency", "CNY")
                sales = item.get("sales_count") or "N/A"
                platform = item.get("platform", "")
                wattage = item.get("wattage") or ""
                lines.append(
                    f"  - {name} | "
                    f"價格:{price}{currency} | "
                    f"銷量:{sales} | "
                    f"來源:{platform} | "
                    f"瓦數:{wattage}"
                )
            total += len(items)

        data_block = "\n".join(lines)

        prompt = f"""
你是電源供應器（PSU）市場分析師，請根據以下今日（{today_str}）
京東、京東國際、天貓、Amazon 的實際銷售數據，撰寫一份專業市場分析報告。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【數據概況】
總計收集商品：{total} 個
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【各品牌商品清單】
{data_block}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

請分析並回覆以下維度：

1. **價格區間分析**：各品牌主流價格帶（低/中/高端）
2. **競爭態勢**：各品牌在京東、天貓、Amazon 的佈局差異
3. **瓦數趨勢**：主流瓦數段（550W/650W/750W/850W/1000W+）的價格與供需
4. **性價比觀察**：各品牌性價比最高的型號推薦
5. **市場洞察**：你觀察到的任何趨勢或異常（如折扣、缺貨、新品）
6. **行銷建議**：針對每個品牌的具體策略建議（1-2句）

請用繁體中文回覆，語氣專業，適合管理層閱讀。
報告請包含明確的數據引用。
"""
        return prompt.strip()

    def analyze(self, products: list[dict]) -> str:
        """
        對收集的產品數據進行 AI 分析
        products: List[dict]，每個 dict 為一個商品（由 ProductInfo 轉來）
        """
        if not products:
            return "⚠️ 今日無收集到任何商品數據，分析報告無法生成。"

        today_str = date.today().isoformat()
        prompt = self._build_prompt(products, today_str)

        # 檢查 API Key
        if not self._cfg.api_key or self._cfg.api_key == "YOUR_MINIMAX_API_KEY_HERE":
            logger.warning("MiniMax API Key 未設定，回退為本地統計分析")
            return self._local_fallback(products, today_str)

        try:
            return self._call_minimax(prompt)
        except Exception as e:
            logger.error(f"MiniMax API 呼叫失敗: {e}，使用本地統計分析")
            return self._local_fallback(products, today_str)

    def _call_minimax(self, prompt: str) -> str:
        """呼叫 MiniMax API"""
        url = f"{self._cfg.base_url}/text/chatcompletion_v2"

        headers = {
            "Authorization": f"Bearer {self._cfg.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._cfg.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self._cfg.max_tokens,
            "temperature": self._cfg.temperature,
        }

        with httpx.Client(timeout=60) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        # MiniMax 回應格式（與 OpenAI 相似）
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return "⚠️ AI 分析服務暫時無法回覆，請稍後重試。"

    def _local_fallback(self, products: list[dict], today_str: str) -> str:
        """本地統計分析（當 API 不可用時）"""

        # 按品牌統計
        by_brand: dict[str, dict] = {}
        for p in products:
            brand = p.get("brand") or "Unknown"
            if brand not in by_brand:
                by_brand[brand] = {"count": 0, "prices": [], "platforms": set(), "wattages": []}
            by_brand[brand]["count"] += 1
            price = p.get("price")
            if price:
                try:
                    by_brand[brand]["prices"].append(float(str(price).replace(",", "")))
                except ValueError:
                    pass
            by_brand[brand]["platforms"].add(p.get("platform", ""))
            if p.get("wattage"):
                by_brand[brand]["wattages"].append(p.get("wattage"))

        lines = [f"# PSU 市場每日快報 — {today_str}\n"]
        lines.append(f"_（說明：尚未設定 MiniMax API Key，以下為本地統計分析）_\n")

        # 品牌概況
        lines.append("## 📊 各品牌覆蓋概況\n")
        lines.append("| 品牌 | 商品數 | 平均價格 | 價格區間 | 來源平台 |")
        lines.append("|------|--------|----------|----------|----------|")

        for brand, info in sorted(by_brand.items(), key=lambda x: x[1]["count"], reverse=True):
            prices = info["prices"]
            avg_p = sum(prices) / len(prices) if prices else 0
            min_p = min(prices) if prices else 0
            max_p = max(prices) if prices else 0
            platforms = " / ".join(sorted(info["platforms"]))
            lines.append(
                f"| {brand} | {info['count']} | "
                f"¥{avg_p:.0f} | ¥{min_p:.0f}~¥{max_p:.0f} | {platforms} |"
            )

        # 瓦數分布
        all_wattages: dict[str, int] = {}
        for brand, info in by_brand.items():
            for w in info["wattages"]:
                all_wattages[w] = all_wattages.get(w, 0) + 1

        if all_wattages:
            lines.append("\n## ⚡ 熱門瓦數分布\n")
            for w, cnt in sorted(all_wattages.items(), key=lambda x: x[1], reverse=True)[:8]:
                lines.append(f"- **{w}**：{cnt} 個商品")

        lines.append(f"\n---\n_報告生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
        return "\n".join(lines)
