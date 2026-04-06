"""
AI Analyzer for IT Hardware Daily Report
Uses MiniMax API with local statistical fallback
"""

import os
import sys
import json
import re
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


@dataclass
class AnalysisResult:
    """Structured analysis result"""
    summary: str
    market_trends: List[str]
    price_analysis: str
    brand_rankings: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]
    recommendations: List[str]
    key_insights: List[str]


class MiniMaxAnalyzer:
    """MiniMax AI analyzer with local fallback"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.api_key = os.getenv("MINIMAX_API_KEY", "")
        self.group_id = os.getenv("MINIMAX_GROUP_ID", "")
        self.model = self.config.get("ai_analysis", {}).get("model", "MiniMax-ablo/MiniMax-Text-01")
        self.temperature = self.config.get("ai_analysis", {}).get("temperature", 0.3)
        self.max_tokens = self.config.get("ai_analysis", {}).get("max_tokens", 2000)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and os.path.exists(config_path):
            with open(config_path, encoding='utf-8') as f:
                return json.load(f)
        base = os.path.dirname(os.path.dirname(__file__))
        cfg = os.path.join(base, 'config', 'settings.json')
        if os.path.exists(cfg):
            with open(cfg, encoding='utf-8') as f:
                return json.load(f)
        return {}

    def analyze(self, products: List[Dict]) -> AnalysisResult:
        """Main analysis entry point"""
        if not products:
            return self._empty_result()

        # Try MiniMax API first
        if self.api_key and self.group_id and HAS_HTTPX:
            try:
                return self._call_minimax(products)
            except Exception as e:
                print(f"[MiniMax] API call failed: {e}, using local fallback")

        # Fallback to local analysis
        return self._local_analysis(products)

    def _call_minimax(self, products: List[Dict]) -> AnalysisResult:
        """Call MiniMax API for analysis"""
        prompt = self._build_prompt(products)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"https://api.minimax.chat/v1/chatcompletion_v2?GroupId={self.group_id}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return self._parse_response(content, products)

    def _build_prompt(self, products: List[Dict]) -> str:
        """Build analysis prompt from product data"""
        today = datetime.now().strftime('%Y-%m-%d')

        # Summarize products by brand
        brand_summary = {}
        for p in products:
            brand = p.get('brand', 'Unknown')
            if brand not in brand_summary:
                brand_summary[brand] = []
            brand_summary[brand].append(p)

        # Build summary text
        summary_parts = []
        for brand, items in brand_summary.items():
            prices = [p.get('price', 0) for p in items if p.get('price')]
            avg_price = sum(prices) / len(prices) if prices else 0
            ratings = [p.get('rating') for p in items if p.get('rating')]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            summary_parts.append(
                f"- {brand}: {len(items)} products, avg price ${avg_price:.2f}, avg rating {avg_rating:.1f}★"
            )

        products_text = "\n".join(summary_parts[:15])

        prompt = f"""你是IT硬體市場分析師。请分析以下電源供應器(PSU)市場數據，生成簡潔的每日報告。

日期: {today}
平台: 京東、天貓、Amazon、Newegg

品牌數據摘要:
{products_text}

請以JSON格式輸出分析結果，包含以下字段（全部用中文）:
{{
  "summary": "市場概覽摘要（1-2句話）",
  "market_trends": ["趨勢1", "趨勢2", "趨勢3"],
  "price_analysis": "價格區間分析",
  "brand_rankings": [{{"brand": "品牌名", "score": 評分, "reason": "原因"}}],
  "top_products": [{{"brand": "品牌", "model": "型號", "price": 價格, "rating": 評分, "reason": "推薦理由"}}],
  "recommendations": ["建議1", "建議2", "建議3"],
  "key_insights": ["洞察1", "洞察2", "洞察3"]
}}

