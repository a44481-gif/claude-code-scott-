"""
AI Analyzer - MiniMax API integration with sklearn/NLTK fallback.
Merges patterns from msi_psu_automation (sklearn/NLTK) + health_food_agent (MiniMax API).
"""
import httpx
import json
import asyncio
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from loguru import logger

# Optional ML/NLP dependencies
try:
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
    try:
        nltk.download("vader_lexicon", quiet=True)
    except Exception:
        pass
except ImportError:
    NLTK_AVAILABLE = False


@dataclass
class AnalyzerConfig:
    """Analyzer configuration"""
    api_endpoint: str = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    model: str = "abab6.5s-chat"
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "AnalyzerConfig":
        return cls(
            api_endpoint=config.get("api_endpoint", cls.api_endpoint),
            model=config.get("model", cls.model),
            api_key=config.get("api_key", ""),
            temperature=config.get("temperature", cls.temperature),
            max_tokens=config.get("max_tokens", cls.max_tokens),
        )


class MiniMaxAnalyzer:
    """
    AI Analyzer with MiniMax API + local statistical/sentiment fallback.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = AnalyzerConfig.from_dict(config or {})
        self._sia = None
        if NLTK_AVAILABLE:
            try:
                self._sia = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.warning(f"NLTK SentimentIntensityAnalyzer 初始化失败: {e}")

    # ── MiniMax API ─────────────────────────────────────────────

    def analyze(self, prompt: str, system: Optional[str] = None) -> str:
        """同步调用 AI 分析。"""
        if not self.config.api_key or self.config.api_key in ("", "YOUR_MINIMAX_API_KEY"):
            logger.warning("MiniMax API Key 未配置，使用本地统计 fallback")
            return self._local_fallback(prompt)

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        try:
            response = httpx.post(self.config.api_endpoint, headers=headers, json=payload, timeout=120)
            data = response.json()

            if "base_resp" in data:
                status_code = data["base_resp"].get("status_code", 0)
                if status_code != 0:
                    error_msg = data["base_resp"].get("status_msg", "未知错误")
                    logger.error(f"MiniMax API 错误: {status_code} - {error_msg}")
                    return self._local_fallback(prompt)

            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            elif "text" in data:
                return data["text"]
            else:
                logger.error(f"无法解析响应: {data}")
                return self._local_fallback(prompt)

        except Exception as e:
            logger.error(f"AI 分析异常: {e}")
            return self._local_fallback(prompt)

    async def analyze_async(self, prompt: str, system: Optional[str] = None) -> str:
        """异步调用 AI 分析。"""
        return await asyncio.to_thread(self.analyze, prompt, system)

    # ── Local Fallback ─────────────────────────────────────────

    def _local_fallback(self, prompt: str) -> str:
        """本地统计/情感分析 fallback（无 API Key 时）。"""
        return (
            f"【本地分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}】\n\n"
            "⚠️ MiniMax API Key 未配置，使用本地统计分析。\n\n"
            f"分析请求: {prompt[:200]}...\n\n"
            "建议: 请在 config/settings.json 中配置 api_key 以获得 AI 增强分析。"
        )

    def _local_analyze(self, data: List[Dict]) -> str:
        """基于本地统计的分析（无 API 时）。"""
        if not PANDAS_AVAILABLE:
            return "pandas 未安装，无法进行统计分析。"

        df = pd.DataFrame(data) if data else pd.DataFrame()
        if df.empty:
            return "没有可用数据进行分析。"

        report = f"【本地统计分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}】\n\n"

        # Price analysis
        if "price" in df.columns:
            prices = pd.to_numeric(df["price"], errors="coerce").dropna()
            if not prices.empty:
                report += f"📊 價格統計:\n"
                report += f"  平均價格: ¥{prices.mean():.2f}\n"
                report += f"  價格區間: ¥{prices.min():.2f} - ¥{prices.max():.2f}\n"
                report += f"  中位數: ¥{prices.median():.2f}\n\n"

        # Brand analysis
        if "brand" in df.columns:
            brand_counts = df["brand"].value_counts()
            report += f"🏷️ 品牌分佈:\n"
            for brand, count in brand_counts.head(5).items():
                report += f"  {brand}: {count} 款\n"
            report += "\n"

        # Source analysis
        if "source" in df.columns:
            source_counts = df["source"].value_counts()
            report += f"🛒 來源分佈:\n"
            for source, count in source_counts.items():
                report += f"  {source}: {count} 款\n"
            report += "\n"

        return report

    # ── Sentiment Analysis ─────────────────────────────────────

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析文本情感。"""
        if self._sia:
            scores = self._sia.polarity_scores(text)
            compound = scores["compound"]
            if compound >= 0.05:
                sentiment = "positive"
            elif compound <= -0.05:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            return {"sentiment": sentiment, "scores": scores, "compound": compound}
        return {"sentiment": "unknown", "scores": {}, "compound": 0.0}

    # ── Trend Forecasting ──────────────────────────────────────

    def forecast_trend(self, series: List[float], periods: int = 7) -> Dict[str, Any]:
        """简单线性回归趋势预测。"""
        if not PANDAS_AVAILABLE or len(series) < 3:
            return {"trend": "unknown", "forecast": [], "confidence": 0}

        try:
            X = np.arange(len(series)).reshape(-1, 1)
            y = np.array(series)
            model = LinearRegression()
            model.fit(X, y)

            X_future = np.arange(len(series), len(series) + periods).reshape(-1, 1)
            y_pred = model.predict(X_future)

            slope = model.coef_[0]
            trend = "up" if slope > 0.05 else "down" if slope < -0.05 else "stable"

            return {
                "trend": trend,
                "forecast": [round(v, 2) for v in y_pred.tolist()],
                "slope": round(slope, 4),
                "confidence": round(model.score(X, y), 3),
            }
        except Exception as e:
            logger.error(f"趋势预测失败: {e}")
            return {"trend": "unknown", "forecast": [], "confidence": 0}

    # ── Market Analysis ────────────────────────────────────────

    def generate_market_analysis(self, products: List[Dict], news: List[Dict]) -> str:
        """生成市场分析报告。"""
        prompt = f"""作为 IT/PC 行业市场分析专家，请分析以下数据并给出建议：

## 产品数据 ({len(products)} 条)
样例产品:
{json.dumps(products[:3], ensure_ascii=False, indent=2)}

## 新闻数据 ({len(news)} 条)
样例新闻:
{json.dumps(news[:3], ensure_ascii=False, indent=2)}

请从以下维度进行分析:
1. 市场需求分析
2. 价格竞争力评估
3. 产品差异化机会
4. 目标客户群体
5. 风险与建议

请用中文输出结构化分析报告。"""

        system = """你是一位专业的 IT/PC 行业市场分析师，擅长 DIY 硬件、AI PC、存储市场分析。回答要专业、具体、数据驱动。"""
        return self.analyze(prompt, system)

    def summarize_news(self, articles: List[Dict]) -> str:
        """AI 新闻摘要。"""
        if not articles:
            return "暂无新闻数据。"
        prompt = f"请为以下 {len(articles)} 条新闻生成一份简洁的每日摘要，每条新闻一行，包含标题和一句话总结：\n\n"
        for i, article in enumerate(articles[:10], 1):
            prompt += f"{i}. {article.get('title', 'N/A')}\n  来源: {article.get('source', 'N/A')}\n  摘要: {article.get('summary', article.get('snippet', ''))[:100]}\n\n"
        return self.analyze(prompt)

    def generate_insights(self, data: Dict) -> str:
        """从结构化数据生成洞察。"""
        prompt = f"""请从以下数据中提取关键洞察和行动建议：

{json.dumps(data, ensure_ascii=False, indent=2)}

请输出:
1. 3-5 个关键洞察
2. 2-3 个优先行动建议
3. 1 个风险提示

用中文回答，简洁明了。"""
        return self.analyze(prompt)
