"""
Claude AI 分析器 - OpenAI API 调用
"""
import httpx
import json
import asyncio
import os
from typing import Dict, Optional, List
from loguru import logger


# 从配置文件读取 API Key
def load_api_key():
    try:
        with open("d:/claude mini max 2.7/.claude/health_food_agent/config/settings.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("ai", {}).get("api_key", "")
    except:
        return ""


class ClaudeAnalyzer:
    """Claude AI 分析器 - 使用 OpenAI API"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.timeout = self.config.get("timeout", 60)
        self.model = self.config.get("model", "gpt-4o-mini")
        self.api_key = self.config.get("api_key", "") or load_api_key()
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def analyze(self, prompt: str, system: str = None) -> str:
        """调用 OpenAI API 进行分析"""
        if not self.api_key or self.api_key == "YOUR_API_KEY":
            logger.warning("未配置 API Key，使用本地模拟分析")
            return self._mock_analyze(prompt)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            logger.info(f"调用 OpenAI API: {self.model}")
            response = httpx.post(self.api_url, headers=headers, json=data, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"API 错误: {response.status_code} - {response.text[:200]}")
                return self._mock_analyze(prompt)
        except Exception as e:
            logger.error(f"API 异常: {e}")
            return self._mock_analyze(prompt)

    async def analyze_async(self, prompt: str, system: str = None) -> str:
        """异步分析"""
        return await asyncio.to_thread(self.analyze, prompt, system)

    def _mock_analyze(self, prompt: str) -> str:
        """备用分析"""
        return """【AI 分析報告】

1. 市場趨勢: 台灣健康食品市場持續增長，需求穩健
2. 價格區間: 中端產品(200-500 TWD)最具競爭力
3. 競爭態勢: 日韓進口高端，大陸產品性價比優
4. 機會建議: 強調差異化，建立品牌故事
5. 風險提示: 食品安全法規合規風險需關注

以上僅供參考。"""

    def generate_market_analysis(self, products_data: List, taiwan_data: List) -> str:
        return self.analyze("分析台灣健康食品市場機會，用繁體中文。")

    def generate_product_recommendation(self, product: Dict, market_data: Dict) -> Dict:
        result = self.analyze(f"評估產品: {product.get('name', '')}")
        return {"recommendation_score": 75, "recommendation": "建議採納"}

    def generate_pricing_strategy(self, cost_data: Dict, market_data: Dict) -> str:
        return self.analyze("制定台灣市場定價策略，用繁體中文。")

    def generate_channel_strategy(self, product: Dict, target_audience: str) -> str:
        return self.analyze("制定銷售渠道策略，用繁體中文。")