只輸出JSON，不要其他文字。"""
        return prompt

    def _parse_response(self, content: str, products: List[Dict]) -> AnalysisResult:
        """Parse MiniMax JSON response"""
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return AnalysisResult(
                    summary=data.get('summary', ''),
                    market_trends=data.get('market_trends', []),
                    price_analysis=data.get('price_analysis', ''),
                    brand_rankings=data.get('brand_rankings', []),
                    top_products=data.get('top_products', []),
                    recommendations=data.get('recommendations', []),
                    key_insights=data.get('key_insights', [])
                )
            except json.JSONDecodeError:
                pass

        # Fallback on parse error
        return self._local_analysis(products)

    def _local_analysis(self, products: List[Dict]) -> AnalysisResult:
        """Local statistical analysis fallback"""
        today = datetime.now().strftime('%Y-%m-%d')

        # Brand aggregation
        brand_data = {}
        for p in products:
            brand = p.get('brand', 'Unknown')
            if brand not in brand_data:
                brand_data[brand] = {'count': 0, 'prices': [], 'ratings': [], 'reviews': []}
            brand_data[brand]['count'] += 1
            if p.get('price'):
                brand_data[brand]['prices'].append(float(p['price']))
            if p.get('rating'):
                brand_data[brand]['ratings'].append(float(p['rating']))
            if p.get('reviews'):
                brand_data[brand]['reviews'].append(int(p['reviews']))

        # Calculate brand scores
        brand_rankings = []
        for brand, data in brand_data.items():
            avg_price = sum(data['prices']) / len(data['prices']) if data['prices'] else 0
            avg_rating = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else 0
            total_reviews = sum(data['reviews']) if data['reviews'] else 0
            score = round(avg_rating * 10 + min(data['count'] / 10, 5), 1)
            brand_rankings.append({
                'brand': brand,
                'score': score,
                'avg_price': round(avg_price, 2),
                'avg_rating': round(avg_rating, 1),
                'total_reviews': total_reviews,
                'reason': self._get_brand_reason(brand, avg_rating, avg_price, data['count'])
            })

        brand_rankings.sort(key=lambda x: x['score'], reverse=True)

        # Top products by rating
        sorted_products = sorted(
            [p for p in products if p.get('rating')],
            key=lambda x: (x.get('rating', 0), x.get('reviews', 0)),
            reverse=True
        )

        top_products = []
        for p in sorted_products[:5]:
            top_products.append({
                'brand': p.get('brand', 'Unknown'),
                'model': p.get('model', 'Unknown'),
                'price': p.get('price', 0),
                'currency': p.get('currency', 'USD'),
                'rating': p.get('rating', 0),
                'reviews': p.get('reviews', 0),
                'platform': p.get('platform', 'Unknown'),
                'reason': self._get_product_reason(p)
            })

        # Price analysis
        prices = [p['price'] for p in products if p.get('price')]
        if prices:
            min_p, max_p = min(prices), max(prices)
            avg_p = sum(prices) / len(prices)
            price_analysis = (
                f"市場價格區間 ${min_p:.0f} - ${max_p:.0f}，"
                f"平均價格 ${avg_p:.0f}。"
                f"${avg_p*0.6:.0f}以下為入門級，"
                f"${avg_p*0.6:.0f}-${avg_p*1.5:.0f}為主流級，"
                f"${avg_p*1.5:.0f}以上為高端級。"
            )
        else:
            price_analysis = "價格數據不足"

        # Generate recommendations
        recommendations = []
        if brand_rankings:
            top_brand = brand_rankings[0]['brand']
            recommendations.append(f"重點關注{top_brand}品牌，其市場表現最強")

        recommendations.append("維持庫存在主流瓦數區間（750W-850W）")
        recommendations.append("加強線上電商管道運營")

        # Market trends
        trends = [
            "ATX 3.0/3.1電源接口成為新品標配",
            "850W-1000W瓦數段需求持續增長",
            "原生16-pin原生線供電需求增加"
        ]

        # Key insights
        insights = []
        if brand_rankings:
            insights.append(f"共監測到{len(brand_data)}個品牌，{len(products)}款產品")
            insights.append(f"平均產品評分 {sum(b['avg_rating'] for b in brand_rankings)/len(brand_rankings):.1f}★")

        return AnalysisResult(
            summary=f"今日監測到{len(products)}款產品，覆蓋{len(brand_data)}個品牌。{brand_rankings[0]['brand'] if brand_rankings else 'N/A'}表現最強。",
            market_trends=trends,
            price_analysis=price_analysis,
            brand_rankings=brand_rankings[:8],
            top_products=top_products,
            recommendations=recommendations,
            key_insights=insights
        )

    def _get_brand_reason(self, brand: str, avg_rating: float, avg_price: float, count: int) -> str:
        reasons = {
            "ASUS": "ROG Thor系列樹立高端品牌形象，性價比與品質兼顧",
            "MSI": "MAG系列入門級市場表現出色，性價比突出",
            "Corsair": "RMx系列市場標杆，高端市場領導者",
            "Seasonic": "電源大廠，Prime系列品質卓越",
            "Gigabyte": "AORUS系列專業玩家定位，全模組化設計受歡迎",
        }
        base = reasons.get(brand, f"擁有{count}款產品，評分{avg_rating:.1f}★")
        if avg_price > 200:
            return f"{base}，定位高端市場"
        elif avg_price < 100:
            return f"{base}，主打性價比"
        return base

    def _get_product_reason(self, p: Dict) -> str:
        rating = p.get('rating', 0)
        reviews = p.get('reviews', 0)
        price = p.get('price', 0)

        if rating >= 4.8 and reviews >= 500:
            return "高分高銷量，市場認可度最高"
        elif rating >= 4.7:
            return "評分優秀，品質可靠"
        elif price < 100:
            return "高性價比入門首選"
        elif rating >= 4.5:
            return "綜合表現均衡，值得推薦"
        return "同價位段有不錯的表現"

    def _empty_result(self) -> AnalysisResult:
        return AnalysisResult(
            summary="今日無數據",
            market_trends=[],
            price_analysis="",
            brand_rankings=[],
            top_products=[],
            recommendations=[],
            key_insights=["請檢查爬蟲模組是否正常運行"]
        )

    def get_analysis_dict(self, products: List[Dict]) -> Dict:
        """Get analysis as dictionary for report generation"""
        result = self.analyze(products)
        return asdict(result)


def main():
    """Test the analyzer with mock data"""
    mock_products = [
        {"brand": "ASUS", "model": "ROG Thor 850P", "price": 189.99, "rating": 4.7, "reviews": 890, "platform": "Amazon", "currency": "USD"},
        {"brand": "MSI", "model": "MEG Ai1300P", "price": 319.99, "rating": 4.9, "reviews": 680, "platform": "Newegg", "currency": "USD"},
        {"brand": "MSI", "model": "MAG A750BN", "price": 89.99, "rating": 4.5, "reviews": 1100, "platform": "JD", "currency": "CNY"},
        {"brand": "Corsair", "model": "RM850x", "price": 139.99, "rating": 4.8, "reviews": 2100, "platform": "Amazon", "currency": "USD"},
        {"brand": "Gigabyte", "model": "AORUS 850W", "price": 159.99, "rating": 4.7, "reviews": 620, "platform": "Tmall", "currency": "CNY"},
        {"brand": "Seasonic", "model": "Focus GX-750", "price": 129.99, "rating": 4.7, "reviews": 890, "platform": "Amazon", "currency": "USD"},
    ]

    analyzer = MiniMaxAnalyzer()
    result = analyzer.analyze(mock_products)

    print("=" * 60)
    print(f"Summary: {result.summary}")
    print(f"\nBrand Rankings:")
    for b in result.brand_rankings:
        print(f"  {b['brand']}: score={b['score']}, reason={b['reason']}")
    print(f"\nTop Products:")
    for p in result.top_products:
        print(f"  {p['brand']} {p['model']} - ${p['price']} ({p['rating']}★)")
    print(f"\nRecommendations:")
    for r in result.recommendations:
        print(f"  - {r}")


if __name__ == '__main__':
    main()
